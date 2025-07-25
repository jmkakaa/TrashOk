import re

ADDRESS_PATTERN = re.compile(
    r".*\b(ул\.?|улица)\b.*\b(д\.?|дом)\s*\d+.*\b(кв\.?|квартира)\s*\d+.*",
    flags=re.IGNORECASE
)


def my_profile(row):
    house, time_to_take, desc, date_first_take, phone_number, sub, time_sub = row
    time_start, time_finish = time_sub.split("---")


    return f"📝 *Ваш профиль* 📝\n\n🏠*Адрес:* {house} \n📱*Телефон:* {phone_number} \n⏰*Промежуток забора:* {time_to_take} \n🤲*Способ передачи:* {desc} \n📦*Тип подписки:* {sub} \n🗓*Первый вывоз:* {date_first_take} \n📅*Период подписки:* \nс {time_start} до {time_finish}"

#Прайс за услуги
price = {
    "daily": 2,
    "weekly": 2,
    "monthly": 2,
    "monthly_plus": 2
}
#Описание услуг
about_rate = {
    "daily": (
        "🗑️ *Единоразовый вынос мусора*\n"
        "Идеально, когда нужно быстро избавиться от накопившегося мусора одним разом. "
        "Выберите удобное время — и наши курьеры приедут, заберут всё сразу и удалят из вашего дома!"
    ),
    "weekly": (
        "📆 *Недельная подписка*\n"
        "Вынос мусора через день в течение 7 дней. "
        "Подходит для тех, кто не успевает выносить каждый день, но хочет свежести и порядка всю неделю."
    ),
    "monthly": (
        "🗓️ *Классическая месячная подписка*\n"
        "2 выноса мусора в неделю (итого 8 раз в месяц). "
        "Оптимальный баланс цены и частоты — удобно для семей и небольших офисов."
    ),
    "monthly_plus": (
        "🚀 *Месячная подписка плюс*\n"
        "Вынос через день в течение всего месяца (до 15 выносов). "
        "Максимальный комфорт: мусора никогда не будет слишком много, а вы — всегда спокойны за чистоту."
    ),
}

button_text = {
    "profile": "Мой профиль",
    "areas_of_work": "Район работы",
    "rate": "Тарифы",
    "about": "О нас",
    "daily": "Единоразово",
    "weekly": "Недельная подписка",
    "monthly": "Месячная подписка",
    "monthly_plus": "Месячная подписка плюс",
    "back": "В главное меню",
    "morning_time": "Утро\n(08:00–12:00)",
    "day_time": "День\n(13:00–17:00)",
    "evening_time": "Вечер\n(18:00–23:00)",
    "to_hand": "Лично в руки",
    "close_door": "Оставлю у двери",

}

bot_message = {
    "choose_time": "Выберете время:",
    "choose_trash": "Выберете способ передачи мусора нашему курьеру",
    "input_phone_number": "Введите ваш номер телефона для экстренной связи\n\nФормат: 89991231212",
    "choose_date": "Введите дату когда курьер приедет за мусором первый раз",
    "hello_message": (
        "👋 Добро пожаловать в «МусорОк» — сервис по оперативному выносу мусора!\n\n"
        "📦 Доступные тарифы:\n"
        "  • *Единоразово* — вынос мусора по вашей заявке один раз. Идеально для разовой уборки.\n"
        "  • *Недельная подписка* — вынос через день в течение 7 дней.\n"
        "  • *Месячная подписка* — классический вариант: 2 выноса мусора в неделю.\n"
        "  • *Месячная плюс* — вынос через день в течение 30 дней.\n\n"
        "📍 Наши районы работы: Юности, Весенняя (см. «Районы работы» для подробностей).\n"
        "🔍 Чтобы узнать подробнее о тарифах, нажмите кнопку «Тарифы».\n"
        "📅 Для заказа выберите «Единоразово» или нужную подписку и следуйте подсказкам бота.\n\n"
        "Если у вас есть вопросы — нажмите «О нас»."
    ),
    "areas_of_work_about": (
        "📍 *Районы работы*\n\n"
        "🚀 Мы только что запустились, поэтому на старте обслуживаем небольшой район:\n"
        "  • Улица Юности\n"
        "  • Улица Весенняя\n\n"
        "Мы планируем расширяться! Если вы за пределами этих зон, "
        "напишите нам в разделе *«О нас»* — и мы постараемся добавить ваш район в ближайшее время. 😊"
    ),
    "rate_about": (
        "💡 *Тарифы*\n\n"
        "Выберите подходящий вариант:\n"
        "  • *Единоразово* — вынос мусора по разовому заказу\n"
        "  • *Недельная подписка* — вынос через день в течение 7 дней\n"
        "  • *Месячная подписка* — классический вариант: 2 раза в неделю\n"
        "  • *Месячная подписка плюс* — вынос через день в течение 30 дней\n\n"
        "Нажмите на кнопку с нужным тарифом и следуйте подсказкам бота. 🗑️"
    ),
    "about_us": (
        "💼 *О нас — МусорОк*\n\n"
        "Мы — молодой стартап, в который вложили всю душу. 🚀\n"
        "Наша миссия — сделать вынос мусора быстрым, надёжным и доступным каждому.\n"
        "Команда МусорОк тщательно отбирает курьеров и постоянно улучшает сервис, "
        "чтобы вы оставались довольны.\n\n"
        "Есть вопросы, идеи или просто хотите сказать «привет»? Пишите мне в Telegram: "
        "[@kramjmka](https://t.me/kramjmka) 😉"
    ),
    "error_address": "Не верный формат.\n\nПожалуйста попробуйте сновав таком формате: \nул. Пушкина, д. 10, кв. 5",
    "error_description": "Не знаю таких вариантов. Попробуй использовать кнопки ниже",
    "error_phone": "Некорректный номер телефона",
    "get_sub_error": "Не удалось получить тип Подписки, начните заново!",
    "ask_address": "Напишите адрес откуда забирать мусор (Улица, дом, квартира)",

    "back": "Вернули вас в главное меню"
}

photos = {
    "location": "template/location.png",
}