# coding! utf-8
import scrapy
import json
from scrapy.linkextractors import LinkExtractor
#from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from project.items import YYItem
import re
import time

title_dict = {
    'jincai': '金采网',
    'zhongyang': '中国政府采购网中央公告',
    'difang': '中国政府采购网地方公告',
    'yidong': '中国移动',
    'liantong': '中国联通',
    'jianyu': '剑鱼网',
    'dongfang': '中国东方航空采购招标网',
    'nanfang': '中国南方电网',
    'dianli': '中国电力招标网',
    'cgzb': '中国采购与招标网',
    'center': '中钢采招网',
    'huobiao': '火标网',
    'jundui': '全军武器装备采购信息网军队公告',
    'jungong': '全军武器装备采购信息网军工公告'
}
keys = list(title_dict.keys())

class Jincai_spider(scrapy.Spider):
    name = keys[0]
    title = title_dict[name]
    # 允许的域名
    allowed_domains = ['www.cfcpn.com']
    # 爬虫的起始url
    # start_urls = ['http://www.cfcpn.com/jcw/noticeinfo/noticeInfo/dataNoticeList']
    base_url = 'http://www.cfcpn.com/jcw/sys/index/goUrl?url=modules/sys/login/detail&column=undefined&searchVal='
    def start_requests(self):
        url = 'http://www.cfcpn.com/jcw/noticeinfo/noticeInfo/dataNoticeList'
        for i in range(1, 5):
            # 向队列中加入post请求
            params = {
                'noticeType': '1',
                'pageSize': '10',
                'pageNo': str(i),
                'noticeState': '1',
                'isValid': '1',
                'orderBy': 'publish_time desc'
            }
            yield scrapy.FormRequest(url=url, formdata=params, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.text)
        if res.get('result'):
            for each in res.get('rows'):
                print(each)
                item = YYItem()
                item['name'] = each['noticeTitle']
                item['time'] = each['publishTime'][:-5]
                item['unit'] = each['noticeSource']
                item['address'] = self.base_url + each['id']
                item['sources'] = self.title
                yield item


class Zhongyang_Spider(scrapy.Spider):
    name = keys[1]
    title = title_dict[name]
    # 允许的域名
    allowed_domains = ['www.ccgp.gov.cn']
    offset = 0
    base_url = 'http://www.ccgp.gov.cn/cggg/zygg/'
    # 爬虫的起始url
    start_urls = [base_url + 'index.htm']

    def parse(self, response):
        items = response.xpath('//div[@class="vF_detail_relcontent_lst"]/ul/li')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('.//a/text()').extract()[0]
            item['time'] = each.xpath('.//em[2]/text()').extract()[0]
            item['unit'] = each.xpath('.//em[last()]/text()').extract()[0]
            item['address'] = self.base_url + each.xpath('.//a/@href').extract()[0].replace('./', '')
            item['sources'] = self.title
            # 将数据发送给管道
            yield item
        if self.offset < 5:
            self.offset += 1
        # 将请求重新发送给调度器
        yield scrapy.Request(self.base_url + 'index_' + str(self.offset) + '.htm', callback=self.parse)


class Difang_Spider(scrapy.Spider):
    name = keys[2]
    title = title_dict[name]
    allowed_domains = ['www.ccgp.gov.cn']
    offset = 0
    base_url = 'http://www.ccgp.gov.cn/cggg/dfgg/'
    start_urls = [base_url + 'index.htm']

    def parse(self, response):
        items = response.xpath('//div[@class="vF_detail_relcontent_lst"]/ul/li')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('.//a/text()').extract()[0]
            item['time'] = each.xpath('.//em[2]/text()').extract()[0]
            item['unit'] = each.xpath('.//em[last()]/text()').extract()[0]
            item['address'] = self.base_url + each.xpath('.//a/@href').extract()[0].replace('./', '')
            item['sources'] = self.title
            yield item
        if self.offset < 5:
            self.offset += 1
        yield scrapy.Request(self.base_url + 'index_' + str(self.offset) + '.htm', callback=self.parse)


class Yidong_Spider(scrapy.Spider):
    name = keys[3]
    title = title_dict[name]
    allowed_domains = ['b2b.10086.cn']
    base_url = 'https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id='
    custom_settings = {
        'SOME_SETTING': 'some value',
    }
    def start_requests(self):
        url = 'https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=2'
        for i in range(1, 5):
            # 向队列中加入post请求
            params = {
                'page.currentPage': str(i),
                'page.perPageSize': '20',
                'noticeBean.sourceCH': '',
                'noticeBean.source': '',
                'noticeBean.title': '',
                'noticeBean.startDate': '',
                'noticeBean.endDate': '',
                '_qt': 'TYjlTMkjY2kzYyETN3UjMlRGM5kTYiFmNzkzNkNzMxQ'
            }
            yield scrapy.FormRequest(url=url, formdata=params, callback=self.parse)

    def parse(self, response):
        items = response.xpath('//table/tr/tr')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('.//td[2]/text()').extract()[0]
            item['time'] = each.xpath('.//td[last()]/text()').extract()[0]
            item['unit'] = each.xpath('.//td[0]/text()').extract()[0]
            item['address'] = self.base_url + each.xpath('.//@onclick').extract()[0]
            item['sources'] = self.title
            yield item


