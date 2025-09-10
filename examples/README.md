# NFO示例文件

本目录包含GV-NFO-Maker生成的NFO文件示例，展示不同类型内容的标准格式。

## 📁 文件说明

### standard_movie.nfo
- **类型**: 标准电影内容
- **模板**: standard
- **特点**: 适用于普通电影、电视剧等内容
- **评级**: PG-13
- **字段**: 包含所有标准NFO字段

### adult_content.nfo
- **类型**: 成人视频内容
- **模板**: adult
- **特点**: 基于RML4001格式，专门用于成人内容
- **评级**: XXX
- **字段**: 包含成人内容特有字段和标签

## 🎯 使用说明

这些示例文件展示了：

1. **字段顺序**: 严格按照Emby推荐的字段顺序排列
2. **CDATA格式**: plot和outline字段使用CDATA格式
3. **必填字段**: title为唯一必填字段
4. **关联字段**: originaltitle与title相同，sorttitle包含ID等
5. **标签规则**: 第一个标签为imdbid
6. **演员信息**: type固定为"Actor"
7. **唯一ID**: imdb、tmdb、tvdb使用相同值

## 📋 字段说明

### 基本信息
- `title`: 标题
- `originaltitle`: 原始标题（与title相同）
- `plot`: 剧情简介（CDATA格式）
- `year`: 年份
- `runtime`: 时长（分钟）

### 评级信息
- `mpaa`: MPAA评级
- `customrating`: 自定义评级
- `rating`: 评分（默认空）
- `criticrating`: 影评人评分（默认空）

### 元数据
- `lockdata`: 锁定数据（固定false）
- `lockedfields`: 锁定字段（固定值）
- `dateadded`: 添加日期（生成时间）

### 媒体信息
- `fileinfo`: 文件信息
  - `streamdetails`: 流详情
    - `video`: 视频流信息
    - `audio`: 音频流信息

这些示例文件可以作为参考，了解GV-NFO-Maker生成的NFO文件格式和结构。