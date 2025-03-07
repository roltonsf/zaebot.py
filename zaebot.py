from telethon import TelegramClient, events
import sqlite3
import time
import random

# 🔹 Укажи свои API_ID и API_HASH
API_ID = 123456
API_HASH = "your_api_hash"

# 🔹 Укажи свой Telegram ID (чтобы команды .д и .с мог использовать только ты)
# Список админов
ADMINS = [1120069212, 1217809305, 7603661633]  # Замени на свои айди

# 🔹 Подключение к базе данных
conn = sqlite3.connect("basketbot.db", check_same_thread=False)
cursor = conn.cursor()

import time

# Проверка активного бустера
def check_booster(user_id):
    cursor.execute("SELECT booster_name, activation_time FROM boosters WHERE user_id = ?", (user_id,))
    booster = cursor.fetchone()

    if not booster:
        return None  # У пользователя нет активного бустера

    booster_name, activation_time = booster

    # Проверяем, не истекло ли время действия бустера
    current_time = int(time.time())  # Текущее время в секундах
    if activation_time + 3600 <= current_time:  # 3600 секунд = 1 час
        # Бустер истек, удаляем его
        cursor.execute("DELETE FROM boosters WHERE user_id = ?", (user_id,))
        conn.commit()
        return None

    return booster_name  # Возвращаем название активного бустера

import sqlite3

# Устанавливаем соединение с базой данных
conn = sqlite3.connect('basketbot.db')
cursor = conn.cursor()

# Создаем таблицу boosters,

cursor.execute("""
CREATE TABLE IF NOT EXISTS boosters (
    user_id INTEGER,
    booster_name TEXT,
    quantity INTEGER,
    PRIMARY KEY (user_id, booster_name)
)
""")
conn.commit()

