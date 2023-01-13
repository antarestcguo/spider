# 图片爬虫
## 介绍
包含谷歌爬虫，bing爬虫，百度爬虫

## 依赖项
```
pip install requirements.txt
```

## 使用说明
参数
+ save_root：保存路径，会以 save_root+query词新建目录保存图片
+ query_file：query词以txt文件形式传入，暂时不支持空格，可以额外做下处理
+ search_count：爬取图片数量，这里由于不同脚本获取url机制不同，不保证一定怕取到准确数量的图片
+ saved_url_path：从路径下读取已爬图片的url文件，不重复爬

目前只支持单线程，且逻辑比较简单，爬虫的核心是读取到url，读取到后的保存处理和后续逻辑可以自行改写

### 谷歌爬虫
+ googla_large.py 爬谷歌大图
+ google.py 爬谷歌缩略图
+ google_use_plugin.py 使用插件爬取，不支持返回已爬图的url

请确保电脑可以访问谷歌

若服务器运行，请在服务器安装无界面谷歌浏览器 [安装方式](https://blog.csdn.net/qq_39147299/article/details/122588194)

```
python google_large.py --serach_count 2000
```

### bing爬虫
bing 爬虫很慢
```
python bing.py --serach_count 2000
```


### 百度爬虫
```
python baidu.py --serach_count 2000
```

## 参考
 + https://www.easemob.com/news/3077 