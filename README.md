# 概要
1. 用来抓取info.xidian.edu.cn上的新闻
2. 下载图片
3. 利用redis去除已经之前已经爬过的URL，实现增量爬取网页

## 项目地址
[https://github.com/PascoCoder/XidianInfo](https://github.com/PascoCoder/XidianInfo)

## 参考文档
[scrapy中文文档](http://scrapy-chs.readthedocs.org/zh_CN/1.0/index.html)

感谢：[博客](http://www.fengxiaochuang.com/?p=144)

## 安装
基本上就是一条命令
```
pip install scrapy
```
## 创建项目
输入命令
```shell
scrapy startproject tutorial
```
会出现一个tutorial的目录，目录结构如下
```
tutorial/
    scrapy.cfg
    tutorial/					
        __init__.py			
        items.py
        pipelines.py
        settings.py
        spiders/
            __init__.py
```
1. scrapy.cfg:部署配置文件
2. items.py:项目items文件，定义字典的字段
3. pipeline.py:项目管道文件，用于后续处理
4. settings.py:项目设置文件
5. spider/:用来放爬虫的目录

自己添加的文件：

1. middlewares.py:下载中间件，位置与settings.py在同一目录下，或者放在新建middleware文件夹内


## 定义item
item是保存爬取到的数据的容器，使用方法类似于Python中的字典。
```Python
import scrapy

class DmozItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()
```
## 第一个爬虫
Spider是从**单一网站**上爬去数据的类。
为了创建一个Spider，您必须继承 `scrapy.Spider` 类， 且定义一些属性:

1. `name`: 用于区别Spider。 该名字必须是唯一的，您不可以为不同的Spider设定相同的名字。
2. `start_urls`: 包含了Spider在启动时进行爬取的url列表。 因此，第一个被获取到的页面将是其中之一。 后续的URL则从初始的URL获取到的数据中提取。
3. `parse()` 是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 该方法负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。
以下为我们的第一个Spider代码，保存在 tutorial/spiders 目录下的 dmoz_spider.py 文件中:
```Python
import scrapy

class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    def parse(self, response):
        filename = response.url.split("/")[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
```
切换到工程的根目录，执行命令
```Shell
scrapy crawl dmoz
```
会发现工程内多了一个文件，即请求到的结果。

### 代码含义解释：

Scrapy为Spider的 `start_urls` 属性中的每个URL创建了 `scrapy.Request` 对象，并将 `parse` 方法作为回调函数(callback)赋值给了Request。

Request对象经过调度，执行生成 scrapy.http.Response 对象并送回给spider parse() 方法。

### 处理请求结果
从网页中提取数据，这里介绍[XPath方法](/2016/02/07/Use-XPath/)


### 最终的样子
```Python
import scrapy

from tutorial.items import DmozItem

class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    def parse(self, response):
        for sel in response.xpath('//ul/li'):
            item = DmozItem()
            item['title'] = sel.xpath('a/text()').extract()
            item['link'] = sel.xpath('a/@href').extract()
            item['desc'] = sel.xpath('text()').extract()
            yield item
```

## Spiders
Spider类定义了如何爬取某个(或某些)网站。包括了爬取的动作(例如:是否跟进链接)以及如何从网页的内容中提取结构化数据(爬取item)。 换句话说，Spider就是您定义爬取的动作及分析某个网页(或者是有些网页)的地方。

scrapy提供了多种Spider

### scrapy.Spider

`scrapy.Spider`:最简单的spider，Spider并没有提供什么特殊的功能。 其仅仅提供了 start_requests() 的默认实现，读取并请求spider属性中的 start_urls, 并根据返回的结果(resulting responses)调用spider的 parse 方法。如上面的那个例子。

### CrawlSpider

`CrawlSpider`:爬取一般网站常用的spider。其定义了一些规则(rule)来提供跟进link的方便的机制。 也许该spider并不是完全适合特定网站或项目，但其对很多情况都使用。
1. `rules`:一个包含一个(或多个) Rule 对象的集合(list)。 每个 Rule 对爬取网站的动作定义了特定表现。 Rule对象在下边会介绍。 如果多个rule匹配了相同的链接，则根据他们在本属性中被定义的顺序，第一个会被使用。
2. `parse_start_url(response)`:该spider也提供了一个可复写(overrideable)的方法。当start_url的请求返回时，该方法被调用。 该方法分析最初的返回值并必须返回一个 Item 对象或者 一个 Request 对象或者 一个可迭代的包含二者对象。

#### 爬取规则：
`link_extractor` 是一个 Link Extractor 对象。 其定义了如何从爬取到的页面提取链接。

`callback` 是一个callable或string(该spider中同名的函数将会被调用)。 从link_extractor中每获取到链接时将会调用该函数。该回调函数接受一个response作为其第一个参数， 并返回一个包含 Item 以及(或) Request 对象(或者这两者的子类)的列表(list)。

> 警告
> 
> 当编写爬虫规则时，请避免使用 parse 作为回调函数。 由于 CrawlSpider 使用 parse 方法来实现其逻辑，如果 您覆盖了 parse 方法，crawl spider 将会运行失败。

`cb_kwargs` 包含传递给回调函数的参数(keyword argument)的字典。

`follow` 是一个布尔(boolean)值，指定了根据该规则从response提取的链接是否需要跟进。 如果 callback 为None， follow 默认设置为 True ，否则默认为 False 。

`process_links` 是一个callable或string(该spider中同名的函数将会被调用)。 从link_extractor中获取到链接列表时将会调用该函数。该方法主要用来过滤。

`process_request` 是一个callable或string(该spider中同名的函数将会被调用)。 该规则提取到每个request时都会调用该函数。该函数必须返回一个request或者None。 (用来过滤request)
#### CrawlSpider样例
```Python
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class MySpider(CrawlSpider):
    name = 'example.com'
    allowed_domains = ['example.com']
    start_urls = ['http://www.example.com']

    rules = (
        # 提取匹配 'category.php' (但不匹配 'subsection.php') 的链接并跟进链接(没有callback意味着follow默认为True)
        Rule(LinkExtractor(allow=('category\.php', ), deny=('subsection\.php', ))),

        # 提取匹配 'item.php' 的链接并使用spider的parse_item方法进行分析
        Rule(LinkExtractor(allow=('item\.php', )), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)

        item = scrapy.Item()
        item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
        item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
        return item
```
该spider将从example.com的首页开始爬取，获取category以及item的链接并对后者使用 parse_item 方法。 当item获得返回(response)时，将使用XPath处理HTML并生成一些数据填入 Item 中。

## Pipeline

注意：pipelines需要在settings.py中启用

当Item在Spider中被收集之后，它将会被传递到Item Pipeline，一些组件会按照一定的顺序执行对Item的处理。
以下是item pipeline的一些典型应用：

1. 清理HTML数据
2. 验证爬取的数据(检查item包含某些字段)
3. 下载图片
4. 查重(并丢弃)
5. 将爬取结果保存到数据库中

### 样例
```Python
import pymongo

class MongoPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))
        return item
```
写好后需要在`settings.py`中启用你写好的Item Pipeline组件
```python
ITEM_PIPELINES = {
    'myproject.pipelines.PricePipeline': 300,
    'myproject.pipelines.JsonWriterPipeline': 800,
}
```
分配给每个类的整型值，确定了他们运行的顺序，item按数字从低到高的顺序，通过pipeline，通常将这些数字定义在0-1000范围内。

### 下载图片
[scrapy自带的图片下载的pipelines](http://doc.scrapy.org/en/1.0/topics/media-pipeline.html)会根据图片链接的hash值会重新命名图片的名称，如果对图片名称没要求的话可以使用

所以我选择了自己重新写一个pipelines用来下载图片，代码如下

```python
import os
import requests

class ImagePipeline(object):
    def process_item(self, item, spider):
        if 'image_urls' in item:
            for image_url in item['image_urls']:
                image_path = image_url.replace('http://info.xidian.edu.cn/','')
                image_folder_url_list = image_path.split('/')[:-1]
                image_folder_path = '/'.join(image_folder_url_list) + '/'

                if not os.path.exists(image_folder_path):
                    os.makedirs(image_folder_path)
                if not os.path.exists(image_path):
                    with open(image_path,'wb') as handle:
                        response = requests.get(image_url, stream=True)
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
        return item
```

## 下载中间件（middlewares）
在此部分用redis去重复

可以实现一下三个方法
### process_request(request, spider)

当每个request通过下载中间件时，该方法被调用。

process_request() 必须返回其中之一: 返回 None 、返回一个 Response 对象、返回一个 Request 对象或raise IgnoreRequest 。

如果其返回 None ，Scrapy将继续处理该request，执行其他的中间件的相应方法，直到合适的下载器处理函数(download handler)被调用， 该request被执行(其response被下载)。

如果其返回 Response 对象，Scrapy将不会调用 任何 其他的 process_request() 或 process_exception() 方法，或相应地下载函数； 其将返回该response。 已安装的中间件的 process_response() 方法则会在每个response返回时被调用。

如果其返回 Request 对象，Scrapy则停止调用 process_request方法并重新调度返回的request。当新返回的request被执行后， 相应地中间件链将会根据下载的response被调用。

如果其raise一个 IgnoreRequest 异常，则安装的下载中间件的 process_exception() 方法会被调用。如果没有任何一个方法处理该异常， 则request的errback(Request.errback)方法会被调用。如果没有代码处理抛出的异常， 则该异常被忽略且不记录(不同于其他异常那样)。

### process_response(request, response, spider)

process_request() 必须返回以下之一: 返回一个 Response 对象、 返回一个 Request 对象或raise一个 IgnoreRequest 异常。

如果其返回一个 Response (可以与传入的response相同，也可以是全新的对象)， 该response会被在链中的其他中间件的 process_response() 方法处理。

如果其返回一个 Request 对象，则中间件链停止， 返回的request会被重新调度下载。处理类似于 process_request() 返回request所做的那样。

如果其抛出一个 IgnoreRequest 异常，则调用request的errback(Request.errback)。 如果没有代码处理抛出的异常，则该异常被忽略且不记录(不同于其他异常那样)。

### process_exception(request, exception, spider)

当下载处理器(download handler)或 process_request() (下载中间件)抛出异常(包括 IgnoreRequest 异常)时， Scrapy调用 process_exception() 。

process_exception() 应该返回以下之一: 返回 None 、 一个 Response 对象、或者一个 Request 对象。

如果其返回 None ，Scrapy将会继续处理该异常，接着调用已安装的其他中间件的 process_exception() 方法，直到所有中间件都被调用完毕，则调用默认的异常处理。

如果其返回一个 Response 对象，则已安装的中间件链的 process_response() 方法被调用。Scrapy将不会调用任何其他中间件的 process_exception() 方法。

如果其返回一个 Request 对象， 则返回的request将会被重新调用下载。这将停止中间件的 process_exception() 方法执行，就如返回一个response的那样。

```python
from scrapy.exceptions import IgnoreRequest
import redis

class MyCustomDownloaderMiddleware(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost',port=6379,db=0)

    def process_request(self, request, spider):
        if self.r.exists(request.url):
            raise IgnoreRequest("request is exists")
        else:
            return None
```

## todos
1. 新建一个pipelines来下载附件
2. 爬取到的item存入数据库
