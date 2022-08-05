import asyncio
from email import message, message_from_binary_file
import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from async_timeout import timeout

from messages import MESSAGES
from config import TELGRAM_TOKEN, PAYMENTS_PROVIDER_TOKEN, TIME_MACHINE_IMAGE_URL,MONGODB_TOKEN
from States import CreateandAdd_states
import DataBase

# Объект бота
bot = Bot(TELGRAM_TOKEN, parse_mode=types.ParseMode.MARKDOWN_V2)
#Подключение БД
storage = MongoStorage(uri=MONGODB_TOKEN)  
# Диспетчер для бота
dp = Dispatcher(bot,storage=storage)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)



@dp.message_handler(commands=['terms'])
async def process_terms_command(message: types.Message):
    await message.reply(MESSAGES['terms'], reply=False)

#функция для создане кнопки
def new_sub_button():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 =types.KeyboardButton("Создать новое напоминание")
    button2 =types.KeyboardButton("Мои напоминания")
    keyboard.add(button1,button2)
    return keyboard

@dp.message_handler(commands=["help","start"])
async def helper(message: types.Message):
    print(1)
    DataBase.set(message.chat.id,message.chat)
    await message.answer("Добро пожаловать в Кафе у дома \nЗдесь вы сможете забронировать столик \nДля начала введите команду /reservation")     
# Setup prices
PRICE = types.LabeledPrice(label='stone', amount=100000)

@dp.message_handler(commands=['reservation'])
async def cmd_buy(message: types.Message):
    print(2)
    await bot.send_invoice(message.chat.id, title='Наш зал',description="Для бронирования столика необходимо внести депозит.",provider_token=PAYMENTS_PROVIDER_TOKEN,currency='RUB',photo_url='https://brauplatz.ru/images/pic/shema-stolov-2017.jpg',photo_height=512,photo_width=780,photo_size=512,prices=[PRICE],start_parameter='reservation',payload='reservation')


@dp.pre_checkout_query_handler()
async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id,ok=True)

@dp.message_handler(state=CreateandAdd_states.choose_table)
async def choose_table(message: types.Message,state):
    reserved_tabel=[]
    for i in range(1,57,4):
        reserved_tabel.append(i)
    try:
        if int(message.text) in reserved_tabel:
            await message.answer("Этот столик уже забронирован")
        else:
            await message.answer("Столик  забронирован")
    except:
        await message.answer("Введите номер столика")
    await state.finish()


@dp.message_handler(content_types = ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    print('successful_payment:')
    receipt = message.successful_payment.to_python() #{'currency':, 'total_amount': , 'invoice_payload':, 'telegram_payment_charge_id':, 'provider_payment_charge_id':}
    receipt["chat_id"]=message.chat.id
    DataBase.set_dish(receipt)
    await message.answer("Введите номер столика ,чтобы узнать свободен ли он")
    await CreateandAdd_states.choose_table.set()


@dp.message_handler()
async def default_handler(message):
    await helper(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)