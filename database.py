import sqlite3
from datetime import datetime, timedelta


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

async def set_number_house(address, user_id):
    cursor.execute("UPDATE users SET number_house = ? WHERE user_id = ?",
                   (address, user_id))
    conn.commit()


async def set_sub_bd(foll, user_id):
    cursor.execute("UPDATE users SET sub = ? WHERE user_id = ?",
                   (foll, user_id))
    conn.commit()


async def set_time_bd(time, user_id):
    cursor.execute("UPDATE users SET get_time_to_take = ? WHERE user_id = ?",
                   (time, user_id))
    conn.commit()


async def set_description_bd(description, user_id):
    cursor.execute("UPDATE users SET description = ? WHERE user_id = ?",
                   (description, user_id))
    conn.commit()


async def set_phone_bd(number, user_id):
    cursor.execute("UPDATE users SET phone_number = ? WHERE user_id = ?",
                   (number, user_id))
    conn.commit()


async def set_date_bd(date, user_id):
    cursor.execute("UPDATE users SET date = ? WHERE user_id = ?",
                   (date, user_id))
    conn.commit()


async def set_payed_bd(user_id):

    now = datetime.now()
    week_sub = now + timedelta(days=7)
    month_sub = now + timedelta(days=30)

    total_date = ""

    row = await get_sub_bd(user_id)
    sub_key = row[0]

    if sub_key == "daily":
        total_date = (now.strftime("%Y-%m-%d") + "---" + (now + timedelta(days=1)).strftime("%Y-%m-%d"))
    elif sub_key == "weekly":
        total_date = (now.strftime("%Y-%m-%d") + "---" + week_sub.strftime("%Y-%m-%d"))
    elif sub_key == "monthly":
        total_date = (now.strftime("%Y-%m-%d") + "---" + month_sub.strftime("%Y-%m-%d"))
    elif sub_key == "monthly_plus":
        total_date = (now.strftime("%Y-%m-%d") + "---" + month_sub.strftime("%Y-%m-%d"))

    cursor.execute("UPDATE users SET sub_time = ? WHERE user_id = ?",
                   (total_date, user_id))
    conn.commit()


async def get_sub_bd(user_id):
    cursor.execute("SELECT sub FROM users WHERE user_id = ?",
                   (user_id,))
    return cursor.fetchone()


async def get_profile_bd(user_id):
    cursor.execute("SELECT number_house, get_time_to_take, description, date, phone_number, sub, sub_time FROM users WHERE user_id = ?",
                   (user_id, ))
    return cursor.fetchone()