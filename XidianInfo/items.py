# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class XidianinfoItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    newsType = Field()
    newsId = Field()
    newsTitle = Field()
    newsTime = Field()
    newsFrom = Field()
    newsContent = Field()

    image_urls = Field()
    images = Field()
    pass
