import requests
from lxml import etree
import argparse
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--save_root", type=str,
                    default="./data_baidu")
parser.add_argument("--query_file", type=str, default='query.txt')
parser.add_argument("--search_count", type=int, default=100)  # find 500 images and stop
parser.add_argument('--saved_url_path', type=str, default='./')
args = parser.parse_args()

# default param
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}
url = 'https://image.baidu.com/search/acjson?'

error_bound = 200

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
    saved_url_file = os.path.join(args.saved_url_path, q + '_baidu.txt')
    saved_url_list = []
    if os.path.exists(saved_url_file):
        with open(saved_url_file, 'r') as f:
            for line in f.readlines():
                saved_url_list.append(line.strip())

    save_path = os.path.join(args.save_root, q)
    if not os.path.exists(save_path):
        command = 'mkdir -p ' + save_path
        os.system(command)

    while count < args.search_count and err_cnt < error_bound:
        param = {
            'tn': 'resultjson_com',
            'logid': '8846269338939606587',
            'ipn': 'rj',
            'ct': '201326592',
            'is': '',
            'fp': 'result',
            'queryWord': q,
            'cl': '2',
            'lm': '-1',
            'ie': 'utf-8',
            'oe': 'utf-8',
            'adpicid': '',
            'st': '-1',
            'z': '',
            'ic': '',
            'hd': '',
            'latest': '',
            'copyright': '',
            'word': q,
            's': '',
            'se': '',
            'tab': '',
            'width': '',
            'height': '',
            'face': '0',
            'istype': '2',
            'qc': '',
            'nc': '1',
            'fr': '',
            'expermode': '',
            'force': '',
            'cg': 'girl',
            'pn': pn,  # 从第几张图片开始
            'rn': '30',
            'gsm': '1e',
        }
        try:
            page_text = requests.get(url=url, headers=header, params=param)
            page_text.encoding = 'utf-8'
            page_text = page_text.json()
            info_list = page_text['data']
            del info_list[-1]
            img_path_list = []
            for i in info_list:
                if i not in saved_url_list:
                    img_path_list.append(i['thumbURL'])
        except Exception:
            err_cnt += 1
            continue

        for img_url in img_path_list:
            try:
                img_data = requests.get(url=img_url, headers=header).content
                t = time.localtime()
                save_name = os.path.join(save_path, "%d_%d_%d_%d_%d_%d_%0.5d.jpg" %
                                         (t.tm_year, t.tm_mon, t.tm_mday,
                                          t.tm_hour, t.tm_min, t.tm_sec, count))
                with open(save_name, 'wb') as fp:
                    fp.write(img_data)
            except Exception:
                time.sleep(1)
                print("save error", )
                err_cnt += 1
            else:
                print("save success: ", save_name)
                count += 1
                saved_url_list.append(img_url)
        pn += 29

    # saved url to file
    with open(saved_url_file, 'w') as f:
        for line in saved_url_list:
            f.write(line + '\n')
