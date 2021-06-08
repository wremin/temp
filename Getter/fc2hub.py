import re
from PIL.ImageFilter import DETAIL, RankFilter
from lxml import etree
import json
from Function.getHtml import get_html

# https://fc2hub.com/search?kw=1760182

def getTitle(html):  # 获取标题
    result = html.xpath('//h1/text()')
    if result:
        result = result[1]
    else:
        result = ''
    return result


def getNum(html):  # 获取番号
    result = html.xpath('//h1/text()')
    if result:
        result = result[0]
    else:
        result = ''
    return result


def getCover(html):  # 获取封面
    result = html.xpath('//a[@data-fancybox="gallery"]/@href')
    if result:
        result = result[0]
    else:
        result = ''
    return result


def getExtraFanart(html):  # 获取剧照
    result = html.xpath('//div[@style="padding: 0"]/a/@href')
    return result


def getTag(html):  # 获取标签
    result = html.xpath('//p[contains(text(), "タグ :")]/a/text()')
    return result

def getOutline(html):  # 获取简介
    result = str(html.xpath('//div[@class="col des"]/text()')).strip('['']').replace("',", '').replace('\\n', '').replace("'", '').replace('・', '')
    return result

def main(number, appoint_url):
    number = number.upper().replace('FC-', '').replace('PPV', '')
    url = 'https://www.google.com/search?q=' + number + ' site:fc2hub.com'
    dic = {}
    real_url = ''
    if appoint_url:
        url = appoint_url
    try:
        htmlcode = get_html(url)
        if str(htmlcode) == 'ProxyError':
            raise TimeoutError
        html = etree.fromstring(htmlcode, etree.HTMLParser()) 
        all_title = html.xpath("//h3/text()")
        if len(all_title):
            web_url = html.xpath('//h3/../@href')[0]
            web_cache_url = html.xpath('//div[@class="action-menu"]/ol/li/a/@href')[0]
            if number in all_title[0]:
                real_url = web_url
            else:
                # 进入第一个结果的网络快照继续尝试查找详情页地址
                minddle_html = get_html(web_cache_url)
                html3 = etree.fromstring(minddle_html, etree.HTMLParser())
                # real_url = html3.xpath("//h4[contains(text()," + number + ")]/../a/@href")
                real_url = html3.xpath("//h4[contains(text(), $number)]/../a/@href", number=number)
                if real_url:
                    real_url = real_url[0]
                else:
                    real_url = ''
        if real_url:
            html_content = get_html(real_url)
            html_info = etree.fromstring(html_content, etree.HTMLParser())
            dic = {
                'title': getTitle(html_info),
                'studio': '',
                'score': '',
                'runtime': '',
                'actor': 'FC2系列',
                'release': '',
                'number': 'FC2-' + number,
                'tag': getTag(html_info),
                'actor_photo': {},
                'cover': getCover(html_info),
                'extrafanart': getExtraFanart(html_info),
                'imagecut': 0,
                'director': '',
                'series': '',
                'publisher': '',
                'year': '',
                'outline': getOutline(html_info),
                'website': real_url,
                'source': 'fc2hub.com',
            }
        else:
            dic = {
                'title': '',
                'website': 'timeout',
            }                
    except TimeoutError:
        dic = {
            'title': '',
            'website': 'timeout',
        }
    except Exception as error_info:
        print('Error in fc2hub.main : ' + str(error_info))
        dic = {
            'title': '',
            'website': '',
        }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )
    return js



# print(main('1613618', ''))
# print(main('1837553', ''))
# print(main('1837589', ""))
# print(main('1760182', ''))
# print(main('1251689', ''))
# print(main('674239', ""))
# print(main('674239', "https://fc2club.com//html/FC2-674239.html"))
