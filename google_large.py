import requests
# pip install selenium==4.1.0
from selenium import webdriver
import argparse
import os
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote, unquote
import re

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

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Proxy-Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    # 'Connection': 'close',
}

# read query
query_list = []
with open(args.query_file, 'r') as f:
    for line in f.readlines():
        query_list.append(line.strip())


def my_print(msg, quiet=False):
    if not quiet:
        print(msg)


def google_image_url_from_webpage(driver, max_number, quiet=False):
    thumb_elements_old = []
    thumb_elements = []
    while True:
        try:
            thumb_elements = driver.find_elements_by_class_name("rg_i")
            my_print("Find {} images.".format(len(thumb_elements)), quiet)
            if len(thumb_elements) >= max_number:
                break
            if len(thumb_elements) == len(thumb_elements_old):
                break
            thumb_elements_old = thumb_elements
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            show_more = driver.find_elements_by_class_name("mye4qd")
            if len(show_more) == 1 and show_more[0].is_displayed() and show_more[0].is_enabled():
                my_print("Click show_more button.", quiet)
                show_more[0].click()
            time.sleep(3)
        except Exception as e:
            print("Exception ", e)
            pass

    if len(thumb_elements) == 0:
        return []

    my_print("Click on each thumbnail image to get image url, may take a moment ...", quiet)

    retry_click = []
    for i, elem in enumerate(thumb_elements):
        try:
            if i != 0 and i % 50 == 0:
                my_print("{} thumbnail clicked.".format(i), quiet)
            if not elem.is_displayed() or not elem.is_enabled():
                retry_click.append(elem)
                continue
            elem.click()
        except Exception as e:
            print("Error while clicking in thumbnail:", e)
            retry_click.append(elem)

    if len(retry_click) > 0:
        my_print("Retry some failed clicks ...", quiet)
        for elem in retry_click:
            try:
                if elem.is_displayed() and elem.is_enabled():
                    elem.click()
            except Exception as e:
                print("Error while retrying click:", e)

    image_elements = driver.find_elements_by_class_name("islib")
    image_urls = list()
    url_pattern = r"imgurl=\S*&amp;imgrefurl"

    for image_element in image_elements[:max_number]:
        outer_html = image_element.get_attribute("outerHTML")
        re_group = re.search(url_pattern, outer_html)
        if re_group is not None:
            image_url = unquote(re_group.group()[7:-14])
            image_urls.append(image_url)
    return image_urls


# start to get image
for q in query_list:
    count = 0

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

    # gen url
    base_url = "https://www.google.com/search?tbm=isch&hl=en"
    keywords_str = "&q=" + quote(q)
    query_url = base_url + keywords_str
    query_url += "&safe=off"
    filter_url = "&tbs="
    query_url += filter_url

    # init browser
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=ch_op)
    browser.set_window_size(1920, 1080)
    browser.get(query_url)

    quiet = False
    image_urls = google_image_url_from_webpage(browser, args.search_count, quiet)

    total_cnt = len(image_urls)
    print("get url end! start to download, len(url) = ", total_cnt)
    # start to donwload
    err_cnt = 0
    for it_url in image_urls:
        if it_url in saved_url_list:
            continue
        t = time.localtime()
        save_name = os.path.join(save_path, "%d_%d_%d_%d_%d_%d_%0.5d.jpg" %
                                 (t.tm_year, t.tm_mon, t.tm_mday,
                                  t.tm_hour, t.tm_min, t.tm_sec, count))
        try_times = 0
        while True:
            try:
                try_times += 1
                response = requests.get(
                    it_url, headers=headers, timeout=20, proxies=None)
                with open(save_name, 'wb') as f:
                    f.write(response.content)
                response.close()
            except Exception as e:
                if try_times < 3:
                    continue
                if response:
                    response.close()
                err_cnt += 1
                print("save error, total: %d, saved: %d, err: %d" % (total_cnt, count, err_cnt))
                break
            else:
                saved_url_list.append(it_url)
                count += 1
                print("save name:", save_name)
                print("save success, total: %d, saved: %d, err: %d" % (total_cnt, count, err_cnt))
                break

    # saved url to file
    with open(saved_url_file, 'w') as f:
        for line in saved_url_list:
            f.write(line + '\n')
