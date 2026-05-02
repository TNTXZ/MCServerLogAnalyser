# MCServerLogAnalyser

Minecraft Server Log Analyser - 一个用于分析 Minecraft 服务器日志的跨平台工具

## 功能特性

### 1. 日志导入
- 支持上传 logs 文件夹
- 支持导入 .log 文件
- 支持导入压缩包（.zip, .tar, .tar.gz, .tgz, .tar.bz2, .tbz2）
- 支持导入 .txt 文本文件

### 2. 级别筛选
- 按日志等级过滤：Info / Debug / Warning / Error

### 3. 时间筛选
- 按时间范围筛选日志条目

### 4. 内容提取
- 单独提取聊天记录
- 单独提取玩家指令

### 5. 标记功能
- 对特定日志行或事件进行标记，便于后续定位

### 6. 多端支持
- 兼容 Windows、Linux、macOS 平台

### 7. 运行时间分析
- 分析服务器的运行时长
- 分析服务器启停时段

### 8. 手动搜索
- 提供关键词搜索功能，快速定位特定内容

## 安装与运行

### 环境要求
- Python 3.8 或更高版本

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python main.py
```

## 项目结构

```
MCServerLogAnalyser/
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── LICENSE                # 许可证
├── README.md              # 本文件
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── log_entry.py       # 日志条目定义
│   ├── log_parser.py      # 日志解析器
│   ├── log_importer.py    # 日志导入器
│   ├── log_filter.py      # 日志筛选器
│   └── runtime_analyzer.py # 运行时间分析器
└── ui/                    # 用户界面
    ├── __init__.py
    └── main_window.py     # 主窗口
```

## 使用说明

1. 点击 "Import Logs" 按钮选择要导入的日志文件或文件夹
2. 使用过滤器区域筛选需要查看的日志
3. 在不同的标签页中查看分类的日志内容
4. 选中日志条目后点击 "Mark Selected" 进行标记
5. 在 "Runtime Analysis" 标签页查看服务器运行分析

## 许可证

请查看 LICENSE 文件
