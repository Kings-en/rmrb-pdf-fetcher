# rmrb-crawler 📰

> 一个自动爬取 **人民日报电子版 (https://paper.people.com.cn/rmrb/)** 当天所有版面文章的 Python 脚本。  
支持 **多线程加速下载**，并将所有文章正文合并保存为单个文本文件。

## 📁 项目结构

```
rmrb-crawler/
├── README.md
├── requirements.txt
├── rmrb_crawler.py
├── .gitignore
└── LICENSE
```


---

## ✨ 功能特性

- 自动识别当天日期（无需手动修改）
- 抓取当天全部版面（node_01、node_02、...）
- 自动解析每篇文章链接与正文内容
- 多线程加速下载，提高爬取速度
- 合并保存为 `rmrb_YYYYMMDD.txt` 文件


## [v1.4.4] - 2025-10-20
> **全面重构版本** — 从单页抓取到全自动多线程PDF生成

### ✨ 新增
- 🗓️ **自动日期检测与回退机制**
  - 支持命令行参数输入日期（格式：`YYYY-MM-DD`）
  - 若当天人民日报尚未更新，则自动回退至前一日  
- 📰 **全版面自动抓取**
  - 自动检测 `node_01.html` 至 `node_30.html` 所有版面  
  - 汇总整份人民日报内容到一份 PDF  
- ⚡ **多线程下载加速**
  - 使用 `ThreadPoolExecutor` 并发抓取文章正文  
  - 下载效率提升约 5~10 倍  
- 🧭 **智能正文提取**
  - 自动识别 `<div class="article-content">` 或 `<div id="articleContent">`
  - 自动提取作者信息（来自 `<p class="sec">`）
  - 容错与异常处理更完善  

### 🧾 PDF 输出系统（全新）
- 📘 **支持 SimSun 中文字体**
- 🧱 **右侧笔记区（默认 6 cm）**
- 🗂️ **自动生成可点击目录页**
  - 标题带跳转锚点，点击可定位正文
  - 自动分页，防止目录过长溢出  
- ✍️ **智能排版算法**
  - 段首空两格
  - 标题居中加粗（28pt），作者居中（10pt）
  - 小标题自动放大加粗
  - 自动换行避免标点出现在行首
- 🧾 **页脚页码**
  - “第 x 页” 居中显示  
- 🖋️ **黑色分割线（0.1pt）**
  - 优化视觉层次感  

### ⚙️ 可配置参数
```python
SIMSUN_PATH = r"C:\Windows\Fonts\simsun.ttc"  # 中文字体路径
RIGHT_NOTE_MM = 60   # 右侧笔记区宽度（mm）
BODY_FONT_SIZE = 12  # 正文字号
LINE_HEIGHT = 7.5    # 行高

---

## 📦 环境要求

Python 3.8 或更高版本

安装依赖：
```bash
pip install -r requirements.txt
````

---

## 🚀 使用方法

1. 克隆项目：

   ```bash
   git clone https://github.com/你的用户名/rmrb-crawler.git
   cd rmrb-crawler
   ```

2. 运行爬虫：

   ```bash
   python rmrb_crawler.py
   ```

3. 生成的文件示例：

   ```
   rmrb_20251020.txt
   ```

---

## ⚙️ 主要参数

| 参数   | 功能说明             |
| ---- | ---------------- |
| 自动日期 | 自动识别当天年月日        |
| 多线程  | 默认线程数：10，可自行修改   |
| 输出文件 | 按日期命名保存，UTF-8 编码 |

---

## 📁 输出示例

```
【向着宏伟目标接续奋进】

……正文内容……

============================================================

【飞驰的光影，映照追梦的中国】

……正文内容……
```

---

## 🔄 后续计划

* [ ] 支持指定日期范围自动爬取
* [ ] 支持 PDF / Word 导出
* [ ] 断点续爬与错误重试

---

## 🧾 LICENSE

本项目采用 [MIT License](LICENSE)

````

---

## 📄 `requirements.txt`

```text
requests>=2.31.0
beautifulsoup4>=4.12.2
````

---

## 📄 `.gitignore`

```gitignore
__pycache__/
*.pyc
*.txt
*.log
.env
```

---

## 📄 `LICENSE`（MIT）

```text
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

---

## 📄 `rmrb_crawler.py`

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

"""
rmrb-crawler
-------------
自动爬取人民日报电子版当日所有版面文章，并合并保存为一个文本文件。
"""

def get_all_sections(base_url):
    """获取当天所有版面链接"""
    index_url = base_url + "node_01.html"
    res = requests.get(index_url)
    res.encoding = "utf-8"
    if res.status_code != 200:
        raise Exception("无法访问人民日报当日页面，请检查网络或日期。")

    soup = BeautifulSoup(res.text, "html.parser")
    sections = soup.select("div.rightMenu a")

    section_links = []
    for s in sections:
        href = s.get("href")
        if href and href.startswith("node_"):
            section_links.append(urljoin(base_url, href))

    if not section_links:
        section_links = [index_url]

    print(f"📰 共发现 {len(section_links)} 个版面")
    return section_links


def get_articles_from_section(section_url):
    """获取版面中的文章链接"""
    res = requests.get(section_url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    ul = soup.find("ul", class_="news-list")
    articles = []
    if not ul:
        return articles
    for a in ul.find_all("a"):
        href = a.get("href")
        title = a.get_text(strip=True)
        if href:
            full_url = urljoin(section_url, href)
            articles.append((title, full_url))
    return articles


def get_article_text(title, url):
    """下载文章正文"""
    try:
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.find("div", class_="article-content") or soup.find("div", id="articleContent")
        if not content:
            return f"【{title}】\n（未找到正文）\n\n"
        text = content.get_text("\n", strip=True)
        return f"【{title}】\n\n{text}\n\n{'='*60}\n\n"
    except Exception as e:
        return f"【{title}】\n（下载失败：{e}）\n\n{'='*60}\n\n"


def main():
    today = datetime.now().strftime("%Y%m/%d")
    base_url = f"https://paper.people.com.cn/rmrb/pc/layout/{today}/"

    print(f"📅 当前抓取日期: {today}")

    sections = get_all_sections(base_url)
    all_articles = []
    for section_url in sections:
        articles = get_articles_from_section(section_url)
        all_articles.extend(articles)

    print(f"📄 共发现 {len(all_articles)} 篇文章")

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_article = {executor.submit(get_article_text, t, u): (t, u) for t, u in all_articles}
        for i, future in enumerate(as_completed(future_to_article), 1):
            title, _ = future_to_article[future]
            try:
                text = future.result()
                results.append(text)
                print(f"✅ [{i}/{len(all_articles)}] 完成: {title}")
            except Exception as e:
                print(f"❌ [{i}] {title} 失败: {e}")

    out_file = f"rmrb_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.writelines(results)

    print(f"\n🎉 所有文章已保存到 {out_file}")


if __name__ == "__main__":
    main()
```
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Kings-en/rmrb-pdf-fetcher&type=date&legend=top-left)](https://www.star-history.com/#Kings-en/rmrb-pdf-fetcher&type=date&legend=top-left)
