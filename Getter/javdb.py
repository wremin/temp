import re
from bs4 import BeautifulSoup, SoupStrainer
from lxml import etree
import json
from Function.getHtml import get_html
from Function.getHtml import post_html
import cloudscraper

def getNumber(html):
    result1 = str(html.xpath('//strong[contains(text(),"番號:")]/../span/a/text()')).strip(
        " ['']").replace('_', '-')
    result2 = str(html.xpath('//strong[contains(text(),"ID:")]/../span/a/text()')).strip(
        " ['']").replace('_', '-')
    return str(result2 + result1).strip('+')

    
def getTitle(html):
    try:
        result = str(html.xpath('/html/body/section/div/h2/strong/text()')).strip(" ['']")
        return re.sub('.*\] ', '', result.replace('/', ',').replace('\\xa0', '').replace(' : ', ''))
    except:
        return re.sub('.*\] ', '', result.replace('/', ',').replace('\\xa0', ''))


def getActor(html):
    result1 = html.xpath('//strong[text()="演員:"]/../span/strong[@class="symbol female"][last()]/preceding-sibling::a/text()')
    result2 = html.xpath('//strong[text()="Actor(s):"]/../span/strong[@class="symbol female"][last()]/preceding-sibling::a/text()')
    return result1 + result2


def getActorPhoto(actor):  # //*[@id="star_qdt"]/li/a/img
    d = {}
    for i in actor:
        if ',' not in i or ')' in i:
            p = {i: ''}
            d.update(p)
    return d