class Liantong_Spider(scrapy.Spider):
    name = keys[4]
    title = title_dict[name]
    allowed_domains = ['www.chinaunicombidding.cn']
    base_url = 'https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id='

    def start_requests(self):
        url = 'https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=2'
        for i in range(1, 5):
            # 向队列中加入post请求
            params = {
                'page.currentPage': str(i),
                'page.perPageSize': '20',
                'noticeBean.sourceCH': '',
                'noticeBean.source': '',
                'noticeBean.title': '',
                'noticeBean.startDate': '',
                'noticeBean.endDate': '',
                '_qt': 'TYjlTMkjY2kzYyETN3UjMlRGM5kTYiFmNzkzNkNzMxQ'
            }
            yield scrapy.FormRequest(url=url, formdata=params, callback=self.parse)

    def parse(self, response):
        items = response.xpath('//table/tr/tr')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('.//td[2]/text()').extract()[0]
            item['time'] = each.xpath('.//td[last()]/text()').extract()[0]
            item['unit'] = each.xpath('.//td[0]/text()').extract()[0]
            item['address'] = self.base_url + each.xpath('.//@onclick').extract()[0]
            item['sources'] = self.title
            yield item


class Jianyu_Spider(scrapy.Spider):
    name = keys[5]
    title = title_dict[name]
    allowed_domains = ['www.jianyu360.com']
    base_url = 'https://www.jianyu360.com/article/content/'
    def start_requests(self):
        url = 'https://www.jianyu360.com/jylab/supsearch/getNewBids'
        for i in range(1, 5):
            yield scrapy.FormRequest(url=url, formdata={'pageNumber': str(i)}, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.text)
        if res.get('list'):
            for each in res.get('list'):
                item = YYItem()
                item['name'] = each['title']
                item['time'] = time.strftime("%Y-%m-%d %H:%M", time.localtime(each['publishtime']))
                item['unit'] = '略'
                item['address'] = self.base_url + each['_id'] + '.html'
                item['sources'] = self.title
                yield item


class Dongfang_Spider(scrapy.Spider):
    name = keys[6]
    title = title_dict[name]
    allowed_domains = ['caigou.ceair.com']
    base_url = 'https://caigou.ceair.com/portal/portal/noticeDetails?id='

    def start_requests(self):
        url = 'https://caigou.ceair.com/portal/portal/sysInfoList?siteFlag=false'
        for i in range(1, 2):
            params = {
                'pageNo': str(i),
                'sourceType': '1',
                'pageSize': '10'
            }
            yield scrapy.FormRequest(url=url, formdata=params, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.text)
        data = res.get('param1')
        if data:
            for each in data.get('result'):
                item = YYItem()
                item['name'] = each['title']
                item['time'] = each['publishTime'][:-3]
                item['unit'] = '略'
                item['address'] = self.base_url + each['id']
                item['sources'] = self.title
                yield item


class Nanfang_Spider(scrapy.Spider):
    name = keys[7]
    title = title_dict[name]
    allowed_domains = ['www.bidding.csg.cn']
    offset = 0
    base_url = 'http://www.bidding.csg.cn/zbcg/index'
    start_urls = [base_url + '.jhtml']

    def parse(self, response):
        items = response.xpath('//div[@class="W750 Right"]/div/ul/li')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('.//a/text()').extract()[0]
            item['time'] = each.xpath('.//span/text()').extract()[0] + " 00:00"
            item['unit'] = each.xpath('./text()').extract()[0]
            item['address'] = 'http://www.bidding.csg.cn' + each.xpath('.//a/@href').extract()[0]
            item['sources'] = self.title
            yield item
        if self.offset < 2:
            self.offset += 1
        yield scrapy.Request(self.base_url + '_' + str(self.offset) + '.jhtml', callback=self.parse)


class Dianli_Spider(scrapy.Spider):
    name = keys[8]
    title = title_dict[name]
    allowed_domains = ['www.bidding.csg.cn']
    start_urls = ['https://www.dlzb.com/zb/']

    def parse(self, response):
        items = response.xpath('//*[@id="con_two_1"]/ul/li')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('./a/text()').extract()[0]
            item['time'] = '2020-' + each.xpath('.//span[1]/text()').extract()[0] + " 00:00"
            item['unit'] = each.xpath('.//span/a/text()').extract()[0]
            item['address'] = each.xpath('./a/@href').extract()[0]
            item['sources'] = self.title
            yield item


