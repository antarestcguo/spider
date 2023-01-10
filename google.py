import requests
# pip install selenium==4.1.0
from selenium import webdriver
import argparse
import os
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

parser = argparse.ArgumentParser()
parser.add_argument("--save_root", type=str,
                    default="./data_google")
parser.add_argument("--query_file", type=str, default='query.txt')
parser.add_argument("--search_count", type=int, default=500)  # find 500 images and stop
parser.add_argument('--saved_url_path', type=str, default='./')
args = parser.parse_args()

# default param
ch_op = Options()
# 设置谷歌浏览器的页面无可视化，如果需要可视化请注释这两行代码
ch_op.add_argument('--headless')
ch_op.add_argument('--disable-gpu')
error_bound = 100

# read query
query_list = []
with open(args.query_file, 'r') as f:
    for line in f.readlines():
        query_list.append(line.strip())

# start to get image
for q in query_list:
    count = 0
    err_cnt = 0
    pn = 1

    # read saved url list
    saved_url_file = os.path.join(args.saved_url_path, q + '_google.txt')
    saved_url_list = []
    if os.path.exists(saved_url_file):
        with open(saved_url_file, 'r') as f:
            for line in f.readlines():
                saved_url_list.append(line.strip())

    save_path = os.path.join(args.save_root, q)
    if not os.path.exists(save_path):
        command = 'mkdir -p ' + save_path
        os.system(command)

    # init driver
    url = 'https://www.google.com.hk/search?q=' + q + '&tbm=isch'
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=ch_op)
    # 访问url
    browser.get(url)
    # 最大化窗口，之后需要爬取窗口中所见的所有图片
    browser.maximize_window()
    pos = 0

    while count < args.search_count or err_cnt < error_bound:
        pos += 500
        # 向下滑动
        js = 'var q=document.documentElement.scrollTop=' + str(pos)
        browser.execute_script(js)
        time.sleep(1)
        img_elements = browser.find_elements_by_tag_name('img')

        for img_element in img_elements:
            img_url = img_element.get_attribute('src')
            # 前几个图片的url太长，不是图片的url，先过滤掉，爬后面的
            if isinstance(img_url, str):
                if len(img_url) <= 200:
                    # 将干扰的goole图标筛去
                    if 'images' in img_url:
                        # 判断是否已经爬过，因为每次爬取当前窗口，或许会重复
                        # 实际上这里可以修改一下，将列表只存储上一次的url，这样可以节省开销，不过我懒得写了···
                        if img_url not in saved_url_list:
                            try:
                                # img_url_dic.append(img_url)
                                save_name = os.path.join(save_path, "%0.5d.jpg" % (count))
                                r = requests.get(img_url)
                                with open(save_name, 'wb') as f:
                                    f.write(r.content)
                                f.close()
                                time.sleep(0.2)
                            except:
                                print("save error", )
                                err_cnt += 1

                            else:
                                print("save success: ", save_name)
                                count += 1
                                saved_url_list.append(img_url)
    # saved url to file
    with open(saved_url_file, 'w') as f:
        for line in saved_url_list:
            f.write(line + '\n')
