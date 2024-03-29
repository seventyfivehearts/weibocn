# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from weibosearch.items import WeiboItem
import re
import time
import pymongo

class WeiboPipeline(object):
    def parse_time(self, datetime):
        if re.match('\d+月\d+日', datetime):
            datetime = time.strftime('%Y{y}').format(y = '年') + datetime
        if re.match('\d+分钟前', datetime):
            minute = re.match('(\d+)', datetime).group(1)
            datetime = time.strftime('%Y{y}%m{m}%d{d} %H:%M', time.localtime(time.time() - float(minute) * 60)).format(y='年',m='月',d='日')
        if re.match('今天.*', datetime):
            datetime = re.match('今天(.*)', datetime).group(1).strip()
            datetime = time.strftime('%Y{y}%m{m}%d{d}', time.localtime()).format(y='年',m='月',d='日') + ' ' + datetime
        return datetime

    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            if item.get('content'):
                item['content'] = item['content'].lstrip(':').strip()
            if item.get('posted_at'):
                item['posted_at'] = item['posted_at'].strip()
                item['posted_at'] = self.parse_time(item.get('posted_at'))
        return item

class MongoPipeline():
    def __init__(self,mongo_url,mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url =crawler.settings.get("MONGO_URL"),
            mongo_db = crawler.settings.get("MONGO_DB")
        )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def close_spider(self,spider):
        self.client.close()

    def process_item(self,item,spider):
        self.db[item.table_name].update({'id':item.get('id')},{'$set':dict(item)},True)
        return item

