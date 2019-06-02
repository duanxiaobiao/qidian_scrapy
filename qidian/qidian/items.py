# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QidianItem(scrapy.Item):
    # define the fields for your item here like:
    #novel :小说
    #小说类型
    novel_type =scrapy.Field()
    #小说分类
    novel_kind =scrapy.Field()
    #小说名字
    name = scrapy.Field()
    #作者
    author =scrapy.Field()
    #小说标签
    novel_tag =scrapy.Field()
    #小说简介
    novel_intro =scrapy.Field()
    #小说字数
    # novel_word_count =scrapy.Field()


