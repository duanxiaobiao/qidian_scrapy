import time
from io import BytesIO

import requests
from fontTools.ttLib import TTFont

import requests, time, re, pprint
from fontTools.ttLib import TTFont
from io import BytesIO
from lxml import etree

def get_font(url):
    """
    获取源代码中数字信息与英文单词之间的映射关系
    :param url: <str> 网页源代码中的字体地址
    :return: <dict> 网页字体映射关系
    """
    time.sleep(1)
    response = requests.get(url)
    font = TTFont(BytesIO(response.content))
    web_font_relation = font.getBestCmap()
    font.close()
    return web_font_relation


#在fontcreator中查看此ttf文件中英文单词与阿拉伯数字的映射关系，写入字典
python_font_relation = {
    'one':1,
    'two':2,
    'three':3,
    'four':4,
    'five':5,
    'six':6,
    'seven':7,
    'eight':8,
    'nine':9,
    'zero':0,
    'period':'.'
}

def get_html_info(url):
    """
    解析网页，获取文字文件的地址和需要解码的数字信息
    :param url: <str> 需要解析的网页地址
    :return:    <str> 文字文件ttf的地址
                <list> 反爬的数字，一维列表
    """
    headers = {
        'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    html_data = requests.get(url, headers=headers)
    # 获取网页的文字ttf文件的地址
    url_ttf_pattern = re.compile('<style>(.*?)\s*</style>',re.S)

    fonturl = re.findall(url_ttf_pattern,html_data.text)[0]

    url_ttf = re.search('woff.*?url.*?\'(.+?)\'.*?truetype', fonturl).group(1)

    # 获取所有反爬的数字
    word_pattern = re.compile('</style><span.*?>(.*?)</span>', re.S)#制定正则匹配规则，匹配所有<span>标签中的内容

    numberlist = re.findall(word_pattern, html_data.text)

    return url_ttf,numberlist


def get_encode_font(numberlist,url):
    """
    把源代码中的数字信息进行2次解码
    :param numberlist: <list> 需要解码的一维数字信息
    :return:
    """
    web_font_relation = get_font(get_html_info(url)[0])
    data = []
    for i in numberlist:
        fanpa_data = ''
        words = i.split(';')
        for k in range(0,len(words)-1):
            words[k] = words[k].strip('&#')
            words[k] = str(python_font_relation[web_font_relation[int(words[k])]])
            fanpa_data += words[k]
        data.append(fanpa_data)
    return data
