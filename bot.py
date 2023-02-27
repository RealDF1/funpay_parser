from asyncio import sleep
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

#from client_kb import kb_client
from funpay_parser import site_funpay

bot_TOKEN = '6030226662:AAFwvsR7V6qmz6-5v_n24J6XUx4675EVfkE'

bot = Bot(token=bot_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
stop = True


class funpay_data(StatesGroup):
    url = State()
    server = State()
    fraction = State()
    price = State()


@dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="stop", callback_data="stop"))
    await message.answer(f'Введите ссылку на страницу Funpay:', reply_markup=keyboard)
    await funpay_data.url.set()


@dp.callback_query_handler(text="stop")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer('123')


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

    await message.answer(
        f'Ниже цены - {price} ₽ просматриваем\nСервер - {server}\nФракция - {fraction}\n\nСтраница оферов:\n{url}')

    global stop
    while stop:
        if items_filtered_old:
            temp = st_funpay.find_rechange_price(items_filtered_old=items_filtered_old)
            items_filtered_old, sorted_items = temp[0], temp[1]
            # await sleep(15)
        else:
            temp = st_funpay.find_rechange_price(items_filtered_old=None)
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