class Cgzb_Spider(scrapy.Spider):
    name = keys[9]
    title = title_dict[name]
    allowed_domains = ['www.chinabidding.cn']
    offset = 1
    base_url = 'https://www.chinabidding.cn/zbxx/zbgg/'
    start_urls = [base_url + '1.html']

    def parse(self, response):
        items = response.xpath('//*[@id="list"]/tbody/tr')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('//td[@class="td_1"]/a/text()').extract()[0]
            item['time'] = each.xpath('./td[last()]/text()').extract()[0] + ' 00:00'
            item['unit'] = '略'
            item['address'] = 'https://www.chinabidding.cn' + each.xpath('//td[@class="td_1"]/a/@href').extract()[0]
            item['sources'] = self.title
            yield item
        if self.offset < 5:
            self.offset += 1
        yield scrapy.Request(self.base_url + str(self.offset) + '.html', callback=self.parse)


class Center_Spider(scrapy.Spider):
    name = keys[10]
    title = title_dict[name]
    allowed_domains = ['www.bidcenter.com.cn']
    offset = 1
    base_url = 'https://www.bidcenter.com.cn/zbpage-1-'
    start_urls = [base_url + '1.html']

    def parse(self, response):
        items = response.xpath('//*[@id="searchcontent"]/ul/li')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('.//div/a[last()]/text()').extract()[0]
            item['time'] = each.xpath('.//div[@class="s_c_l_right"]/text()').extract()[1].split('\r')[0].replace('/', '-') + ' 00:00'
            item['unit'] = '略'
            item['address'] = 'https://www.bidcenter.com.cn' + each.xpath('.//div/a[last()]/@href').extract()[0]
            item['sources'] = self.title
            yield item
        if self.offset < 5:
            self.offset += 1
        yield scrapy.Request(self.base_url + str(self.offset) + '.html', callback=self.parse)


class Huobiao_Spider(scrapy.Spider):
    name = keys[11]
    title = title_dict[name]
    allowed_domains = ['www.huobiao.cn']
    offset = 1
    base_url = 'http://www.huobiao.cn/bid/page/'
    start_urls = [base_url + '1.html']

    def parse(self, response):
        items = response.xpath('//a[@class="item-blue"]')
        for each in items:
            item = YYItem()
            item['name'] = each.xpath('.//div/div/div[1]/text()').extract()[0]
            item['time'] = each.xpath('.//div/div/div[last()]/text()').extract()[1][1:12] + '00:00'
            item['unit'] = '略'
            item['address'] = 'http://www.huobiao.cn' + each.xpath('./@href').extract()[0]
            item['sources'] = self.title
            yield item
        if self.offset < 5:
            self.offset += 1
        yield scrapy.Request(self.base_url + str(self.offset) + '.html', callback=self.parse)


class Jundui_Spider(scrapy.Spider):
    name = keys[12]
    title = title_dict[name]
    allowed_domains = ['www.weain.mil.cn']
    base_url = 'http://www.weain.mil.cn/api/front/list/cggg/list?LMID=1149231276155707394&pageNo='
    offset = 1
    start_urls = [base_url + str(offset)]

    def parse(self, response):
        res = json.loads(response.text)
        items = res.get('list', {}).get('contentList')
        if items:
            for each in items:
                item = YYItem()
                item['name'] = each['nonSecretTitle']
                item['time'] = each['publishTime'][:-3]
                item['unit'] = '略'
                item['address'] = 'http://www.weain.mil.cn' + each['pcUrl']
                item['sources'] = self.title
                yield item
        if self.offset < 5:
            self.offset += 1
        yield scrapy.Request(self.base_url + str(self.offset), callback=self.parse)


class Jungong_Spider(scrapy.Spider):
    name = keys[13]
    title = title_dict[name]
    allowed_domains = ['www.weain.mil.cn']
    base_url = 'http://www.weain.mil.cn/api/front/list/cggg/list?LMID=1149231318006472705&pageNo='
    offset = 1
    start_urls = [base_url + str(offset)]

    def parse(self, response):
        res = json.loads(response.text)
        items = res.get('list', {}).get('contentList')
        if items:
            for each in items:
                item = YYItem()
                item['name'] = each['nonSecretTitle']
                item['time'] = each['publishTime'][:-3]
                item['unit'] = '略'
                item['address'] = 'http://www.weain.mil.cn' + each['pcUrl']
                item['sources'] = self.title
                yield item
        if self.offset < 5:
            self.offset += 1
        yield scrapy.Request(self.base_url + str(self.offset), callback=self.parse)
