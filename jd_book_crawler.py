# coding=utf-8
import re
import os
import sys
import time
import json
import logging
import requests
import urllib.parse
from openpyxl import Workbook
from datetime import datetime
from dotenv import load_dotenv

logging.getLogger().setLevel(logging.DEBUG)
load_dotenv()

CACHE_ONLY=True
SLEEP_DURATION=1

def getContent(url, filename, headers, cookies, shouldRetry=False, validator=None):
    content = None
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            content = file.read()
    elif CACHE_ONLY:
        logging.info(f'missing cache file {filename} skipping {url}')
    else:
        time.sleep(SLEEP_DURATION)
        logging.info(f'fetching {url}')
        content = requests.get(url, headers=headers, cookies=cookies).text
        isValid = validator is not function or validator(content)
        if shouldRetry:
            backoff = SLEEP_DURATION
            while not isValid:
                backoff *= 2
                time.sleep(backoff)
                content = requests.get(url, headers=headers, cookies=cookies).text
                isValid = validator(content)
        if isValid:
            with open(filename, 'w') as file:
                file.write(content)
        else:
            content = None
    return content

def get_all_book_id(page_num, base_url, headers, cookies):
    logging.info("----------Loading lists-------------")
    for page in range(1, page_num+1):
        logging.info(f"----------Page {page}-------------")
        url = base_url+f"&page={page}&s={1+(page-1)*30}&click=0"
        logging.info(url)
        filename = f"lists/{base_url.split('cat=')[1]}_page{page}.html"
        content = getContent(url, filename, headers, cookies, shouldRetry=False, validator=None)
        if content:
            matches = re.findall(r'search000014_log:{wids:\'(.*?)\',uuid', content, re.M)
            try:
                book_ids = matches[0].split(',')
                logging.info(f'found {len(book_ids)} books')
                yield book_ids
            except:
                logging.info("end of list")
                break


def get_book_information(book_ids, headers, cookies, ws):
    logging.info("----------reading book details-------------")
    for book_id in book_ids:
        url = "https://item.jd.com/"+book_id+".html"
        filename = f'books/{book_id}.html'
        def validator(content):
            return len(content) < 300
        content = getContent(url, filename, headers, cookies, shouldRetry=False, validator=validator)
        if content:
            data = []
            data.append(url)
            data.append(f'{book_id}')
            try:
                name = re.findall(r'<div class="sku-name">(.*?)</div>', content, re.DOTALL)[0]
                name = re.sub("\s+", " ", name)
                name = re.sub(r'</?strong>', '', name)
                name = re.sub(r'<img.*?/>', '', name)
                name = re.sub("\s+", " ", name)
                if name[0] == "<":
                    name = name.split(">")[-1]
                data.append(name)
            except:
                data.append("")
            try:
                authors = re.findall(r'a data-name=".*?著', content, re.M)[0]
                data.append(', '.join(re.findall(
                    r'a data-name="(.*?)"', authors, re.M)))
            except:
                data.append("")
            try:
                translators = re.findall(r'著.*?译', content)[0]
                data.append(', '.join(re.findall(
                    r'a data-name="(.*?)"', translators)))
            except:
                data.append("")
            for pattern in [
                r'<li title=(.*?) clstag',
                r'<li title=(.*?)>出版时间',
                r'<li title=(.*?)>包装',
                r'<li title=(.*?)>页数',
                r'<li title=(.*?)>开本',
                r'<li title=(.*?)>用纸',
            ]:
                try:
                    data.append(re.findall(pattern, content)[0])
                except:
                    data.append("")

            data.append(get_price(book_id, headers, cookies))
            yield data

def get_price(book_id, headers, cookies):
    params = {
        'pduid': 'null',
        'pdpin': 'null',
        'pin': 'null',
        'skuIds': f'J_{book_id}',
    }
    content = ""
    try:
        url = f'https://p.3.cn/prices/mgets?' + urllib.parse.urlencode(params)
        filename = f'prices/{book_id}.json'
        def validator(content):
            try:
                data = json.loads(content)
                return bool(len(data) > 0 and 'm' in data[0] and data[0]['m'])
            except:
                return False
        content = getContent(url, filename, headers, cookies, shouldRetry=False, validator=validator)
        data = json.loads(content)
        return data[0]['m']
    except:
        if re.findall('captcha', content):
            logging.info(f'captcha detected fetching {url}, exiting program, content: {content}')
            sys.exit(0)
        logging.info(f'failed to get price for book {url} content: {content}')
        return ""


if __name__ == "__main__":
    start_time = datetime.now().strftime(r'%Y%m%d%H%M%S')
    paths = [
        "lists",
        "books",
        "results",
        "prices",
    ]
    for path in paths:
        os.makedirs(path, exist_ok=True)
    # set headers and cookies
    headers = {
        'User-Agent': os.getenv('USER_AGENT'),
    }
    cookies = {
        "Cookie": os.getenv('COOKIES'),
    }
    

    categories = {
        '经济': '1713,3264',
        '金融与投资': '1713,3265',
        '经济管理大学教材': '1713,11047,11048',
    }
    wb = Workbook()
    ws = wb.active
    filename = f"results/jd_books{start_time}.xlsx"
    ws.append(["链接", "ID", "书名", "作者", "译者", "出版社",
              "出版时间", "包装", "页数", "开本", "用纸", "定价"])
    try:
        for cat_name in categories:
            url = f'https://list.jd.com/list.html?cat={categories[cat_name]}'
            # loop thru pages
            for book_ids in get_all_book_id(20, url, headers, cookies):
                # get book information
                for book_data in get_book_information(book_ids, headers, cookies, ws):
                    book_data.append(cat_name)
                    ws.append(book_data)
    finally:
        wb.save(filename=filename)
