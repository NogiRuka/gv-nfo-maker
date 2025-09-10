"""GV-NFO-Maker 主程序入口。

GV-NFO-Maker是一个支持多网站的NFO文件生成器，专门用于生成符合Emby标准的NFO文件。
主要面向Emby媒体服务器，同时兼容Kodi和Plex。
"""

import sys
import argparse
from typing import Optional

from .core.exceptions import NFOGeneratorError, ConfigurationError
from .config.config_manager import ConfigManager
from .generators.ck_download_generator import CkDownloadNfoGenerator
from .generators.trance_generator import TranceMusicNfoGenerator
from .utils.generator_factory import GeneratorFactory
from .utils.logger import setup_logging


def main():
    """主函数 - 命令行模式入口。"""
    parser = argparse.ArgumentParser(
        description="GV-NFO-Maker - 支持多网站的NFO文件生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的网站:
  - CK-Download: ck-download.com (标准电影内容)
  - Trance-Video: trance-video.com (成人视频内容)

使用示例:
  python -m src.main https://ck-download.com/product/detail/12345
  python -m src.main --site trance-video https://www.trance-video.com/product/detail/39661
  python -m src.main --mode auto https://example.com/movie
  python -m src.main --config custom_config.json https://example.com/movie
        """
    )
    
    parser.add_argument(
        "url",
        help="视频或电影的URL地址"
    )
    
    parser.add_argument(
        "-s", "--site",
        help="指定网站类型 (不指定则自动检测)",
        choices=["ck-download", "trance-video", "auto"],
        default="auto"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="配置文件路径",
        default="config.json"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出文件名 (默认使用视频标题)"
    )
    
    parser.add_argument(
        "--no-manual",
        action="store_true",
        help="跳过手动输入修正步骤"
    )
    
    parser.add_argument(
        "-m", "--mode",
        help="运行模式 (auto:自动/manual:手动/interactive:交互)",
        choices=["auto", "manual", "interactive"],
        default="interactive"
    )
    
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="创建默认配置文件"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="GV-NFO-Maker 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager(args.config)
        
        # 如果请求创建默认配置文件
        if args.create_config:
            config_manager.create_default_config_file()
            return 0
        
        # 验证配置
        config_manager.validate_config()
        
        # 创建生成器工厂
        factory = GeneratorFactory(config_manager)
        
        # 获取合适的生成器
        if args.site == "auto":
            generator = factory.create_generator_from_url(args.url)
            if not generator:
                print("❌ 无法识别URL对应的网站，请使用 --site 参数指定")
                print("支持的网站: ck-download, trance-video")
                return 1
        else:
            generator = factory.create_generator(args.site)
        
        # 根据参数覆盖设置
        if args.no_manual:
            generator.config["manual_input"] = False
            generator.run_mode = "auto"
        
        if args.mode:
            generator.run_mode = args.mode
            generator.config["run_mode"] = args.mode
        
        # 生成NFO文件
        print(f"🎬 使用 {generator.site_name} 生成器")
        nfo_file = generator.run(args.url)
        
        if nfo_file:
            # 如果指定了输出文件名则重命名
            if args.output:
                import os
                if os.path.exists(nfo_file):
                    os.rename(nfo_file, args.output)
                    print(f"📁 文件已重命名为: {args.output}")
            
            print("\n🎉 NFO文件生成成功！")
            return 0
        else:
            print("\n❌ NFO文件生成失败")
            return 1
    
    except ConfigurationError as e:
        print(f"❌ 配置错误: {e}")
        return 1
    
    except NFOGeneratorError as e:
        print(f"❌ 生成器错误: {e}")
        return 1
    
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        return 1
    
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def interactive_mode():
    """交互模式 - 用于NFO文件生成的交互式界面。"""
    print("🎬 GV-NFO-Maker - 交互模式")
    print("=" * 40)
    
    try:
        # 初始化配置
        config_manager = ConfigManager()
        factory = GeneratorFactory(config_manager)
        
        while True:
            print("\n支持的网站:")
            sites = config_manager.get_supported_sites()
            for i, site in enumerate(sites, 1):
                site_config = config_manager.get_site_config(site)
                print(f"  {i}. {site_config['name']} ({site})")
            
            print("\n请选择操作:")
            print("  1. 输入URL自动识别")
            print("  2. 手动选择网站")
            print("  3. 设置运行模式")
            print("  4. 查看配置")
            print("  5. 退出")
            
            choice = input("\n请输入选择 (1-5): ").strip()
            
            if choice == "1":
                url = input("请输入URL: ").strip()
                if url:
                    generator = factory.create_generator_from_url(url)
                    if generator:
                        generator.run(url)
                    else:
                        print("❌ 无法识别URL对应的网站")
            
            elif choice == "2":
                print("\n选择网站:")
                for i, site in enumerate(sites, 1):
                    site_config = config_manager.get_site_config(site)
                    print(f"  {i}. {site_config['name']}")
                
                try:
                    site_choice = int(input("请输入网站编号: ").strip()) - 1
                    if 0 <= site_choice < len(sites):
                        site = sites[site_choice]
                        url = input("请输入URL: ").strip()
                        if url:
                            generator = factory.create_generator(site)
                            generator.run(url)
                    else:
                        print("❌ 无效的选择")
                except ValueError:
                    print("❌ 请输入有效的数字")
            
            elif choice == "3":
                print("\n当前运行模式设置:")
                current_mode = config_manager.get('run_mode', 'interactive')
                print(f"  当前模式: {current_mode}")
                print("\n可选模式:")
                print("  1. auto - 自动模式 (无人工干预)")
                print("  2. manual - 手动模式 (需要人工修正)")
                print("  3. interactive - 交互模式 (可选择是否修正)")
                
                mode_choice = input("\n请选择运行模式 (1-3): ").strip()
                mode_map = {'1': 'auto', '2': 'manual', '3': 'interactive'}
                if mode_choice in mode_map:
                    new_mode = mode_map[mode_choice]
                    config_manager.set('run_mode', new_mode)
                    print(f"✅ 运行模式已设置为: {new_mode}")
                else:
                    print("❌ 无效的选择")
            
            elif choice == "4":
                print("\n当前配置:")
                print(f"  配置文件: {config_manager.config_file}")
                print(f"  运行模式: {config_manager.get('run_mode', 'interactive')}")
                print(f"  超时时间: {config_manager.get('timeout')}秒")
                print(f"  支持网站: {', '.join(sites)}")
            
            elif choice == "5":
                print("👋 再见！")
                break
            
            else:
                print("❌ 无效的选择，请重新输入")
    
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 无参数时启动交互模式
        interactive_mode()
    else:
        # 命令行模式
        sys.exit(main())