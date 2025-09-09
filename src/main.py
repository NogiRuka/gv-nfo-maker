"""Main entry point for NFO Generator."""

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
    """Main function."""
    parser = argparse.ArgumentParser(
        description="NFO Generator - 支持多网站的NFO文件生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的网站:
  - CK-Download: ck-download.com
  - Trance Music: 各种trance音乐网站

示例:
  python -m src.main https://ck-download.com/product/detail/12345
  python -m src.main --site trance-music https://trance-music.com/track/67890
  python -m src.main --config custom_config.json https://example.com/movie
        """
    )
    
    parser.add_argument(
        "url",
        help="影片或音乐的URL地址"
    )
    
    parser.add_argument(
        "-s", "--site",
        help="指定网站类型 (auto-detect if not specified)",
        choices=["ck-download", "trance-music", "auto"],
        default="auto"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="配置文件路径",
        default="config.json"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出文件名 (默认使用影片标题)"
    )
    
    parser.add_argument(
        "--no-manual",
        action="store_true",
        help="跳过手动输入修正步骤"
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
        version="NFO Generator 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(args.config)
        
        # Create default config if requested
        if args.create_config:
            config_manager.create_default_config_file()
            return 0
        
        # Validate configuration
        config_manager.validate_config()
        
        # Create generator factory
        factory = GeneratorFactory(config_manager)
        
        # Get appropriate generator
        if args.site == "auto":
            generator = factory.create_generator_from_url(args.url)
            if not generator:
                print("❌ 无法识别URL对应的网站，请使用 --site 参数指定")
                print("支持的网站: ck-download, trance-music")
                return 1
        else:
            generator = factory.create_generator(args.site)
        
        # Override manual input setting if specified
        if args.no_manual:
            generator.config["manual_input"] = False
        
        # Generate NFO file
        print(f"🎬 使用 {generator.site_name} 生成器")
        nfo_file = generator.run(args.url)
        
        if nfo_file:
            # Rename output file if specified
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
    """Interactive mode for NFO generation."""
    print("🎬 NFO Generator - 交互模式")
    print("=" * 40)
    
    try:
        # Initialize configuration
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
            print("  3. 查看配置")
            print("  4. 退出")
            
            choice = input("\n请输入选择 (1-4): ").strip()
            
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
                print("\n当前配置:")
                print(f"  配置文件: {config_manager.config_file}")
                print(f"  超时时间: {config_manager.get('timeout')}秒")
                print(f"  支持网站: {', '.join(sites)}")
            
            elif choice == "4":
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
        # No arguments, start interactive mode
        interactive_mode()
    else:
        # Command line mode
        sys.exit(main())