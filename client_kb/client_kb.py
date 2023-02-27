from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import callback_data

b1 = KeyboardButton('/start')
b2 = KeyboardButton('/stop', callback_data='stop')

kb_client = ReplyKeyboardMarkup()

#kb_client.add(b1).add(b2)
