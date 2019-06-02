# -*- coding: utf-8 -*-
import re

import scrapy

from qidian.items import QidianItem
from qidian.spiders.solve_font import get_html_info, get_font, get_encode_font


class QidianspiderSpider(scrapy.Spider):
    name = 'qidianspider'
    # allowed_domains = ['www.qidian.com']
    start_urls = ['http://www.qidian.com/']

    def parse(self, response):
        # 小说类型列表
        novel_type_list =response.xpath('//dl[@class ="cf"]//dd//span//i/text()').extract()
        #小说类型URL列表
        novel_type_url_list=response.xpath('//dl[@class ="cf"]//dd//a/@href').extract()
        #小说类型和URL只选取前12种.如：玄幻，奇幻，武侠，仙侠，都市，现实，军事，历史，游戏，体育，科幻，悬疑灵异(因网页结构不同)
        for novel_type ,novel_type_url in zip(novel_type_list[0:-2],novel_type_url_list[0:-2]):
            item =QidianItem()
            item['novel_type'] =novel_type
            #小说分类页url
            URL="https://www.qidian.com"+novel_type_url
            yield scrapy.Request(
                URL,
                callback=self.parse_kind_parse,
                meta={'item':item}
            )
     #分类页解析函数
    # 类似于:  https://www.qidian.com/xuanhuan
    def parse_kind_parse(self,response):
        #接收item
        item =response.meta['item']
        # 分类页小说类型名字列表
        novel_kind_names =response.xpath('//div[@class="sub-type-wrap"]//div[@class ="box-center cf"]//a/text()').extract()
        #分类页小说类型URL列表
        novel_kind_urls =response.xpath('//div[@class="sub-type-wrap"]//div[@class ="box-center cf"]//a/@href').extract()
        for novel_kind_url ,novel_kind_name in zip  (novel_kind_urls,novel_kind_names):
            item['novel_kind'] =novel_kind_name
            # yield item
            #如果对应的是(xx排行)的URL ,例如:https://www.qidian.com/rank?chn=21
            if novel_kind_url.split('/')[-1].split('?')[0]=='rank':
                novel_kind_url ="https://www.qidian.com/"+novel_kind_url.split('/')[-1]
                yield scrapy.Request(
                    novel_kind_url,
                    callback=self.paihang_parse,
                    meta={'item':item}
                )
            #否则对应的就是类似url：https://www.qidian.com/all?chanId=21&subCateId=58
            else:
                novel_kind_url ="https://www.qidian.com/"+novel_kind_url.split('/')[-1]
                yield scrapy.Request(
                    novel_kind_url,
                    callback=self.detail_url_parse,
                    meta={'item':item}
                )

    #类型名称为：(xx排行)的解析函数
    def paihang_parse(self,response):
        item =response.meta['item']
        paihang_divided_url =response.xpath('//ul[@class ="list_type_detective"]//li//a/@href').extract()
        for divided_url  in paihang_divided_url:
            url ='https://www.qidian.com/rank/'+divided_url.split('/')[-1]
            yield scrapy.Request(
                url,
                callback=self.detail_url_parse1,
                meta={'item':item}
            )
    #类似于  https://www.qidian.com/all?chanId=21&subCateId=8打开的页面 的解析函数
    def detail_url_parse(self,response):
        item =response.meta['item']
        url_list =response.xpath('//div[@class ="book-img-text"]//li//div[@class ="book-mid-info"]//h4/a/@href').extract()
        for url in url_list:
            detail_url ="https://book.qidian.com/"+url.split('/')[-2]+'/'+url.split('/')[-1]
            try:
                yield scrapy.Request(
                    detail_url,
                    callback =self.detail_parse,
                    meta={'item':item},
                )
            except:
                print('ERROR')
        #下一页
        next_urls =response.xpath('//a[@class="lbf-pagination-next "]/@href').extract()
        if next_urls !='javascript:;':
            for next_url in next_urls:
                next_url ='https://'+next_url.strip('//')
                print(next_url)
                yield scrapy.Request(
                    next_url,
                    callback=self.detail_url_parse,
                    meta ={'item':item}
                )
    #类似于 https://www.qidian.com/rank?chn=21打开之后的页面，在这只取热门作品排行和新书排行的url.
    def detail_url_parse1(self,response):
        item = response.meta['item']
        url_list = response.xpath(
            '//div[@class ="book-img-text"]//li//div[@class ="book-mid-info"]//h4/a/@href').extract()
        for url in url_list:
            detail_url = "https://book.qidian.com/" + url.split('/')[-2] + '/' + url.split('/')[-1]
            try:
                yield scrapy.Request(
                    detail_url,
                    callback=self.detail_parse,
                    meta={'item': item},
                )
            except:
                print('ERROR')
        #下一页
        next_url_header = response.url+'&page='
        for i in range(2,30):
            next_url =next_url_header +str(i)
            yield scrapy.Request(
                next_url,
                callback=self.detail_url_parse,
                meta={'item': item}
            )
    #详细页的解析函数.
    def detail_parse(self,response):
        item =response.meta['item']
        #名字
        name = response.xpath('//div[@class ="book-info "]/h1/em/text()').extract_first()
        #作者
        author =response.xpath('//div[@class ="book-info "]/h1/span/a/text()').extract_first()
        #小说标签
        novel_tag =response.xpath('//p[@class ="tag"]//a[2]/text()').extract()
        #小说简介
        novel_intro =response.xpath('//div[@class ="book-intro"]/p/text()').extract_first().replace('\r','').replace(' ','').replace('\u3000','')
        #----------------------------------------------------------------------
        # get_html_info(response.url)
        # web_font_relation = get_font(get_html_info(response.url)[0])
        # data =get_encode_font(get_html_info(response.url)[1],response.url)
        #小说字数
        # novel_word_count =data[0]
        #  item['novel_word_count'] =novel_word_count
        #-----------------------------------------------------------------------
        #获取小说字数的部分，由于需要将拿到的‘方框’进行解析，调取了solve_font.py的函数。
        #如果开启，爬取速度会变慢。 注释：solve_font.py 中的解析函数是我拿取：https://blog.csdn.net/qq_35741999/article/details/82018049的代码。
                                                                    #已注明出处。
        item['name'] = name
        item['author'] = author
        item['novel_tag'] =novel_tag
        item['novel_intro'] =novel_intro
        yield item


