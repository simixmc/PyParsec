import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from contextlib import closing
import pymysql
from pymysql.cursors import DictCursor
import xlwt
import pandas.io.sql as sql

pages = [
    {'link': 'http://www.hantex.ru/produkciya/shariki/shariki-shkh15/?page=', 'count': 4, 'folder': 'shariki-shkh15'},
    {'link': 'http://www.hantex.ru/produkciya/shariki/shariki-95x18/?page=', 'count': 2, 'folder': 'shariki-95x18'},
    {'link': 'http://www.hantex.ru/produkciya/shariki/shariki-12x18n10t/?page=', 'count': 2, 'folder': 'shariki-12x18n10t'},
    {'link': 'http://www.hantex.ru/produkciya/roliki/?page=4', 'count': 4, 'folder': 'roliki'}
]


def pars_1():
    global pages
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.83"
    }
    for item in pages:
        for i in range(item.get('count')):
            link = f'{item.get("link")}{i+1}'
            q = requests.get(url=link, headers=headers)
            with open(f"hantex/{item.get('folder')}/page-{i+1}.html", "w") as file:
                file.write(q.text)
    print('SAVE PAGE DONE!!!')


def get_link_1():
    con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='hantex', cursorclass=DictCursor)
    query = 'SELECT * FROM `categories`'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        folder = f'hantex/{row.get("folder")}'
        count = row.get('count')
        for i in range(count):
            path = f'{folder}/page-{i+1}.html'
            with open(path) as file:
                html = file.read()
            soup = BeautifulSoup(html, "lxml")
            for item in soup.find_all('div', class_='product-layout'):
                link = item.find('a', class_='lazy')['href']
                category_id = row.get('category_id')
                query = f"INSERT INTO `products`(`category_id`, `link`) VALUES (%s, %s)"
                con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='hantex', cursorclass=DictCursor)
                try:
                    with con.cursor() as cur:
                        cur.execute(query, (category_id, link))
                        con.commit()
                finally:
                    con.close()
    print('GET LINK DONE!!!')


def save_products_1():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.83"
    }
    con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='hantex', cursorclass=DictCursor)
    query = 'SELECT * FROM `products`'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        link = row.get('link')
        name = f"{link.split('/')[len(link.split('/'))-2]}.html"
        path = f"hantex/products/{name}"
        q = requests.get(url=link, headers=headers)
        with open(path, "w") as file:
            file.write(q.text)
    print('SAVE PRODUCTS DONE!!!')


def get_item_info_1():
    con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='hantex', cursorclass=DictCursor)
    query = 'SELECT * FROM `products`'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        product_id = row.get('product_id')
        link = row.get('link')
        slug = f"{link.split('/')[len(link.split('/')) - 2]}"
        path = f"hantex/products/{slug}.html"
        with open(path) as file:
            html = file.read()
        soup = BeautifulSoup(html, "lxml")
        title = soup.find('h1', class_='product-title').text
        try:
            img = soup.find('div', class_='product-image').find('img')['data-zoom-image']
        except:
            img = ''
        degree_of_accuracy = soup.find('div', {'id': 'product'}).find('div', class_='form-group').find_all('div', class_='radio')
        doa = []
        for item in degree_of_accuracy:
            doa.append(item.find('label').text.strip())
        degree_of_accuracy = ', '.join(doa)
        props = soup.find('div', {'id': 'tab-specification'}).find('tbody').find_all('tr')
        properties = []
        for item in props:
            td = item.find_all('td')
            prop_name = td[0].text
            prop_value = td[1].text
            properties.append(f'{prop_name} = {prop_value}')
        query = f"UPDATE `products` SET `slug`=%s,`title`=%s,`img`=%s,`degree_of_accuracy`=%s,`properties`=%s WHERE `product_id` = %s"
        con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='hantex', cursorclass=DictCursor)
        try:
            with con.cursor() as cur:
                cur.execute(query, (slug, title, img, degree_of_accuracy, '; '.join(properties), product_id))
                con.commit()
        finally:
            con.close()
    print('GET PRODUCT INFO DONE!!!')


def export_1():
    con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='hantex',
                          cursorclass=DictCursor)
    query = 'SELECT * FROM `categories`'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        category_id = row.get('category_id')
        con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='hantex',
                              cursorclass=DictCursor)
        query = f'SELECT * FROM `products` WHERE `category_id` = {category_id}'
        try:
            with con.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
        finally:
            con.close()
        json_object = json.dumps(rows, indent=4)
        with open(f'hantex/export/{row.get("title")}.json', 'w') as f:
            f.write(json_object)
        # df = sql.read_sql(query, con)
        # df.to_excel(f'hantex/export/{row.get("title")}.xls', index=False)
        # df.to_json(f'hantex/export/{row.get("title")}.json', index=False)
    print('SAVE XLS DONE!!!')


def main():
    # pars_1()
    # get_link_1()
    # save_products_1()
    # get_item_info_1()
    export_1()


if __name__ == '__main__':
    main()
