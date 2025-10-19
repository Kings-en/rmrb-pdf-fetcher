import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ====== 1. 设置基础参数 ======
base_url = "https://paper.people.com.cn/rmrb/pc/layout/202510/19/node_01.html"
root_url = "https://paper.people.com.cn/rmrb/"

# ====== 2. 获取页面并解析 ======
response = requests.get(base_url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "html.parser")

# 找到包含文章链接的 ul
news_list = soup.find("ul", class_="news-list")

if not news_list:
    print("未找到 news-list，请检查网页结构或 class 名称")
    exit()

# ====== 3. 提取每条新闻链接 ======
article_links = []
for a in news_list.find_all("a"):
    href = a.get("href")
    title = a.get_text(strip=True)
    if href:
        full_url = urljoin(base_url, href)
        article_links.append((title, full_url))

print(f"共找到 {len(article_links)} 篇文章")

# ====== 4. 下载并提取正文 ======
def get_article_text(url):
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    # 正文一般在 <div class="article-content"> 或 <div id="articleContent">
    content = soup.find("div", class_="article-content") or soup.find("div", id="articleContent")
    if not content:
        return ""
    # 去掉多余标签，仅保留纯文本
    return content.get_text("\n", strip=True)

# ====== 5. 合并保存 ======
with open("merged_articles.txt", "w", encoding="utf-8") as f:
    for i, (title, link) in enumerate(article_links, 1):
        print(f"正在下载 {i}/{len(article_links)}: {title}")
        text = get_article_text(link)
        f.write(f"【{title}】\n\n{text}\n\n{'='*60}\n\n")

print("✅ 所有文章已保存到 merged_articles.txt")
