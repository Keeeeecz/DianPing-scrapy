# -*- coding: utf-8 -*-
from importlib import reload

import scrapy, sys
import scrapy.spiders
from scrapy.conf import settings
from scrapy import Request
from debug.items import DPItem
from debug.spiders.DecodePOI import decode
import json
import re
# 设置编码格式
reload(sys)

class DmozSpider(scrapy.spiders.Spider):
    nullData = 0
    i = 0            #店家数量计数
    city = 0         #城市计数
    name = "dianping"
    coun = 0         #记录每个城市已爬分区，达到最大后跳转到下一城市
    linklen=0        #存储每个城市的分区数
    download_delay = 3
    # ["杭州","广州","上海","北京","深圳","西安","重庆","南京","武汉","成都","兰州"]
    cityName = ["杭州","广州","上海","北京","深圳","西安","重庆","南京","武汉","成都","兰州"]
    start_urls = [
        # "http://www.dianping.com/hangzhou/ch10",
        "http://www.dianping.com/guangzhou/ch10",
        "http://www.dianping.com/shanghai/ch10",
        "http://www.dianping.com/beijing/ch10",
        "http://www.dianping.com/shenzhen/ch10",
        "http://www.dianping.com/xian/ch10",
        "http://www.dianping.com/chongqing/ch10",
        "http://www.dianping.com/nanjing/ch10",
        "http://www.dianping.com/wuhan/ch10",
        "http://www.dianping.com/chengdu/ch10",
        "http://www.dianping.com/lanzhou/ch10",
    ]

    cookie = settings['COOKIE']  # 带着Cookie向网页发请求
    # 发送给服务器的http头信息，有的网站需要伪装出浏览器头进行爬取，有的则不需要
    headers = {
        'Connection': 'keep - alive',  # 保持链接状态
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        'Accept': 'application/json, text/javascript'
    }
    meta = {
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302],  # 对哪些异常返回进行处理
    }

    # 爬虫的起点
    def start_requests(self):

        # 带着cookie向网站服务器发请求，表明我们是一个已登录的用户
        yield Request(self.start_urls[0], callback=self.parse, cookies=self.cookie,
                        headers=self.headers, meta=self.meta)


    def parse(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html
        @scrapes name
        """
        self.coun = 0
        filename = response.url.split("/")[-2]
        with open(filename, 'wb') as f:
            f.write(response.body)
        # 获取所有区的链接
        for sel in response.xpath('//*[@id="region-nav"]'):
            links = sel.xpath('a/@href').extract()

        self.linklen = len(links)
        # 循环爬取所有区
        for link in links:
            yield Request(str(link), callback=self.nextDistrict, cookies=self.cookie, headers=self.headers)

    # 每个区第一页
    def nextDistrict(self, response):
        item = DPItem()
        self.i = self.i+1
        next = response.xpath("//a[@class='next']/@href").extract()
        for sel in response.xpath('//*[@id="shop-all-list"]/ul/li'):

            item['city'] = sel.xpath("//a[@class='city J-city']/span[2]/text()")[0].extract()
            title = sel.xpath("./div[@class='txt']/div[@class='tit']/a/h4/text()")[0].extract()
            # 不知道为什么这段循环会运行两次，而且第二次返回值为空
            # 所以加一个判断语句忽略第二次
            if title:
                item['title'] = title
                try:
                    item['avgPrice'] = \
                        sel.xpath("./div[@class='txt']/div[@class='comment']/a[@class='mean-price']/b/text()")[0].extract()
                except IndexError as e:
                    self.nullData = self.nullData + 1
                    print('null data: ' + str(self.nullData))
                item['address'] = \
                    sel.xpath("./div[@class='txt']/div[@class='tag-addr']/span[@class='addr']/text()")[0].extract()
                poi = sel.xpath(
                    './div[@class="operate J_operate Hide"]/a[@class="o-map J_o-map"]/@data-poi').extract()
                s = decode(poi[0])
                item['longitude'] = s['lng']
                item['latitude'] = s['lat']
                item['backCateName'] = \
                    sel.xpath("./div[@class='txt']/div[@class='tag-addr']/a[1]/span[@class='tag']/text()")[0].extract()
                #部分店铺没有评分
                # item['avgScore'] = sel.xpath(
                #     "./div[@class='txt']/div[@class='comment']/span[@class='sml-rank-stars sml-str45']/@title")[0].extract()
                yield item
            else:
                print("************")
                print("title is null")
                print("************")
        if(next):
            yield Request(next[0], meta={'item': item}, callback=self.NextPage, cookies=self.cookie, headers=self.headers)
        else:
            print("************")
            print("next is null")
            print("************")

    # 爬取第二页至最后一页
    def NextPage(self,response):
        item = response.meta['item']
        nextPage = response.xpath('//a[@class="next"]/@href').extract()
        self.i = self.i + 1
        print("****************")
        print(" 第 " + str(self.i) + " 页")
        print("****************")
        for sel in response.xpath('//*[@id="shop-all-list"]/ul/li'):

            item['city'] = sel.xpath("//a[@class='city J-city']/span[2]/text()")[0].extract()
            title = sel.xpath("./div[@class='txt']/div[@class='tit']/a/h4/text()")[0].extract()
            # 不知道为什么这段循环会运行两次，而且第二次返回值为空
            # 所以加一个判断语句忽略第二次
            if title:
                item['title'] = title
                try:
                    item['avgPrice'] = \
                        sel.xpath("./div[@class='txt']/div[@class='comment']/a[@class='mean-price']/b/text()")[0].extract()
                except IndexError as e:
                    self.nullData = self.nullData + 1
                    print('null data: ' + str(self.nullData))
                item['address'] = \
                    sel.xpath("./div[@class='txt']/div[@class='tag-addr']/span[@class='addr']/text()")[0].extract()
                poi = sel.xpath(
                    './div[@class="operate J_operate Hide"]/a[@class="o-map J_o-map"]/@data-poi').extract()
                s = decode(poi[0])
                item['longitude'] = s['lng']
                item['latitude'] = s['lat']
                item['backCateName'] = \
                    sel.xpath("./div[@class='txt']/div[@class='tag-addr']/a[1]/span[@class='tag']/text()")[0].extract()
                # 部分店铺没有评分
                # item['avgScore'] = sel.xpath(
                #     "./div[@class='txt']/div[@class='comment']/span[@class='sml-rank-stars sml-str45']/@title")[0].extract()
                yield item
            else:
                print("************")
                print("title is null")
                print("************")
        if(nextPage):
            yield Request(nextPage[0],meta={'item': item}, callback=self.NextPage, cookies=self.cookie, headers=self.headers)
        else:
            self.coun = self.coun + 1
            if self.coun == self.linklen:
                self.city = self.city + 1
                if self.start_urls[self.city]:
                    yield Request(self.start_urls[self.city], callback=self.parse, cookies=self.cookie,
                                  headers=self.headers, meta=self.meta)
            print("************")
            print("nextPage is null")
            print("************")
