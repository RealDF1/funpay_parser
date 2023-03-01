import asyncio
from asyncio import sleep
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# from client_kb import kb_client
from funpay_parser_asyncio import site_funpay

bot_TOKEN = '6030226662:AAFwvsR7V6qmz6-5v_n24J6XUx4675EVfkE'

bot = Bot(token=bot_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
stop = False


class funpay_data(StatesGroup):
    url = State()
    server = State()
    fraction = State()
    price = State()


async def check_stop():
    global stop
    await asyncio.sleep(5)
    return stop


@dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    await message.answer(f'Введите ссылку на страницу Funpay:')
    await funpay_data.url.set()


@dp.callback_query_handler(text='stop')
async def handle_true_menu_2(callback_query: CallbackQuery):
    global stop  # обращаемся к глобальной переменной
    stop = True  # устанавливаем флаг
    await bot.send_message(callback_query.from_user.id, "Остановка цикла...")


@dp.message_handler(state=funpay_data.url)
async def get_url(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer(f'Введите сервер:')
    await funpay_data.server.set()


@dp.message_handler(state=funpay_data.server)
async def get_url(message: types.Message, state: FSMContext):
    await state.update_data(server=message.text)
    await message.answer(f'Введите цену:')
    await funpay_data.price.set()


@dp.message_handler(state=funpay_data.price)
async def get_url(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer(f'Введите фракцию:')
    await funpay_data.fraction.set()


@dp.message_handler(state=funpay_data.fraction)
async def get_url(message: types.Message, state: FSMContext):
    await state.update_data(fraction=message.text)

    data = await state.get_data()
    url = data.get('url')
    server = data.get('server')
    fraction = data.get('fraction')
    price = float(data.get('price'))
    st_funpay = site_funpay(url=url, server=server, price=price, fraction=fraction)
    items_filtered_old, sorted_items = [], []

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.insert(InlineKeyboardButton(text="Остановить", callback_data="stop"))
    await message.answer(
        f'Ниже цены - {price} ₽ просматриваем\nСервер - {server}\nФракция - {fraction}\n\nСтраница оферов:\n{url}',
        reply_markup=keyboard)

    while True:
        if await check_stop():
            break

        if items_filtered_old:
            temp = await st_funpay.find_rechange_price(items_filtered_old=items_filtered_old)
            items_filtered_old, sorted_items = temp[0], temp[1]
            # await sleep(15)
        else:
            temp = await st_funpay.find_rechange_price(items_filtered_old=None)
            items_filtered_old = temp[0]

        if sorted_items:
            print(sorted_items)
            for x in range(len(sorted_items)):
                # Вывод именных данных если < price
                if float(sorted_items[x][5]) < price:
                    if temp[2]:
                        await message.answer(
                            f'Продавец {sorted_items[x][2]} понизил цену\n  📉 Новый прайс - {sorted_items[x][5]}\n\n{sorted_items[x][3]} ₽')
                    else:
                        await message.answer(
                            f'Продавец {sorted_items[x][2]} повысил цену\n  📈 Новый прайс - {sorted_items[x][5]}\n\n{sorted_items[x][3]} ₽')

    await message.answer('Произошла остановка')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
