from icrawler.builtin import GoogleImageCrawler
import os

q = 'cat'
save_path = os.path.join('./data_google', q)
if not os.path.exists(save_path):
    command = 'mkdir -p ' + save_path
    os.system(command)
# google_storage = {'root_dir': save_path}
# google_crawler = GoogleImageCrawler(parser_threads=1, downloader_threads=1, storage=google_storage)
# google_crawler.crawl(keyword=q, max_num=10)

a = 0