def getStudio(html):
    result1 = str(html.xpath('//strong[contains(text(),"片商:")]/../span/a/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"Maker:")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getPublisher(html):
    result1 = str(html.xpath('//strong[contains(text(),"發行:")]/../span/a/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"Publisher:")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getRuntime(html):
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"Duration:")]/../span/text()')).strip(" ['']")
    return str(result1 + result2).replace(' 分鍾', '').replace(' minute(s)', '')


def getSeries(html):
    result1 = str(html.xpath('//strong[contains(text(),"系列:")]/../span/a/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"Series:")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')

def getRelease(html):
    result1 = str(html.xpath('//strong[contains(text(),"日期:")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"Released Date:")]/../span/text()')).strip(" ['']")
    return str(result1 + result2).strip('+')

def getYear(getRelease):
    try:
        result = str(re.search('\d{4}', getRelease).group())
        return result
    except:
        return getRelease


def getTag(html):
    result1 = str(html.xpath('//strong[contains(text(),"類別:")]/../span/a/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"Tags:")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace(",\\xa0", "").replace("'", "").replace(' ', '').replace(',,',
                                                                                                             '').lstrip(
        ',')


def getCover_small(html, count):
    result = html.xpath("//div[@class='grid-item column']/a[@class='box']/div/img/@data-src")[count]
    if 'thumbs' not in result:
        result = html.xpath("//div[@class='grid-item column']/a[@class='box']/div/img/@src")[count]
    if not 'https' in result:
        result = 'https:' + result
    return result


def getCover(html):
    try:
        result = str(html.xpath("//img[@class='video-cover']/@src")[0]).strip(" ['']")
    except:
        result = ''
    return result


def getExtraFanart(html):  # 获取封面链接
    extrafanart_list = html.xpath("//div[@class='tile-images preview-images']/a[@class='tile-item']/@href")
    return extrafanart_list

def getDirector(html):
    result1 = str(html.xpath('//strong[contains(text(),"導演:")]/../span/a/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"Director:")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getScore(html):
    result = str(html.xpath("//span[@class='score-stars']/../text()")).strip(" ['']")
    try:
        score = re.findall(r'(\d{1}\..+)分', result)[0]
    except:
        score = ''
    return score


def getOutlineScore(number):  # 获取简介
    outline = ''
    score = ''
    try:
        response = post_html("https://www.jav321.com/search", query={"sn": number})
        detail_page = etree.fromstring(response, etree.HTMLParser())
        outline = str(detail_page.xpath('/html/body/div[2]/div[1]/div[1]/div[2]/div[3]/div/text()')).strip(" ['']")
        score = detail_page.xpath('//img/@data-original')[0][-6:7]
        score = str(float(score) / 10.0)
    except Exception as error_info:
        print('Error in javdb.getOutlineScore : ' + str(error_info))
        outline = ''
        score = ''
    return outline, score


def main(number, appoint_url, isuncensored=False):
    try:
        result_url = ''
        if appoint_url == '':
            url_search = 'https://javdb.com/search?q=' + number + '&f=all&locale=zh'
            # ========================================================================搜索番号
            scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
            # # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
            html_search = scraper.get(url_search).text.replace(u'\xa0', u' ')
            # html_search = get_html('https://javdb9.com/search?q=' + number + '&f=all').replace(u'\xa0', u' ')
            if str(html_search) == 'ProxyError':
                raise TimeoutError
            html = etree.fromstring(html_search, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
            # print(etree.tostring(html,encoding="utf-8").decode())
            CloudFlare5 = str(html.xpath('//title/text()')).strip(" ['']")
            if CloudFlare5 == 'Please Wait... | Cloudflare':
                raise Exception('SearchCloudFlare')
            counts = len(html.xpath(
                '//div[@id=\'videos\']/div[@class=\'grid columns\']/div[@class=\'grid-item column\']'))
            if counts == 0:
                raise Exception('Movie Data not found in javdb.main! No search results!')
            # ========================================================================遍历搜索结果，找到需要的番号所在URL
            count = 1
            number_get = ''
            movie_found = 0
            for count in range(1, counts + 1):
                number_get = html.xpath(
                    '//div[@id=\'videos\']/div[@class=\'grid columns\']/div[@class=\'grid-item column\'][' + str(
                        count) + ']/a[@class=\'box\']/div[@class=\'uid\']/text()')[0]
                if number_get.upper() == number.upper():
                    movie_found = 1
                    break
            if movie_found == 0:
                raise Exception('Movie Data not found in javdb.main! No matched result!')
            result_url = 'https://javdb.com' + html.xpath('//*[@id="videos"]/div/div/a/@href')[count - 1] + '?locale=zh'
        else:
            result_url = appoint_url

        # ========================================================================请求、判断结果
        # html_info = get_html(result_url).replace(u'\xa0', u' ')
        scraper = cloudscraper.CloudScraper()
        html_info = scraper.get(result_url).text
        if str(html_info) == 'ProxyError':
            raise TimeoutError
        # ========================================================================获取评分、简介
        html_detail = etree.fromstring(html_info, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        CloudFlare5 = str(html_detail.xpath('//title/text()')).strip(" ['']")
        if CloudFlare5 == 'Please Wait... | Cloudflare':
            raise Exception('DetailCloudFlare')
        imagecut = 1
        outline = ''
        if isuncensored and (re.match('^\d{4,}', number) or re.match('n\d{4}', number)):  # 无码，收集封面、评分
            imagecut = 0
            score = getScore(html_detail)
        elif 'HEYZO' in number.upper():  # HEYZO，收集封面、评分、简介
            imagecut = 0
            outline, score = getOutlineScore(number)
        else:  # 其他，收集评分、简介
            outline, score = getOutlineScore(number)
            score = getScore(html_detail)
        # ========================================================================收集信息
        actor = getActor(html_detail)
        if len(actor) == 0 and 'FC2-' in number.upper():
            actor.append('FC2-NoActor')
        release = getRelease(html_detail)
        dic = {
            'number': number.upper(),
            'title': getTitle(html_detail).replace('中文字幕', '').replace('無碼', '').replace("\\n", '').replace('_','-').replace(number.upper(), '').replace(number, '').strip().replace(' ', '-').replace('--', '-'),
            'actor': str(actor).strip(" [',']").replace('\'', ''),
            'outline': outline,
            'release': release,
            'year': getYear(release),
            'runtime': getRuntime(html_detail),
            'score': score,
            'series': getSeries(html_detail),
            'director': getDirector(html_detail),
            'publisher': getPublisher(html_detail),
            'studio': getStudio(html_detail),
            'cover': getCover(html_detail),
            'cover_small': '',
            'extrafanart': getExtraFanart(html_detail),
            'actor_photo': getActorPhoto(actor),
            'imagecut': imagecut,
            'tag': getTag(html_detail),
            'website': result_url.replace('?locale=zh', ''),
            'source': 'javdb.com',
        }

    except TimeoutError:
        dic = {
            'title': '',
            'website': 'timeout',
        }
    except Exception as error_info:
        print('Error in javdb.main : ' + str(error_info))
        if str(error_info) == 'SearchCloudFlare':
            dic = {
                'title': '',
                'website': 'SearchCloudFlare',
            }
        elif str(error_info) == 'DetailCloudFlare':
            dic = {
                'title': '',
                'website': 'DetailCloudFlare',
            }
        else:
            dic = {
                'title': '',
                'website': '',
            }
    except:
        pass

    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js


def main_us(number, appoint_url=''):
    try:
        result_url = ''
        if appoint_url:
            result_url = appoint_url
        else:
            # ========================================================================搜索番号
            url_search = 'https://javdb.com/search?q=' + number + '&f=all&locale=zh'
            scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
            # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
            htmlcode = scraper.get(url_search).text
            # htmlcode = get_html('https://javdb.com/search?q=' + number + '&f=all').replace(u'\xa0', u' ')
            if str(htmlcode) == 'ProxyError':
                raise TimeoutError
            html = etree.fromstring(htmlcode, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
            counts = len(html.xpath(
                '//div[@id=\'videos\']/div[@class=\'grid columns\']/div[@class=\'grid-item column\']'))
            if counts == 0:
                raise Exception('Movie Data not found in javdb.main_us!')
            # ========================================================================遍历搜索结果，找到需要的番号所在URL
            number_series = number.split('.')[0]
            number_date = '20' + number.replace(number_series, '').strip('.')
            number_date = number_date.replace('.', '-')
            count = 1
            movie_found = 0
            for count in range(1, counts + 1):  # 遍历搜索结果，找到需要的番号
                series_get = html.xpath(
                    '//div[@id=\'videos\']/div[@class=\'grid columns\']/div[@class=\'grid-item column\'][' + str(
                        count) + ']/a[@class=\'box\']/div[@class=\'uid2\']/text()')[0]
                date_get = html.xpath(
                    '//div[@id=\'videos\']/div[@class=\'grid columns\']/div[@class=\'grid-item column\'][' + str(
                        count) + ']/a[@class=\'box\']/div[@class=\'meta\']/text()')[0]
                if re.search('\d{4}-\d{1,2}-\d{1,2}', date_get):
                    date_get = re.findall('\d{4}-\d{1,2}-\d{1,2}', date_get)[0]
                series_get = series_get.replace(' ', '')
                if (series_get.upper() == number_series.upper() or series_get.replace('-', '').upper() == number_series.upper()) \
                        and number_date == date_get:
                    movie_found = 1
                    break
            if movie_found == 0:
                raise Exception('Movie Data not found in javdb.main_us!')
            result_url = 'https://javdb.com' + html.xpath('//*[@id="videos"]/div/div/a/@href')[count - 1]
        # ========================================================================请求、判断结果
        # html_info = get_html(result_url).replace(u'\xa0', u' ')
        scraper = cloudscraper.create_scraper()
        html_detail = scraper.get(result_url).text
        html_info = etree.fromstring(html_detail, etree.HTMLParser())  # //table/tr[1]/td[1]/text()

        if str(html_info) == 'ProxyError':
            raise TimeoutError
        # ========================================================================收集信息
        number = getNumber(html_info)
        actor = getActor(html_info)
        release = getRelease(html_info)
        dic = {
            'number': number,
            'title': getTitle(html_info).replace('中文字幕', '').replace("\\n", '').replace('_', '-').replace(number,
                                                                                                          '').strip(),
            'actor': str(actor).strip(" [',']").replace('\'', ''),
            'outline': '',
            'release': release,
            'year': getYear(release),  # str(re.search('\d{4}',getRelease(htmlcode)).group()),
            'runtime': getRuntime(html_info),
            'score': getScore(html_info),
            'series': getSeries(html_info),
            'director': getDirector(html_info),
            'publisher': getPublisher(html_info),
            'studio': getStudio(html_info),
            'cover': getCover(html_info),
            'cover_small': '',
            'extrafanart': getExtraFanart(html_info),
            'actor_photo': getActorPhoto(actor),
            'imagecut': 0,
            'tag': getTag(html_info),
            'website': result_url.replace('?locale=zh', ''),
            'source': 'javdb.com',
        }
    except TimeoutError:
        dic = {
            'title': '',
            'website': 'timeout',
        }
    except Exception as error_info:
        print('Error in javdb.main_us : ' + str(error_info))
        dic = {
            'title': '',
            'website': '',
        }
    except:
        pass

    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js


'''
print(main('abs-141'))
print(main('HYSD-00083'))
print(main('IESP-660'))
print(main('n1403'))
print(main('GANA-1910'))
print(main('heyzo-1031'))
print(main_us('x-art.19.11.03'))
print(main('032020-001'))
print(main('S2M-055'))
print(main('LUXU-1217'))
'''
# print(main('SSIS-001', ''))
# print(main('SSIS-090', ''))
# print(main('SNIS-016', ''))
# print(main('HYSD-00083', ''))
# print(main('IESP-660', ''))
# print(main('n1403', ''))
# print(main('GANA-1910', ''))
# print(main('heyzo-1031', ''))
# print(main_us('x-art.19.11.03'))
# print(main('032020-001', ''))
# print(main('S2M-055', ''))
# print(main('LUXU-1217', ''))
# print(main_us('x-art.19.11.03', ''))