# 🔹 Создание таблицы, если её нет
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY, 
    username TEXT, 
    balance INTEGER DEFAULT 1000, 
    last_bonus INTEGER DEFAULT 0,
    started INTEGER DEFAULT 0
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS boosters (
    user_id INTEGER, 
    booster_name TEXT, 
    quantity INTEGER DEFAULT 0, 
    PRIMARY KEY (user_id, booster_name)
)""")
conn.commit()

# 🔹 Запуск Telethon-клиента
bot = TelegramClient("basketbot", API_ID, API_HASH)

# 🔹 Функции работы с балансом
def get_user(user_id, username=None):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id, username, balance) VALUES (?, ?, 1000)", (user_id, username))
        conn.commit()
        return (user_id, username, 1000, 0, 0)
    return user

def update_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

import random

# 🏀 Баскетбол
import random
from telethon import events

@bot.on(events.NewMessage(pattern=r"\.б (\d+)"))
async def basketball_game(event):
    user_id = event.sender_id
    bet = int(event.pattern_match.group(1))

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user is None or user[0] < bet:
        await event.reply("🚫 Недостаточно лудкоинов для ставки!")
        return

    await event.reply("🏀")  # Отправка эмодзи баскетбола

    # Определяем исход игры
    outcome = random.choices(
        ["lose", "x2", "x3"], 
        weights=[60, 30, 10], 
        k=1
    )[0]

    if outcome == "lose":
        new_balance = user[0] - bet  # Проигрыш - просто вычитаем ставку
        result_text = random.choice([
            "💀 Ты не попал... Лудкоины утекают сквозь пальцы!",
            "😔 Неудача... Сегодня баскетбольное кольцо явно не твой друг.",
            "👎 Промах! Может, стоит взять перерыв?"
        ])
        multiplier_text = ""
    else:
        multiplier_value = 2 if outcome == "x2" else 3  # Определяем множитель
        winnings = bet * multiplier_value  # Выигрыш = ставка * множитель
        new_balance = user[0] - bet + winnings  # Вычитаем ставку, добавляем выигрыш

        result_text = random.choice([
            f"🔥 Красавчик! Твой бросок точен, и ты забираешь {winnings} лудкоинов!",
            f"🏆 Отличный бросок! Вдвое больше лудкоинов — {winnings} теперь у тебя!",
            f"🎯 Точная стрельба! Ты выиграл {winnings} лудкоинов!"
        ])
        multiplier_text = f" (x{multiplier_value})"

    # Обновляем баланс игрока
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()

    # Отправляем сообщение с результатом
    await event.reply(result_text + multiplier_text, reply_to=event.id)

# ⚽ Футбол
@bot.on(events.NewMessage(pattern=r"\.ф (\d+)"))
async def football_game(event):
    user_id = event.sender_id
    bet = int(event.pattern_match.group(1))

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user is None or user[0] < bet:
        await event.reply("🚫 Недостаточно лудкоинов для ставки!")
        return

    await event.reply("⚽")  # Отправка эмодзи футбола

    # Определяем исход игры
    outcome = random.choices(
        ["lose", "x2", "x3"], 
        weights=[60, 30, 10], 
        k=1
    )[0]

    if outcome == "lose":
        new_balance = user[0] - bet
        result_text = random.choice([
            "💀 Ты промахнулся по воротам... Лудкоины утекают!",
            "😔 Мимо! Сегодня явно не твой день.",
            "👎 Вратарь ловит мяч! Твой счет уменьшается."
        ])
        multiplier_text = ""
    else:
        multiplier_value = 2 if outcome == "x2" else 3
        winnings = bet * multiplier_value
        new_balance = user[0] - bet + winnings

        result_text = random.choice([
            f"🔥 Гол! Ты выигрываешь {winnings} лудкоинов!",
            f"⚡ Мастерский удар! Твой приз — {winnings} лудкоинов!",
            f"🥅 Отличный гол! Лудкоины твои — {winnings}!"
        ])
        multiplier_text = f" (x{multiplier_value})"

    # Обновляем баланс игрока
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()

    # Отправляем сообщение с результатом
    await event.reply(result_text + multiplier_text, reply_to=event.id)

# 💰 Баланс
@bot.on(events.NewMessage(pattern=r"\.бал"))
async def check_balance(event):
    user_id = event.sender_id
    user = get_user(user_id)
    await event.reply(f"💰 Твой баланс: {user[2]} лудкоинов.")

# 🎁 Бонус раз в 3 часа
@bot.on(events.NewMessage(pattern=r"\.бонус"))
async def get_bonus(event):
    user_id = event.sender_id
    user = get_user(user_id)

    current_time = int(time.time())
    if current_time - user[3] < 10800:
        await event.reply("⏳ Ты уже получал бонус! Попробуй позже.")
        return

    update_balance(user_id, 5000)
    cursor.execute("UPDATE users SET last_bonus = ? WHERE user_id = ?", (current_time, user_id))
    conn.commit()
    await event.reply("🎁 Ты получил 5000 лудкоинов!")

# 🔄 Передача монет
@bot.on(events.NewMessage(pattern=r"\.т (\d+)"))
async def transfer_coins(event):
    user_id = event.sender_id
    user = get_user(user_id)

    if not event.is_reply:
        await event.reply("⚠️ Ответь на сообщение игрока, которому хочешь передать монеты!")
        return

    reply_msg = await event.get_reply_message()
    target_id = reply_msg.sender_id

    if user_id == target_id:
        await event.reply("🚫 Нельзя передавать монеты самому себе!")
        return

    amount = int(event.pattern_match.group(1))

    if amount <= 0 or user[2] < amount:
        await event.reply("💸 Недостаточно лудкоинов!")
        return

    update_balance(user_id, -amount)
    update_balance(target_id, amount)
    
    await event.reply(f"✅ Ты передал **{amount}** лудкоинов игроку {reply_msg.sender.first_name}! 💰")

# 🏆 Топ-5 игроков
@bot.on(events.NewMessage(pattern=r"\.топ 5"))
async def top_players(event):
    cursor.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 5")
    top_list = cursor.fetchall()

    if not top_list:
        await event.reply("📉 Топ пуст!")
        return

    msg = "🏆 **Топ 5 игроков по балансу:**\n"
    for i, (username, balance) in enumerate(top_list, 1):
        msg += f"{i}. @{username} — {balance} лудкоинов\n"
    await event.reply(msg)

# 🚀 Старт (исправленный)
@bot.on(events.NewMessage(pattern=r"\.старт"))
async def start_game(event):
    user_id = event.sender_id
    sender = await event.get_sender()
    username = getattr(sender, "username", None) or f"User#{user_id}"

    # Проверяем, является ли игрок админом
    if user_id in ADMINS:
        admin_tag = "✨🎩 **Вы — Админ!** 🎩✨"  # Яркая метка для админа
        admin_style ="🔥 **Король этой игры!** 🔥"
    else:
        admin_tag = ""  # Если не админ, то пусто
        admin_style = "⚡ Ты на старте, игрок! ⚡"  # Для обычных пользователей

    # Устанавливаем начальный баланс
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, 1000)", (user_id,))
        conn.commit()

    # Отправляем приветственное сообщение с красивым оформлением
    await event.reply(f"""
    🎉 **Добро пожаловать в БаскетБот!** 🏀
    {admin_tag}

    {admin_style} 

    💰 Проверяй свой баланс, если там что-то завалялось — можешь сыграть! 👀
    ⚡ Используй .хелп, чтобы узнать список команд!

    💬 Ты всегда можешь обратиться за помощью или узнать подробности команд.
    """)


# 📜 Хелп
@bot.on(events.NewMessage(pattern=r"\.хелп"))
async def help_command(event):
    msg = ("📜 **Список команд:**\n"
           "🏀 **.б [ставка]** — сыграть в баскетбол\n"
           "⚽ **.ф [ставка]** — сыграть в футбол\n"
           "💰 **.бал** — узнать баланс\n"
           "🎁 **.бонус** — получить бонус (раз в 3 часа)\n"
           "🔄 **.т [сумма]** — передать монеты\n"
           "🏆 **.топ 5** — топ игроков\n"
           "🚀 **.старт** — начать игру\n"
"🎰 **.р [ставка]** - опасная игра в рулетку, подробнее: `.ринф`\n"
"💹 **.ставка** — __объяснение как играть__ — `.ставки`\n")


    await event.reply(msg)

# 💸 Выдача монет (только для владельца)
@bot.on(events.NewMessage(pattern=r"\.д (\d+)"))
async def give_coins(event):
    if event.sender_id not in ADMINS:
        await event.reply("⛔ У тебя нет прав на эту команду!")
        return

    if not event.is_reply:
        await event.reply("⚠️ Ответь на сообщение игрока, которому хочешь выдать лудкоины!")
        return


    reply_msg = await event.get_reply_message()
    target_id = reply_msg.sender_id
    amount = int(event.pattern_match.group(1))

    update_balance(target_id, amount)
    await event.reply(f"✅ Выдано **{amount}** лудкоинов игроку {reply_msg.sender.first_name}!")

import random
import asyncio

# 🎰 Игра в рулетку с анимацией
@bot.on(events.NewMessage(pattern=r"\.р (\d+)"))
async def play_roulette(event):
    user_id = event.sender_id
    sender = await event.get_sender()
    username = getattr(sender, "username", None) or f"User{user_id}"
    user = get_user(user_id, username)

    bet = int(event.pattern_match.group(1))

    if bet < 1000:
        await event.reply("⚠️ Минимальная ставка — **1000** лудкоинов!")
        return

    if user[2] < bet:
        await event.reply("💸 У тебя недостаточно лудкоинов для этой ставки!")
        return

    # Новые шансы на исход
    outcomes = [
        ("🔴 Проигрыш", 0, 60),  
        ("🟡 Возврат ставки", 1, 10),  
        ("🟢 x2 ставка", 2, 15),  
        ("🔵 x3 ставка", 3, 8),  
        ("💎 x5 ставка", 5, 5),  
        ("🔥 x10 ставка (джекпот)", 10, 2)  
    ]

    # Выбираем случайный исход
    result = random.choices(outcomes, weights=[o[2] for o in outcomes])[0]
    outcome_text, multiplier, _ = result

    # Вычисляем изменение баланса
    winnings = bet * multiplier
    balance_change = winnings - bet
    update_balance(user_id, balance_change)

    # Анимация вращения рулетки
    animation_frames = ["🎰 🔄", "🎰 🔄🔄", "🎰 🔄🔄🔄", "🎰 🔄🔄🔄🔄", "🎰 🎯"]
    msg = await event.reply(f"🎰 **Рулетка крутится...** 🔄")

    for frame in animation_frames:
        await asyncio.sleep(0.5)
        await msg.edit(frame)

    # Итоговое сообщение
    final_msg = (
        f"🎰 **Рулетка остановилась!**\n\n"
        f"💰 **Ставка:** {bet} лудкоинов\n"
        f"🎲 **Результат:** {outcome_text}\n"
        f"🏦 **Твой баланс:** {get_user(user_id, username)[2]} лудкоинов\n\n"
        f"🔄 Попробуй снова с `.р`!"
    )

    await msg.edit(final_msg)

# 🎰 Информация о рулетке
@bot.on(events.NewMessage(pattern=r"\.ринф"))
async def roulette_info(event):
    msg = (
        "🎰 **Рулетка — Испытай удачу!** 🎰\n\n"
        "💰 **Как играть:**\n"
        "Отправь `.р [ставка]`, и рулетка решит твою судьбу!\n\n"
        "🎲 **Шансы на выигрыш:**\n"
        "🔴 Проигрыш — **60%**\n"
        "🟡 Возврат ставки — **10%**\n"
        "🟢 x2 ставка — **15%**\n"
        "🔵 x3 ставка — **8%**\n"
        "💎 x5 ставка — **5%**\n"
        "🔥 x10 ставка (джекпот) — **2%**\n\n"
        "⚠️ Минимальная ставка: **1000 лудкоинов**\n"
        "💎 Чем больше ставка, тем больше выигрыш!\n\n"
        "🔄 Удачи, игрок! 🎰"
    )
    await event.reply(msg)

import random

# Список возможных цветов и их шансов
colors = {
    "🖤": 49,  # Черный
    "❤️": 49,  # Красный
    "💚": 2     # Зеленый
}

# Игровая логика
user_bets = {}

# Маппинг сокращений на цвета
color_mapping = {
    "ч": "🖤",  # Черный
    "к": "❤️",  # Красный
    "з": "💚"   # Зеленый
}

# Команда для ставок
@bot.on(events.NewMessage(pattern=r"\.ставка (ч|к|з) (\d+)"))
async def place_bet(event):
    color_key = event.pattern_match.group(1)
    bet_amount = int(event.pattern_match.group(2))
    user_id = event.sender_id

    # Проверка баланса игрока
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result is None:
        # Если игрока нет в базе данных, создаем его с начальным балансом
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 1000))
        conn.commit()
        balance = 1000
    else:
        balance = result[0]

    if bet_amount > balance:
        await event.reply(f"❌ У вас недостаточно лудкоинов для ставки! Ваш баланс: {balance} лудкоинов.")
        return

    if color_key not in color_mapping:
        await event.reply("❌ Неверный выбор цвета! Пожалуйста, используйте .ставка ч (черный), .ставка к (красный) или .ставка з (зеленый).")
        return

    color = color_mapping[color_key]
    user_bets[user_id] = {"color": color, "bet_amount": bet_amount}

    await event.reply(f"🎲 Вы выбрали {color} и поставили {bet_amount} лудкоинов. Для начала игры напишите .го.")

# Команда для начала игры
@bot.on(events.NewMessage(pattern=r"\.го"))
async def start_game(event):
    user_id = event.sender_id
    if user_id not in user_bets:
        await event.reply("❌ Вы еще не сделали ставку! Напишите .ставка [цвет] [ставка].")
        return
    
    # Получаем цвет и ставку игрока
    user_bet = user_bets[user_id]
    chosen_color = user_bet["color"]
    bet_amount = user_bet["bet_amount"]
    
    # Рандомный выбор цвета
    drawn_color = random.choices(list(colors.keys()), weights=colors.values(), k=1)[0]
    
    # Вычисление выигрыша
    if drawn_color == chosen_color:
        if drawn_color == "💚":
            winnings = bet_amount * 15
            await event.reply(f"🎉 Вы выбрали правильно! Цвет {drawn_color} и вы выиграли {winnings} лудкоинов! 🔥")
        else:
            winnings = bet_amount * 2
            await event.reply(f"🎉 Вы выбрали правильно! Цвет {drawn_color} и вы выиграли {winnings} лудкоинов! ✨")
        
        # Обновление баланса игрока
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, user_id))
        conn.commit()
    else:
        await event.reply(f"💥 Увы, не угадали. Бот выбрал {drawn_color}. Попробуйте снова!")
        
        # Списывание ставки с баланса игрока
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bet_amount, user_id))
        conn.commit()

    # Удаляем ставку игрока
    del user_bets[user_id]

# Команда для объяснения игры
@bot.on(events.NewMessage(pattern=r"\.ставки"))
async def show_rules(event):
    rules = """
    💡 **Как играть в ставки по цветам:**
    
    1. Напишите `.ставка [цвет] [ставка]`, чтобы выбрать цвет и поставить лудкоины.
       Доступные цвета:
       - .ставка ч (черный) 🖤
       - .ставка к (красный) ❤️
       - .ставка з (зеленый) 💚
    
    2. После этого напишите `.го`, чтобы начать игру.
    
    🎲 **Шансы на победу:**
    - 🖤 Черный: 49%
    - ❤️ Красный: 49%
    - 💚 Зеленый: 2%
    
    💰 **Выигрыши:**
    - Если вы выбрали черный или красный, ставка удваивается.
    - Если вы выбрали зеленый, ставка умножается на 15!
    
    Удачи в игре! 🍀
    """
    await event.reply(rules)

# 🚫 Обнуление баланса (только для владельца)
@bot.on(events.NewMessage(pattern=r"\.снять"))
async def reset_balance(event):
    if event.sender_id not in ADMINS:
        await event.reply("⛔ У тебя нет прав на эту команду!")
        return

    if not event.is_reply:
        await event.reply("⚠️ Ответь на сообщение игрока для сброса баланса!")
        return

    reply_msg = await event.get_reply_message()
    target_id = reply_msg.sender_id

    cursor.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (target_id,))
    conn.commit()
    await event.reply(f"❌ Баланс игрока {reply_msg.sender.first_name} обнулён!")

# ✅ Запуск
with bot:
    bot.run_until_disconnected()
