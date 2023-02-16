from bs4 import BeautifulSoup
import requests
from time import gmtime, strftime
import re

url = 'https://funpay.com/chips/34/'


class site_funpay:
    def __init__(self, url):
        self.server = str(input('Сервер: '))
        self.fraction = str(input('Фракция: '))
        self.url = url
        self.headers = {
            "Accept": "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                      "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/108.0.0.0 YaBrowser/23.1.2.987 Yowser/2.5 Safari/537.36",
        }
        self.request = requests.get(self.url, headers=self.headers)
        if self.request.status_code != 200:
            raise Exception("request.status_code != 200, ошибка подключения")

    def get_info(self):
        all_lots = BeautifulSoup(self.request.text, 'lxml').find_all(class_='tc-item')
        items_filtered = []

        for item in all_lots:
            item_href = item.get('href')
            item_nickname = item.find(class_='media-user-name').text.strip()
            item_price = re.findall(r'\d+.\d+', item.find(class_='tc-price').text.strip())[0]
            item_amount = re.findall(r'\d+', item.find(class_='tc-amount').text.strip())[0]
            item_server = item.find_all(class_='hidden-xxs')[0].text.strip()
            item_fraction = item.find_all(class_='hidden-xxs')[1].text.strip()
            if self.server.lower() in item_server.lower() and self.fraction.lower() in item_fraction.lower():
                #print(f'{item_server} | {item_fraction} {item_nickname} ({item_href}) - {item_amount}  {item_price}')
                items_filtered.append([item_server, item_fraction, item_nickname, item_href, item_amount, item_price])

        if len(items_filtered) == 0:
            raise Exception("Что то пошло не так, список пуст, возможно не правильно указано: Сервер, Фракция")

        return items_filtered

    def find_rechange_price(self):
        items_filtered_old = self.get_info()

        pass


if __name__ == '__main__':
    print(site_funpay(url=url).get_info())  # проверить статус код
