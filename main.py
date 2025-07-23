import asyncio
from uuid import uuid4
import sqlite3
import logging
import phonenumbers

from aiogram.utils.markdown import hide_link
from yoomoney import Client, Quickpay
from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

import phrase
import database

#DataBase
conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users
                (user_id INTEGER PRIMARY KEY,
                 number_house TEXT,
                 get_time_to_take TEXT,
                 description TEXT,
                 date TEXT,
                 phone_number TEXT,
                 sub TEXT,
                 sub_time TEXT)
                 """)

#Словарь для проверки оплаты
SAVE = {}

#yoomoney
client = Client(
    "4100117331671010.01638F83F51CF938F21112A42E39C11F832512D39364F9C28CD740BC75A31B07C495DA23E0DC8BC29C50695C61D14EADC8A90041079194373DEEE0BF976CCF5C9E4581BADA41540E2207F9C5CAA5F4A64C83B218E98B17F54598A25D56DC32E2026E1B625883EA670EB94EB4732CB17104AB41A2822EDB7994ACBA813B6B8429")

#telegram
bot = Bot(token="7733794741:AAFByS35qyCQJJbs7NEEB6YDwWGdciP5qj8")
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)
logging.basicConfig(level=logging.INFO)


class GetAddress(StatesGroup):
    address = State()


class GetTime(StatesGroup):
    time = State()


class GetDescription(StatesGroup):
    description = State()


class GetPhoneNumber(StatesGroup):
    number = State()


class GetDate(StatesGroup):
    date = State()


#Сохраняем адрес от пользователя
@router.message(GetAddress.address)
async def get_address(message: Message, state: FSMContext):
    address = message.text.lower().strip()
    user_id = message.from_user.id

    if not phrase.ADDRESS_PATTERN.match(address):
        await message.answer(phrase.bot_message["error_address"])
        return

    await database.set_number_house(address, user_id)
    await state.clear()
    await ask_time(message, state)


#Сохраняем время от пользователя
@router.message(GetTime.time)
async def get_time(message: Message, state: FSMContext):
    time = message.text
    user_id = message.from_user.id

    await database.set_time_bd(time, user_id)
    await state.clear()
    await ask_description(message, state)


#Сохраняем способ забора мусора
@router.message(GetDescription.description)
async def get_description(message: Message, state: FSMContext):
    description = message.text.lower().strip()
    user_id = message.from_user.id

    if description == "лично в руки" or description == "оставлю у двери":
        await database.set_description_bd(description, user_id)
        await state.clear()
        await ask_phone_number(message, state)
    elif description == "в главное меню":
        await back_but(message, state)
    else:
        await message.answer(phrase.bot_message["error_description"])


#Сохраняем номер телефона
@router.message(GetPhoneNumber.number)
async def get_phone(message: Message, state: FSMContext):
    number = message.text.lower().strip()
    user_id = message.from_user.id

    try:
        phone_number = phonenumbers.parse(number, "RU")
        if not phonenumbers.is_valid_number(phone_number):
            await message.reply(phrase.bot_message["error_phone"])
            return

        formatted_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        number = formatted_number

        await database.set_phone_bd(number, user_id)
        await state.clear()
        await ask_date_to_take(message, state)
    except Exception as e:
        await message.answer(
            "Неверный номер телефона. Пожалуйста, повторите ввод в формате +7XXXXXXXXXX или 8XXXXXXXXXX."
        )


#Сохраняем дату прихода за мусором
@router.message(GetDate.date)
async def get_date(message: Message, state: FSMContext):
    date = message.text.lower().strip()
    user_id = message.from_user.id

    await database.set_date_bd(date, user_id)
    row = await database.get_sub_bd(user_id)

    if row is None:
        await message.answer(phrase.bot_message["get_sub_error"])
        await state.clear()
        return
    sub_key = row[0]

    about = phrase.about_rate[sub_key]
    amount = phrase.price[sub_key]

    await send_pay_link(message, about, amount)
    await state.clear()


#start bot menu
def start_menu() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=phrase.button_text["areas_of_work"],)
    kb.button(text=phrase.button_text["rate"],)
    kb.button(text=phrase.button_text["about"],)
    kb.button(text=phrase.button_text["profile"],)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


#bot menu choose
def choose_rate() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=phrase.button_text["daily"])
    kb.button(text=phrase.button_text["weekly"])
    kb.button(text=phrase.button_text["monthly"])
    kb.button(text=phrase.button_text["monthly_plus"])
    kb.button(text=phrase.button_text["back"])
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


#Спрашиваем адрес
async def ask_address(message: Message, state: FSMContext):
    await message.answer(phrase.bot_message["ask_address"])
    await state.set_state(GetAddress.address)


#Спрашиваем время
async def ask_time(message: Message, state: FSMContext):
    kb = ReplyKeyboardBuilder()
    kb.button(text=phrase.button_text["morning_time"])
    kb.button(text=phrase.button_text["day_time"])
    kb.button(text=phrase.button_text["evening_time"])
    kb.button(text=phrase.button_text["back"])
    kb.adjust(3)
    await message.answer(phrase.bot_message["choose_time"],
                         reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(GetTime.time)


#Спрашиваем у пользователя передаст ли он мусор в руки или оставит у своей квартиры
async def ask_description(message: Message, state: FSMContext):
    kb = ReplyKeyboardBuilder()
    kb.button(text=phrase.button_text["to_hand"])
    kb.button(text=phrase.button_text["close_door"])
    kb.button(text=phrase.button_text["back"])
    kb.adjust(2)
    await message.answer(phrase.bot_message["choose_trash"],
                         reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(GetDescription.description)


#Спрашиваем номер телефона для экстренной связи
async def ask_phone_number(message: Message, state: FSMContext):
    await message.answer(phrase.bot_message["input_phone_number"])
    await state.set_state(GetPhoneNumber.number)


#Спрашиваем дату первого забора мусора, если это месячная подписка или дату забора, если это единоразовая
async def ask_date_to_take(message: Message, state: FSMContext):
    await message.answer(phrase.bot_message["choose_date"])
    await state.set_state(GetDate.date)


#hendler
@router.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                   (user_id,))
    conn.commit()
    await message.answer(phrase.bot_message["hello_message"], reply_markup=start_menu(), parse_mode="Markdown")


#Обработчики кнопок

#Спрашиваем адрес
@router.message(F.text == "Единоразово")
async def daily_pay(message: Message, state: FSMContext):
    user_id = message.from_user.id
    follow = "daily"

    await database.set_sub_bd(follow, user_id)
    await ask_address(message, state)


@router.message(F.text == "Недельная подписка")
async def weekly_pay(message: Message, state: FSMContext):
    user_id = message.from_user.id
    follow = "weekly"

    await database.set_sub_bd(follow, user_id)
    await ask_address(message, state)


@router.message(F.text == "Месячная подписка")
async def monthly_pay(message: Message, state: FSMContext):
    user_id = message.from_user.id
    follow = "monthly"

    await database.set_sub_bd(follow, user_id)
    await ask_address(message, state)


@router.message(F.text == "Месячная подписка плюс")
async def monthly_plus_pay(message: Message, state: FSMContext):
    user_id = message.from_user.id
    follow = "monthly_plus"

    await database.set_sub_bd(follow, user_id)
    await ask_address(message, state)


@router.message(F.text == "Район работы")
async def areas_of_work(message: Message):
    photo = types.FSInputFile(path=phrase.photos["location"])
    await message.answer_photo(photo, caption=phrase.bot_message["areas_of_work_about"], parse_mode="Markdown")


@router.message(F.text == "Тарифы")
async def rate(message: Message):
    await message.answer(phrase.bot_message["rate_about"], parse_mode="Markdown", reply_markup=choose_rate())


@router.message(F.text == "О нас")
async def about_text(message: Message):
    await message.answer(phrase.bot_message["about_us"], parse_mode="Markdown")


@router.message(F.text == "В главное меню")
async def back_but(message: Message):
    await message.answer(phrase.bot_message["back"], reply_markup=start_menu())


@router.message(F.text == "Мой профиль")
async def profile(message: Message):
    #Подключение к БД генерация красивого сообщения с профайлом / информация о подписке /
    user_id = message.from_user.id
    row = database.get_profile_bd(user_id)

    my_profile = phrase.my_profile(row)

    await message.answer(my_profile, parse_mode="Markdown")


#Генерация ссылки на оплату
async def send_pay_link(message: Message, about: str, amount: float):
    label = str(uuid4())
    quickpay = Quickpay(
        receiver="4100117331671010",
        quickpay_form="shop",
        targets="test payment",
        paymentType="SB",
        sum=amount,
        label=label
    )

    SAVE[label] = message.chat.id

    await message.answer(f"{hide_link(quickpay.base_url)}{about}\n\nОплатить по ссылке:", parse_mode="HTML")
    asyncio.create_task(check_success(message, label))


#Проверка оплаты
async def check_success(message: Message, label: str, timeout=300, interval=5):
    user_id = message.from_user.id
    chat_id = SAVE[label]

    if not chat_id:
        return

    for _ in range(timeout // interval):
        history = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.operation_history(label=label))

        if any(op.status == "success" for op in history.operations):
            await database.set_payed_bd(user_id)
            await bot.send_message(chat_id, "Оплачено!")
            return

        await asyncio.sleep(interval)
    await bot.send_message(chat_id, "Время ожидания оплаты истекло")


async def main():
    skip_updates = True
    while True:
        try:
            await dp.start_polling(
                bot,
                skip_updates=skip_updates,
                timeout=30,
                backoff_time=5
            )
        except Exception as e:
            logging.exception("Ошибка polling перезагрузка через 5 сек")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
