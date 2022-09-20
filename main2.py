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


def get_data():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.83"
    }
    q = requests.get(url='https://yandex.by/maps/org/itr_inzhenerno_tekhnicheske_resheniya/236612198902/reviews/?ll=37.418523%2C55.712827&z=16', headers=headers)
    if not os.path.exists('data2'):
        os.mkdir("data2")
    with open("data2/ya.html", "w") as file:
        file.write(q.text)


def parser_1():
    with open("data2/ya_save.html") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    data = []
    for item in soup.find_all('div', class_='business-reviews-card-view__review'):
        autor = item.find('div', class_='business-review-view__author').find('span').text
        comment = item.find('span', class_='business-review-view__body-text').text
        data.append([autor, comment])
    df = pd.DataFrame(data)
    df.to_excel(excel_writer="otzivi.xls")


def parser_2():
    with open("data2/ya_save_2.html") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    data = []
    for item in soup.find_all('div', class_='business-reviews-card-view__review'):
        autor = item.find('div', class_='business-review-view__author').find('span').text
        comment = item.find('span', class_='business-review-view__body-text').text
        data.append([autor, comment])
    df = pd.DataFrame(data)
    df.to_excel(excel_writer="otzivi2.xls")


def parser_3():
    with open("data3/otzivi.html") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    data = []
    js = soup.find('script', {'type': "application/ld+json"}).text
    json_data = json.loads(js)
    review = json_data['review']
    for item in review:
        autor = item['author']
        if "description" in item:
            comment = item['description']
            data.append([autor, comment])
    df = pd.DataFrame(data)
    df.to_excel(excel_writer="otzivi3.xls")


def main():
    # get_data()
    # parser_1()
    # parser_2()
    parser_3()


if __name__ == '__main__':
    main()