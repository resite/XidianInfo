#!/usr/bin/env python
# encoding: utf-8

from scrapy.exceptions import IgnoreRequest
import redis

class MyCustomDownloaderMiddleware(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost',port=6379,db=0)

    def process_request(self, request, spider):
        print("000000000000000000000000")
        #r = redis.Redis(host='localhost',port=6379,db=0)
        if self.r.exists(request.url):
            raise IgnoreRequest("request is exists")
        else:
            return None
