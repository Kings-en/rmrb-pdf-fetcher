# 人民日报自动下载器
> 这是一个用于自动获取每日人民日报完整PDF的项目，仅限自己学习使用，若有侵权联系删除。

这是一个用于自动下载并合并人民日报版面 PDF 的 Python 程序。该程序每天定时从人民日报的官方网站下载最新的 PDF 文件，并将它们合并为一个完整的 PDF 文件。

## 功能

- 自动获取人民日报最新页面。
- 下载并合并该页面中的所有 PDF 文件。
- 每天早上8点定时执行任务。
- 支持日志记录和错误处理。

## 安装

1. 克隆项目到本地：

   ```bash
   git clone https://github.com/Kings-en/rmrb-pdf-fetcher.git
   cd rmrb_download


2. 安装依赖库：

   ```bash
   pip install -r requirements.txt


3. 确保你的系统上已经安装了 `Google Chrome` 和适配的 `ChromeDriver`。

如果未安装 ChromeDriver，请使用 WebDriver Manager自动安装。

## 配置

1. 打开 main.py，检查下载目录和日志文件位置，确保它们适合你的需求。

2. 你可以根据需要修改下载时间，程序默认每天早上 8 点运行。

## 使用

1. 运行程序：

   ```bash
   python main.py

2. 程序将会开始运行并每天自动执行下载任务。
3. 查看日志文件 rmrb_download.log，可以查看每次下载任务的详细日志。
4. 启动与维护
确保项目按以下步骤启动：
克隆此 GitHub 仓库。
安装依赖库（运行 pip install -r requirements.txt）。
运行 python main.py 启动程序。
程序将每隔一分钟检查一次定时任务，并每天自动下载人民日报的 PDF 文件。

## 贡献

如果你希望为该项目贡献代码，可以创建一个 pull request，提交新的功能或修复 bug。
