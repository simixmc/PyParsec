import os
import requests
from bs4 import BeautifulSoup
from contextlib import closing
import pymysql
from pymysql.cursors import DictCursor
import xlwt
import pandas.io.sql as sql


def catalog_page():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.83'
    }
    q = requests.get(url='https://olimp-parketa.ru/catalog/', headers=headers)
    if not os.path.exists('data'):
        os.mkdir("data")
    with open("data/catalog.html", "w") as file:
        file.write(q.text)


def pars_catalog_page():
    with open("data/catalog.html") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    for item in soup.find('div', class_='category__tabs-cont').find_all('a', class_='part'):
        link = item.get('href')
        name = item.find('p').text
        query = f"INSERT INTO categories (`name`, `url`) VALUES (%s, %s)"
        con = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            db='pars_poly',
            cursorclass=DictCursor
        )
        try:
            with con.cursor() as cur:
                cur.execute(query, (name, link))
                con.commit()
        finally:
            con.close()


def subcat_page():
    if not os.path.exists('data/catalog'):
        os.mkdir("data/catalog")
    con = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root',
        db='pars_poly',
        cursorclass=DictCursor
    )
    query = 'SELECT * FROM `categories`'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        name = row.get('name')
        link = f"https://olimp-parketa.ru{row.get('url')}"
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.83'
        }
        q = requests.get(url=link, headers=headers)
        with open(f"data/catalog/{name}.html", "w") as file:
            file.write(q.text)


def pars_desc_catalog():
    con = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root',
        db='pars_poly',
        cursorclass=DictCursor
    )
    query = 'SELECT * FROM `categories`'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        path = f"data/catalog/{row.get('name')}.html"
        id = int(row.get('id'))
        with open(path) as file:
            src = file.read()
            soup = BeautifulSoup(src, 'lxml')
            desc = soup.find('div', class_="top_seo_text").find('p').text.strip()
            query = f"UPDATE `categories` SET `description`=%s WHERE `id` = %s"
            con = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='root',
                db='pars_poly',
                cursorclass=DictCursor
            )
            try:
                with con.cursor() as cur:
                    cur.execute(query, (desc, id))
                    con.commit()
            finally:
                con.close()


def pars_subcat_page():
    con = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root',
        db='pars_poly',
        cursorclass=DictCursor
    )
    query = 'SELECT * FROM `categories` WHERE parent_id IS NULL'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        parent_id = row.get('id')
        path = f"data/catalog/{row.get('name')}.html"
        with open(path) as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        for item in soup.find_all('div', class_='slide'):
            link = item.find('a').get('href')
            name = item.find('p', class_='part__title').text
            query = f"INSERT INTO categories (`parent_id`, `name`, `url`) VALUES (%s, %s, %s)"
            con = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='root',
                db='pars_poly',
                cursorclass=DictCursor
            )
            try:
                with con.cursor() as cur:
                    cur.execute(query, (parent_id, name, link))
                    con.commit()
            finally:
                con.close()


def save_subcat_page():
    con = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root',
        db='pars_poly',
        cursorclass=DictCursor
    )
    query = 'SELECT * FROM `categories` WHERE parent_id IS NULL'
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        parent_id = int(row.get('id'))
        name = row.get('name')
        if not os.path.exists(f'data/catalog/{name}'):
            os.mkdir(f"data/catalog/{name}")
        con = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            db='pars_poly',
            cursorclass=DictCursor
        )
        query = f"SELECT * FROM `categories` WHERE parent_id = %s AND url LIKE %s"
        try:
            with con.cursor() as cur:
                cur.execute(query, (parent_id, '%/catalog/%'))
                rows = cur.fetchall()
        finally:
            con.close()
        for row in rows:
            link = f"https://olimp-parketa.ru{row.get('url')}"
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.83'
            }
            q = requests.get(url=link, headers=headers)
            with open(f"data/catalog/{name}/{row.get('name')}.html", "w") as file:
                file.write(q.text)


def pars_desc_subcat():
    con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='pars_poly', cursorclass=DictCursor)
    query = "SELECT * FROM `categories` WHERE parent_id IS NOT NULL AND url LIKE '%/catalog/%'"
    try:
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        con.close()
    for row in rows:
        id = row.get('id')
        parent_id = row.get('parent_id')
        name = row.get('name')
        con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='pars_poly',cursorclass=DictCursor)
        query = "SELECT name FROM `categories` WHERE id = %s LIMIT 1"
        try:
            with con.cursor() as cur:
                cur.execute(query, parent_id)
                rows = cur.fetchall()
        finally:
            con.close()
        path = f"data/catalog/{rows[0].get('name')}/{name}.html"
        with open(path, 'r') as file:
            html = file.read()
        top_seo_text = BeautifulSoup(html, 'lxml').find('div', class_='top_seo_text')
        if top_seo_text:
            if top_seo_text.find('p'):
                desc = top_seo_text.find('p').text.strip()
                print(id)
                print(desc)
                con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='pars_poly', cursorclass=DictCursor)
                query = f"UPDATE `categories` SET `description`=%s WHERE `id` = %s"
                try:
                    with con.cursor() as cur:
                        cur.execute(query, (desc, id))
                        con.commit()
                finally:
                    con.close()


def export_db():
    con = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='pars_poly',cursorclass=DictCursor)
    df = sql.read_sql('select * from categories', con)
    df.to_excel('export.xls')


def main():
    # catalog_page()
    # pars_catalog_page()
    # subcat_page()
    # pars_desc_catalog()
    # pars_subcat_page()
    # save_subcat_page()
    # pars_desc_subcat()
    # export_db()
    pass


if __name__ == '__main__':
    main()
