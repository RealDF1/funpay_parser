from bs4 import BeautifulSoup
from time import sleep
from typing import Union
import asyncio
import re
import requests

# Данные для теста
url = 'https://funpay.com/chips/34/'
server = 'everlook'
price = 5
fraction = ''


class site_funpay:
    def __init__(self, url, server, price: Union[int, float], fraction=''):
        self.server = server
        self.price = float(price)
        self.fraction = fraction
        self.url = url
        self.headers = {
            "Accept": "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                      "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/108.0.0.0 YaBrowser/23.1.2.987 Yowser/2.5 Safari/537.36",
        }

    def __unic_list(self, list_frist, list_second):
        """
        [list1] - [list2]
        :param list_frist:
        :param list_second:
        :return sorted_list:
        """
        return [x for x in list_frist if x not in list_second]

    def get_info(self):
        """
        Получения вложенного списка с отфильтрованными данными, вида:
        [[item_server, item_fraction, item_nickname, item_href, item_amount, item_price], ...]
        :return items_filtered:
        """
        # Получение верстки
        request = requests.get(self.url, headers=self.headers)
        if request.status_code != 200:  # Проверка статус кода запроса
            raise Exception("request.status_code != 200, ошибка подключения")
        all_lots = BeautifulSoup(request.text, 'lxml').find_all(class_='tc-item')

        items_filtered = []  # Будущий отфильтрованный список

        # Раcпарсинг полученной верстки
        for item in all_lots:
            item_href = item.get('href')  # Ссылка на офер
            item_nickname = item.find(class_='media-user-name').text.strip()  # Никнейм офера
            item_price = re.findall(r'\d+.\d+', item.find(class_='tc-price').text.strip())[0]  # Цена у офера
            item_amount = re.findall(r'\d+', item.find(class_='tc-amount').text.strip())[0]  # Наличие в кормашке ру-ру
            item_server = item.find_all(class_='hidden-xxs')[0].text.strip()  # Наименование сервера
            item_fraction = item.find_all(class_='hidden-xxs')[1].text.strip()  # Фракция офера

            #  Нахождение нужной фракции и нужного сервера
            if self.server.lower() in item_server.lower() and self.fraction.lower() in item_fraction.lower():
                items_filtered.append([item_server, item_fraction, item_nickname, item_href, item_amount, item_price])

                # Для тестов, вывод списков
                # print(f'{item_server} | {item_fraction} {item_nickname} ({item_href}) - {item_amount}  {item_price}')

        # Если список отфильтрованных данных пуст / Неверно указаны данные для фильтрации
        if len(items_filtered) == 0:
            raise Exception("Что то пошло не так, список пуст, возможно не правильно указано: Сервер, Фракция")

        return items_filtered  # Вывод отфильтрованных данных

    def find_rechange_price(self, items_filtered_old=[]):
        """
        Поиск выставленной цены ниже self.price
        :param items_filtered_old:
        :return:
        """
        items_filtered_new = self.get_info()  # Получение отфильтрованных данных
        items_filtered = []

        # Проверка на появление/изменение данных / Пустой ли items_filtered_old
        if items_filtered_old is not None and not items_filtered_new == items_filtered_old:
            items_filtered = self.__unic_list(items_filtered_new, items_filtered_old)
            items_filtered_old = self.__unic_list(items_filtered_old, items_filtered_new)
            print(float(items_filtered_old[0][5]), float(items_filtered[0][5]))
            if float(items_filtered_old[0][5]) - float(items_filtered[0][5]) < 0:
                return [items_filtered_new, items_filtered, False]  # Получение изменений
            return [items_filtered_new, items_filtered, True]
        else:
            return [items_filtered_new, items_filtered]


if __name__ == '__main__':
    while True:
        print(site_funpay(url=url, server=server, price=price, fraction=fraction).find_rechange_price())
