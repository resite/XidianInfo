#!/usr/bin/env python
# encoding: utf-8

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from XidianInfo.items import XidianinfoItem
import redis

class XidianInfoSpider(CrawlSpider):
    def __init__(self):
        self.r = redis.Redis(host='localhost',port=6379,db=0)

    name = 'info.xidian.edu.cn'
    alllowed_domains = ['info.xidian.edu.cn']
    start_urls = [
            "http://info.xidian.edu.cn/info/1010/8713.htm"
            #"http://info.xidian.edu.cn/xdxw.htm",
            #"http://info.xidian.edu.cn/bkjx.htm",
            #"http://info.xidian.edu.cn/yjsjx.htm",
            #"http://info.xidian.edu.cn/kyxx.htm",
            #"http://info.xidian.edu.cn/hzjl.htm",
            #"http://info.xidian.edu.cn/xsgz.htm",
            #"http://info.xidian.edu.cn/rsdt.htm",
            #"http://info.xidian.edu.cn/bkzs.htm",
            #"http://info.xidian.edu.cn/xsjy.htm",
            ]

    rules = (
            #Rule(LinkExtractor(allow=('\d+.htm',))),
            Rule(LinkExtractor(allow=('info/\d+/\d+.htm',)),callback='parse_item'),
            )

    def parse_item(self, response):
        self.log('Hi,this is an item page! %s' % response.url)
        #r = redis.Redis(host='localhost',port=6379,db=0)
        self.r.set(response.url,1)
        sel = Selector(response)
        item = XidianinfoItem()
        urlParts = response.url.strip().split('/')
        item['newsType'] = urlParts[-2]
        item['newsId'] = urlParts[-1][:-4]
        item['newsTitle'] = sel.xpath('//td[@class="titlestyle1040"]/text()').extract_first()
        item['newsTime'] = sel.xpath('//span[@class="timestyle1040"]/text()').extract_first().strip()
        item['newsFrom'] = sel.xpath('//span[@class="authorstyle1040"]/text()').extract_first().strip()
        item['newsContent'] = sel.xpath('//div[@class="c1040_content"]//p').extract_first()

        image_urls = response.xpath('//div[@class="c1040_content"]/div/p/img/@src').extract()
        item['image_urls'] = []
        for image_url in image_urls:
            item['image_urls'].append(image_url.replace('../..','http://info.xidian.edu.cn'))

        print('============================')

        print(item['newsType'].strip().encode('utf8') + '---------------------')
        print(item['newsId'].strip().encode('utf8') + '---------------------')
        print(item['newsTitle'].strip().encode('utf8') + '---------------------')
        print(item['newsTime'].strip().encode('utf8') + '---------------------')
        print(item['newsFrom'].strip().encode('utf8') + '---------------------')
        print(item['newsContent'].strip().encode('utf8') + '---------------------')

        return item
