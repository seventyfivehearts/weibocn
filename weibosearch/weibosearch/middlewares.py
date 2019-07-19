# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import requests
import json
import logging
from requests.exceptions import ConnectionError
from scrapy.exceptions import IgnoreRequest

class CookiesMiddleware():
    def __init__(self,cookies_pool_url):
        self.logger = logging.getLogger(__name__)
        self.cookies_pool_url=cookies_pool_url

    def _get_random_cookies(self):
        try:
            response = requests.get(self.cookies_pool_url)
            if response.status_code ==200:
                cookies = json.loads(response.text)
                return cookies
        except ConnectionError:
            return None

    def process_request(self, request, spider):
        cookies = self._get_random_cookies()
        if cookies:
            request.cookies = cookies
            self.logger.debug('Using Cookies ' + json.dumps(cookies))
        else:
            self.logger.debug('No Valid Cookies')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            cookies_pool_url=crawler.settings.get('COOKIES_POOL_URL')
        )

    def process_response(self,request,response,spider):
        if response.status in [300,301,302,303]:
            try:
                redirect_url = response.headers['location']
                if 'passport' in redirect_url:
                    self.logger.warning('Need login,Update Cookies')
                elif 'weibo.cn/security' in redirect_url:
                    self.logger.warning('Account is Locked!')
                request.cookies = self._get_random_cookies()
                return request
            except:
                raise IgnoreRequest
        elif response.status in [414]:
            return request
        else:
            return response
