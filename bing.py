# coding=utf-8
import os
import urllib.request
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote
import string
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--save_root", type=str,
                    default="./data_bing")
parser.add_argument("--query_file", type=str, default='query.txt')
parser.add_argument("--search_count", type=int, default=500)  # find 500 images and stop
parser.add_argument('--saved_url_path', type=str, default='./')
args = parser.parse_args()


def getStartHtml(url):
    try:
        url = quote(url, safe=string.printable)
        page = urllib.request.Request(url, headers=header)
        html = urllib.request.urlopen(page)
    except Exception:
        html = None
    return html


def findImgUrlFromHtml(html, rule, count, err_cnt, save_path, saved_url_list):
    soup = BeautifulSoup(html, 'lxml')
    link_list = soup.find_all("a", class_="iusc")
    if len(link_list) == 0:
        err_cnt += 1
    download_list = []
    for link in link_list:
        result = re.search(rule, str(link))
        if result:
            url = result.group(0)
            url = url[8:len(url)]
            if url in saved_url_list:
                continue

            t = time.localtime()
            save_name = os.path.join(save_path, "%d_%d_%d_%d_%d_%d_%0.5d.jpg" %
                                     (t.tm_year, t.tm_mon, t.tm_mday,
                                      t.tm_hour, t.tm_min, t.tm_sec, count))
            try:
                # img_data = requests.get(url=url, headers=header).content
                # with open(save_name, 'wb') as fp:
                #     fp.write(img_data)
                urllib.request.urlretrieve(url, save_name)
            except Exception:
                time.sleep(1)
                print("save error", )
                err_cnt += 1
            else:
                print("save success: ", save_name)
                count += 1
                download_list.append(url)

    return count, err_cnt, download_list


# deault param
header = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) "
                   "Gecko/20100101 Firefox/64.0")
}
error_bound = 1000
rule = re.compile(r"\"murl\"\:\"http\S[^\"]+")

# read query
query_list = []
with open(args.query_file, 'r') as f:
    for line in f.readlines():
        query_list.append(line.strip())

# start to get image
for q in query_list:
    # base setting
    first = 1
    loadNum = 35
    sfx = 1
    count = 0
    err_cnt = 0

    save_path = os.path.join(args.save_root, q)
    if not os.path.exists(save_path):
        command = 'mkdir -p ' + save_path
        os.system(command)

    saved_url_file = os.path.join(args.saved_url_path, q + '_bing.txt')
    saved_url_list = []
    if os.path.exists(saved_url_file):
        with open(saved_url_file, 'r') as f:
            for line in f.readlines():
                saved_url_list.append(line.strip())

    while count < args.search_count and err_cnt < error_bound:
        url = "http://cn.bing.com/images/async?first=%s&count=35&q=%s" % (first, q)
        html = getStartHtml(url)
        if html is not None:
            count, err_cnt, download_list = findImgUrlFromHtml(html, rule, count, err_cnt, save_path, saved_url_list)
            saved_url_list.extend(download_list)
        else:
            err_cnt += 1
        first += 1

    # saved url to file
    with open(saved_url_file, 'w') as f:
        for line in saved_url_list:
            f.write(line + '\n')
