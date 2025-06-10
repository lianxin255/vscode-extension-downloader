'''
FilePath: download_vsix.py
Author: lianxin
Date: 2025-06-05 16:15:20
LastEditors: lianxin
LastEditTime: 2025-06-09 14:09:59
Copyright (c) 2025 by lianxin, email: wsl1933467270@gamil.com, All Rights Reserved.
Descripttion: 批量下载VS Code扩展的VSIX文件
'''
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download_vsix.log"),
        logging.StreamHandler()
    ]
)

def read_extensions(file_path):
    """从文本文件读取扩展列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        # 读取所有行，去除空行和注释，并去除首尾空白
        return [line.strip() for line in f.readlines() 
                if line.strip() and not line.startswith('//')]

def get_chrome_options(output_dir=None, extension_id=None):
    """获取Chrome配置选项"""
    # 为会话创建一个唯一的标识符，以确保每个Chrome实例都是独立的
    if extension_id:
        # 清理扩展ID，使其适用于目录名
        sanitized_ext_id = "".join(c for c in extension_id if c.isalnum() or c in ('.', '-', '_')).rstrip()
        session_id = f'session_{sanitized_ext_id}_{int(time.time() * 1000)}'
    else:
        # 用于环境检查的会话
        session_id = f'env_check_{int(time.time() * 1000)}'
        
    # 创建临时用户数据目录
    temp_dir = os.path.join(
        os.path.dirname(__file__), 
        'temp_chrome_data', 
        session_id
    )
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    
    # 如果指定了下载目录，添加下载配置
    if output_dir:
        prefs = {
            "download.default_directory": os.path.abspath(output_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options, temp_dir

def cleanup_chrome_data(temp_dir):
    """清理临时用户数据目录"""
    try:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            logging.info(f"已清理临时目录: {temp_dir}")
    except Exception as e:
        logging.warning(f"清理临时目录失败: {str(e)}")

def check_environment():
    """检查环境是否满足要求"""
    logging.info("检查运行环境...")
    print("正在检查浏览器环境...")
    
    try:
        chrome_options, temp_dir = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        print("✓ 浏览器环境检查通过!")
        return True
    except Exception as e:
        logging.error(f"环境检查失败: {str(e)}")
        print(f"✗ 浏览器环境检查失败: {str(e)}")
        return False
    finally:
        if 'temp_dir' in locals():
            cleanup_chrome_data(temp_dir)

def download_vsix_selenium(extension_id, output_dir, max_retries=3):
    """使用 selenium 下载 VSIX 文件"""
    logging.info(f"开始下载扩展: {extension_id}")
    retry_count = 0
    
    while retry_count < max_retries:
        chrome_options, temp_dir = get_chrome_options(output_dir, extension_id)
        driver = None
        try:
            retry_count += 1
            driver = webdriver.Chrome(options=chrome_options)
            
            # 导航到下载网站
            driver.get("https://vsix.2i.gs/")
            logging.info(f"尝试 {retry_count}/{max_retries}: 已打开下载页面")
            time.sleep(3)  # 等待页面加载
            
            # 找到输入框并确保清空
            input_box = driver.find_element(By.CLASS_NAME, "css-1x5jdmq")
            input_box.clear()
            time.sleep(1)  # 等待清空完成
            
            # 直接粘贴整个扩展ID
            input_box.send_keys(extension_id)
            logging.info(f"已输入扩展ID: {extension_id}")
            time.sleep(0.5) # 等待输入反应

            # 触发失去焦点事件
            driver.execute_script("arguments[0].blur();", input_box)
            logging.info(f"已触发输入框失去焦点事件")
            time.sleep(1)  # 等待页面可能因此产生的变化
            
            # 点击下载按钮
            download_button = driver.find_element(By.XPATH, "//button[contains(text(), '下载')]")
            driver.execute_script("arguments[0].click();", download_button)
            logging.info("已点击第一次下载按钮")
            time.sleep(5)
            
            # 检查下载结果
            downloaded_file = None
            for _ in range(30):  # 最多等待30*2=60秒
                current_files = os.listdir(output_dir)
                for file in current_files:
                    if file.endswith('.vsix') and extension_id.lower() in file.lower():
                        downloaded_file = file
                        break
                if downloaded_file:
                    break
                time.sleep(2)
            
            if downloaded_file:
                logging.info(f"下载成功: {downloaded_file}")
                return True
            else:
                logging.error(f"下载超时: {extension_id} (尝试 {retry_count}/{max_retries})")
                if retry_count < max_retries:
                    time.sleep(5 * retry_count)  # 重试前等待更长时间
                    continue
                return False
                
        except Exception as e:
            logging.error(f"下载过程发生错误: {str(e)}")
            if retry_count < max_retries:
                time.sleep(5 * retry_count)
                continue
            return False
            
        finally:
            if driver:
                driver.quit()
            cleanup_chrome_data(temp_dir)
    
    return False

def batch_download(extensions, output_dir, max_workers=3):
    """批量下载扩展
    Args:
        extensions: 扩展ID列表
        output_dir: 输出目录
        max_workers: 最大并发数(默认3)
    """
    # 只检查一次环境
    if not check_environment():
        print("环境检查失败，程序终止")
        return
        
    print(f"\n当前配置: 最大并发数={max_workers}, 每个扩展最大重试次数=3")
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"创建输出目录: {output_dir}")
    
    total = len(extensions)
    success_count = 0
    fail_count = 0
    
    logging.info(f"开始批量下载，共 {total} 个扩展")
    print(f"\n{'='*50}")
    print(f"开始下载 {total} 个扩展...")
    print(f"注意：每个扩展下载可能需要1-3分钟，请耐心等待")
    print("="*50)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_vsix_selenium, ext, output_dir): ext
            for ext in extensions
        }
        
        for future in as_completed(futures):
            ext = futures[future]
            try:
                success = future.result()
                if success:
                    success_count += 1
                    print(f"✓ 成功: {ext}")
                else:
                    fail_count += 1
                    print(f"✗ 失败: {ext}")
            except Exception as e:
                logging.error(f"处理扩展失败: {ext}, 错误: {str(e)}")
                fail_count += 1
                print(f"✗ 错误: {ext} - {str(e)}")

    logging.info(f"下载完成! 成功: {success_count}, 失败: {fail_count}")
    print(f"\n{'='*50}")
    print(f"下载完成! 成功: {success_count}/{total}, 失败: {fail_count}/{total}")
    print(f"下载文件保存在: {os.path.abspath(output_dir)}")
    print("="*50)

if __name__ == "__main__":
    # 从txt文件读取扩展列表
    try:
        # 从环境变量读取配置
        output_dir = os.getenv('VSIX_DOWNLOAD_PATH', 'vsix_files')
        max_workers = int(os.getenv('VSIX_MAX_WORKERS', '3')) # 默认为3个线程

        extensions_file = os.path.join(os.path.dirname(__file__), 'extensions.txt')
        extensions = read_extensions(extensions_file)
        
        print("="*50)
        print(f"VSIX下载器 v1.2 (插件增强版)")
        print(f"扩展列表: {extensions_file}")
        print(f"输出目录: {os.path.abspath(output_dir)}")
        print(f"最大并发数: {max_workers}")
        print(f"找到 {len(extensions)} 个扩展")
        print("="*50)
        
        batch_download(extensions, output_dir, max_workers=max_workers)
    except Exception as e:
        logging.error(f"程序运行失败: {str(e)}")
        print(f"\n错误: {str(e)}")
        print("程序终止")
