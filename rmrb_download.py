import schedule
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PyPDF2 import PdfMerger, PdfReader
import os
import logging
from datetime import datetime
import traceback
import random
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rmrb_download.log'),
        logging.StreamHandler()
    ]
)

# 用户代理列表，用于随机切换
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def setup_driver():
    """设置并返回Chrome浏览器驱动"""
    try:
        # 配置浏览器选项
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--window-size=1920,1080')
        
        # 随机选择用户代理
        user_agent = random.choice(USER_AGENTS)
        options.add_argument(f'user-agent={user_agent}')
        
        # 禁用自动化控制标志
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 自动下载和管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # 执行JavaScript隐藏自动化特征
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {},
                };
            '''
        })
        
        driver.implicitly_wait(15)  # 隐式等待15秒
        return driver
    except Exception as e:
        logging.error(f"浏览器驱动设置失败: {e}")
        logging.error(traceback.format_exc())
        raise

def get_current_date():
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")

def get_pdf_urls(driver, main_url):
    """获取所有PDF链接"""
    pdf_urls = []
    date_str = get_current_date()
    
    try:
        # 访问人民日报网站
        logging.info(f"正在访问人民日报网站: {main_url}")
        driver.get(main_url)
        
        # 等待页面基本加载完成
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        logging.info("页面基本加载完成")
        
        # 尝试获取日期元素
        try:
            date_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'date'))
            )
            date_text = date_element.text
            date_match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', date_text)
            
            if date_match:
                date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                logging.info(f"从页面获取到日期: {date_str}")
            else:
                logging.warning("日期格式不匹配，使用当前日期")
        except Exception as e:
            logging.warning(f"获取日期元素失败: {e}, 使用当前日期")
        
        # 尝试获取所有PDF链接
        try:
            # 等待版面链接出现
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#pageLink'))
            )
            
            page_links = driver.find_elements(By.CSS_SELECTOR, '#pageLink')
            
            if not page_links:
                logging.warning("未找到任何页面链接")
                return date_str, []
            
            logging.info(f"找到 {len(page_links)} 个页面链接")
            
            # 获取每个页面的PDF链接
            for i, link in enumerate(page_links):
                try:
                    page_url = link.get_attribute('href')
                    if not page_url:
                        continue
                        
                    logging.info(f"处理页面 {i+1}/{len(page_links)}: {page_url}")
                    
                    # 在新标签页中打开页面
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(page_url)
                    
                    # 等待新页面加载
                    WebDriverWait(driver, 20).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                    
                    # 尝试获取PDF链接
                    try:
                        pdf_link = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.paper-bot a'))
                        )
                        pdf_url = pdf_link.get_attribute('href')
                        if pdf_url and pdf_url.endswith('.pdf'):
                            pdf_urls.append(pdf_url)
                            logging.info(f"找到PDF链接: {pdf_url}")
                        else:
                            logging.warning(f"无效的PDF链接: {pdf_url}")
                    except Exception as e:
                        logging.warning(f"在页面 {page_url} 中找不到PDF链接: {e}")
                    
                    # 关闭当前标签页并切换回主标签页
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                except Exception as e:
                    logging.error(f"处理页面链接时出错: {e}")
                    logging.error(traceback.format_exc())
                    # 确保切换回主标签页
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
            
            return date_str, pdf_urls
            
        except Exception as e:
            logging.error(f"获取版面链接失败: {e}")
            return date_str, []
        
    except Exception as e:
        logging.error(f"访问人民日报网站失败: {e}")
        logging.error(traceback.format_exc())
        return date_str, []

def download_and_merge_pdfs(date_str, pdf_urls):
    """下载并合并PDF文件"""
    if not pdf_urls:
        logging.warning("没有可下载的PDF链接")
        return False
    
    # 创建下载目录
    download_dir = "人民日报下载"
    os.makedirs(download_dir, exist_ok=True)
    
    # 下载并合并PDF
    merger = PdfMerger()
    downloaded_files = []
    success_count = 0
    
    for i, url in enumerate(pdf_urls):
        try:
            logging.info(f"下载PDF {i+1}/{len(pdf_urls)}: {url}")
            
            # 设置请求头，模拟浏览器访问
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Referer': 'https://paper.people.com.cn/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # 增加随机延迟，避免请求过快
            time.sleep(random.uniform(1.0, 3.0))
            
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # 保存单个PDF
            filename = os.path.join(download_dir, f"人民日报-{date_str}-第{i+1}版.pdf")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 验证PDF文件是否有效
            try:
                with open(filename, 'rb') as f:
                    PdfReader(f)
                downloaded_files.append(filename)
                success_count += 1
                
                # 添加到合并器
                with open(filename, 'rb') as f:
                    merger.append(f)
                
                logging.info(f"已保存: {filename}")
            except Exception as e:
                logging.error(f"PDF文件无效: {filename}, 错误: {e}")
                os.remove(filename)
                logging.info(f"已删除无效文件: {filename}")
                
        except Exception as e:
            logging.error(f"下载PDF失败: {url}, 错误: {e}")
    
    # 保存合并的PDF
    if success_count > 0:
        merged_filename = os.path.join(download_dir, f"人民日报-{date_str}-完整版.pdf")
        with open(merged_filename, 'wb') as f:
            merger.write(f)
        
        logging.info(f"已合并并保存完整版: {merged_filename}")
        
        # 删除单个版面的PDF文件
        for file in downloaded_files:
            try:
                os.remove(file)
                logging.info(f"已删除单个文件: {file}")
            except Exception as e:
                logging.error(f"删除文件失败: {file}, 错误: {e}")
        
        return True
    else:
        logging.warning("没有成功下载任何PDF文件")
        return False

def download_rmrb_pdf():
    """下载并合并人民日报PDF"""


    driver = None
    try:
        logging.info("开始人民日报PDF下载任务")
        driver = setup_driver()
        
        # 人民日报网址
        main_url = 'https://paper.people.com.cn/rmrb/'
        
        # 获取日期和PDF链接
        date_str, pdf_urls = get_pdf_urls(driver, main_url)
        
        # 下载并合并PDF
        result = download_and_merge_pdfs(date_str, pdf_urls)
        
        if result:
            logging.info("人民日报PDF下载任务完成")
        else:
            logging.warning("人民日报PDF下载任务未完成")
        
        return result
        
    except Exception as e:
        logging.error(f"任务执行失败: {e}")
        logging.error(traceback.format_exc())
        return False
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("浏览器已关闭")
            except:
                pass

# 设置定时任务
schedule.every().day.at("08:00").do(download_rmrb_pdf)  # 每天早上8点执行

# 立即执行一次（测试用）
logging.info("开始测试运行...")
if download_rmrb_pdf():
    logging.info("测试运行成功！")
else:
    logging.warning("测试运行失败")

logging.info("人民日报自动下载程序已启动，每天8点自动执行")

# 保持程序运行
while True:
    try:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
        break
    except Exception as e:
        logging.error(f"主循环出错: {e}")
        logging.error(traceback.format_exc())
        time.sleep(300)  # 出错后等待5分钟再重试
