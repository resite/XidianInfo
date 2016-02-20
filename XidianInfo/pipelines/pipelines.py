# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

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
                    print('000000000000000000000')
                if not os.path.exists(image_path):
                    print('111111111111111111111')
                    with open(image_path,'wb') as handle:
                        response = requests.get(image_url, stream=True)
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
        return item
