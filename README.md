# HTTPXX - URL请求工具

一个简单的Python工具，用于读取txt文件中的URL列表，对每个URL发送HTTP请求，并获取状态码和页面标题。

## 功能特性

- 支持读取txt文件中的URL列表（每行一个URL）
- 自动处理只有域名的情况（自动添加https://协议）
- 支持HTTP和HTTPS协议
- 自动重试机制（可配置重试次数）
- 请求延迟控制（避免请求过快）
- 结果输出到控制台和CSV文件
- 支持多种编码格式的文件读取
- 错误处理和异常捕获

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法
```bash
python main.py urls.txt
```

### 带参数用法
```bash
python main.py urls.txt -o results.csv -t 15 -r 5 -d 2
```

### 参数说明
- `urls.txt`: 包含URL列表的文本文件路径（必需）
- `-o, --output`: 输出结果到CSV文件（可选）
- `-t, --timeout`: 请求超时时间，默认10秒
- `-r, --retries`: 重试次数，默认3次
- `-d, --delay`: 请求间隔延迟，默认1秒

## URL文件格式

URL文件应为纯文本文件，每行一个URL：

```
https://www.google.com
www.baidu.com
http://example.com
github.com
```

支持以下格式：
- 完整URL：`https://www.example.com`
- 只有域名：`example.com`（会自动添加https://）
- HTTP协议：`http://example.com`

## 输出示例

```
找到 4 个有效URL，开始处理...
--------------------------------------------------------------------------------
处理第1行: https://www.google.com
  状态码: 200
  标题: Google
--------------------------------------------------------------------------------
处理第2行: https://www.baidu.com
  状态码: 200
  标题: 百度一下，你就知道
--------------------------------------------------------------------------------
处理完成! 成功: 4/4
```

## 打包为EXE

使用PyInstaller打包为可执行文件：

```bash
pip install pyinstaller
pyinstaller --onefile --console main.py
```

或者使用提供的spec文件：

```bash
pyinstaller build.spec
```

打包后的exe文件在`dist`目录中。

## 项目结构

```
httpxx/
├── main.py              # 主程序
├── requirements.txt     # 依赖包列表
├── build.spec          # PyInstaller打包配置
├── example_urls.txt    # 示例URL文件
└── README.md           # 说明文档
```

## 注意事项

1. 请确保网络连接正常
2. 对于大量URL，建议设置适当的延迟时间
3. 某些网站可能有反爬虫机制，请合理使用
4. 输出文件为CSV格式，可用Excel打开