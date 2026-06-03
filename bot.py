import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import db

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
if LOG_CHANNEL_ID:
    LOG_CHANNEL_ID = int(LOG_CHANNEL_ID)
else:
    LOG_CHANNEL_ID = None

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище для поиска
search_results = {}
search_mode = {}  # Кто сейчас в режиме поиска

# Лимиты на запросы от одного пользователя
user_requests = {}

def check_rate_limit(user_id):
    """Защита от спама - не более 1 запроса в секунду. Админ не ограничен."""
    if user_id == ADMIN_ID:
        return True
    
    now = datetime.now()
    if user_id not in user_requests:
        user_requests[user_id] = []

    user_requests[user_id] = [t for t in user_requests[user_id] if (now - t).seconds < 1]

    if len(user_requests[user_id]) >= 1:
        return False

    user_requests[user_id].append(now)
    return True

# ==================== ЛОГИРОВАНИЕ ====================
async def log_to_channel(user_id, username, first_name, text):
    """Отправляет лог в Telegram канал"""
    if not LOG_CHANNEL_ID or user_id == ADMIN_ID:
        return
    try:
        now = datetime.now().strftime("%H:%M:%S")
        log_text = (
            f"📨 *Новое сообщение*\n"
            f"🕒 `{now}`\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Имя: {first_name}\n"
            f"📛 Юзернейм: @{username if username else 'нет'}\n"
            f"💬 Текст:\n`{text[:500]}`"
        )
        await bot.send_message(chat_id=LOG_CHANNEL_ID, text=log_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Лог ошибка: {e}")

# ==================== КЛАВИАТУРЫ ====================
def get_main_keyboard(is_admin=False):
    buttons = [
        [KeyboardButton(text="📜 Все скрипты")],
        [KeyboardButton(text="🔎 Поиск")],
        [KeyboardButton(text="📖 Помощь")]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Админ панель")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_keyboard():
    buttons = [
        [KeyboardButton(text="➕ Добавить скрипт")],
        [KeyboardButton(text="📋 Список скриптов")],
        [KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="➕ Добавить канал")],
        [KeyboardButton(text="❌ Удалить канал")],
        [KeyboardButton(text="⭐ Выдать премиум")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_subscription_keyboard(channels):
    buttons = []
    for channel_data in channels:
        channel_id, channel_username, channel_name = channel_data
        if channel_username and channel_username != "":
            link = f"https://t.me/{channel_username}"
        else:
            link = f"https://t.me/c/{str(channel_id)[4:]}"
        buttons.append([InlineKeyboardButton(text=f"📢 Подписаться: {channel_name}", url=link)])
    buttons.append([InlineKeyboardButton(text="🔄 Проверить подписку", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_paginated_keyboard(items, page, items_per_page=5):
    if not items:
        return InlineKeyboardMarkup(inline_keyboard=[]), 1
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = start + items_per_page
    current_items = items[start:end]

    keyboard = []
    for item in current_items:
        script_id, name = item[0], item[1]
        short_name = name[:35] + "..." if len(name) > 35 else name
        keyboard.append([InlineKeyboardButton(text=f"📜 {short_name}", callback_data=f"script_{script_id}")])

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard), total_pages

# ==================== ПРОВЕРКА ПОДПИСКИ (ВРЕМЕННО ОТКЛЮЧЕНА) ====================
async def check_and_force_subscription(message):
    """Временно отключено — все пользователи имеют доступ"""
    return True

# ==================== ОСНОВНЫЕ КОМАНДЫ ====================
@dp.message(Command("start"))
async def start(message: types.Message):
    if not check_rate_limit(message.from_user.id):
        await message.answer("⏳ Подожди секунду.")
        return
    
    await log_to_channel(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        "/start"
    )
    
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    has_access = await check_and_force_subscription(message)
    if not has_access:
        return
    await message.answer(
        f"🎮 *ROBLOX SCRIPT HUB*\n\nПривет, {message.from_user.first_name}!\n\n📚 Используй кнопки ниже:",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(message.from_user.id == ADMIN_ID)
    )

@dp.message(F.text == "📜 Все скрипты")
async def all_scripts(message: types.Message):
    if not check_rate_limit(message.from_user.id):
        await message.answer("⏳ Подожди секунду.")
        return
    
    await log_to_channel(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        "📜 Все скрипты"
    )
    
    scripts = db.get_all_scripts()
    if not scripts:
        await message.answer("📭 Пока нет скриптов!")
        return
    search_results[message.from_user.id] = scripts
    keyboard, total = get_paginated_keyboard(scripts, 1, 5)
    await message.answer(f"📚 *Скрипты* - {len(scripts)} шт.\n📄 Страница 1 из {total}", parse_mode="Markdown",
                         reply_markup=keyboard)

@dp.message(F.text == "🔎 Поиск")
async def search_start(message: types.Message):
    if not check_rate_limit(message.from_user.id):
        await message.answer("⏳ Подожди секунду.")
        return
    
    await log_to_channel(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        "🔎 Поиск"
    )
    
    search_mode[message.from_user.id] = True
    await message.answer("🔍 *Введи название скрипта:*\n\nПример: `Auto Farm`", parse_mode="Markdown")

@dp.message(F.text == "📖 Помощь")
async def help_command(message: types.Message):
    if not check_rate_limit(message.from_user.id):
        await message.answer("⏳ Подожди секунду.")
        return
    
    await log_to_channel(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        "📖 Помощь"
    )
    
    await message.answer(
        "📚 *Помощь*\n\n"
        "📜 Все скрипты - показать скрипты\n"
        "🔎 Поиск - найти по названию\n\n"
        "*Как использовать:*\n"
        "1. Скачай executor\n"
        "2. Скопируй скрипт\n"
        "3. Вставь и Execute\n\n"
        "⚠️ На свой страх и риск!",
        parse_mode="Markdown"
    )

# ==================== ОБРАБОТЧИК ПОИСКА ====================
@dp.message(F.text)
async def handle_search(message: types.Message):
    user_id = message.from_user.id
    
    # Логируем всё, кроме команд админа
    if user_id != ADMIN_ID or user_id not in admin_states:
        await log_to_channel(user_id, message.from_user.username, message.from_user.first_name, message.text)
    
    # Проверка спама
    if not check_rate_limit(user_id):
        await message.answer("⏳ Подожди секунду.")
        if search_mode.get(user_id):
            del search_mode[user_id]
        return
    
    # Режим поиска
    if search_mode.get(user_id):
        del search_mode[user_id]
        results = db.search_scripts(message.text)
        if not results:
            await message.answer(f"❌ Ничего не найдено по '{message.text}'")
            return
        search_results[user_id] = results
        keyboard, total = get_paginated_keyboard(results, 1, 5)
        await message.answer(f"🔍 *Результаты:* {len(results)} скриптов\n📄 Страница 1 из {total}", 
                             parse_mode="Markdown", reply_markup=keyboard)
        return

# ==================== КОЛБЭКИ ====================
@dp.callback_query(lambda c: c.data and c.data.startswith("script_"))
async def view_script(callback: types.CallbackQuery):
    script_id = int(callback.data.replace("script_", ""))
    script = db.get_script_by_id(script_id)
    if not script:
        await callback.answer("Скрипт не найден!", show_alert=True)
        return
    _, name, code = script
    await callback.message.answer(f"📜 *{name}*\n\n```lua\n{code}\n```", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("page_"))
async def paginate(callback: types.CallbackQuery):
    page = int(callback.data.replace("page_", ""))
    scripts = search_results.get(callback.from_user.id, db.get_all_scripts())
    if not scripts:
        await callback.answer("Устарело", show_alert=True)
        return
    keyboard, total = get_paginated_keyboard(scripts, page, 5)
    await callback.message.edit_text(f"📚 *Скрипты*\n📄 Страница {page} из {total}",
                                     parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

# ==================== АДМИН ПАНЕЛЬ ====================
@dp.message(F.text == "👑 Админ панель")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав!")
        return
    await message.answer("👑 Админ панель", reply_markup=get_admin_keyboard())

@dp.message(F.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав!", reply_markup=get_main_keyboard(False))
        return
    await message.answer("Главное меню:", reply_markup=get_main_keyboard(True))

admin_states = {}

@dp.message(F.text == "➕ Добавить скрипт")
async def add_script_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав!")
        return
    admin_states[message.from_user.id] = {"step": "name"}
    await message.answer("📝 *Введи название скрипта:*\nПример: `Auto Farm`", parse_mode="Markdown")

@dp.message(F.text == "📋 Список скриптов")
async def list_scripts(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    scripts = db.get_all_scripts()
    if not scripts:
        await message.answer("📭 Нет скриптов")
        return
    buttons = [[InlineKeyboardButton(text=f"❌ {s[1][:30]}", callback_data=f"del_{s[0]}")] for s in scripts]
    await message.answer("📋 *Скрипты* (нажми для удаления):", parse_mode="Markdown",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.message(F.text == "📢 Рассылка")
async def broadcast_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_states[message.from_user.id] = {"step": "broadcast"}
    await message.answer("📢 Отправь сообщение для рассылки:")

@dp.message(F.text == "➕ Добавить канал")
async def add_channel_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_states[message.from_user.id] = {"step": "channel_id"}
    await message.answer("📢 Введи ID канала (число):")

@dp.message(F.text == "❌ Удалить канал")
async def remove_channel_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    channels = db.get_all_channels()
    if not channels:
        await message.answer("📭 Нет каналов")
        return
    buttons = [[InlineKeyboardButton(text=f"❌ {ch[2]}", callback_data=f"delchan_{ch[0]}")] for ch in channels]
    await message.answer("Выбери канал:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.message(F.text == "⭐ Выдать премиум")
async def give_premium_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_states[message.from_user.id] = {"step": "premium"}
    await message.answer("👤 Введи ID пользователя:")

# ==================== АДМИНСКИЙ ВВОД ====================
@dp.message(F.text)
async def admin_input(message: types.Message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID or user_id not in admin_states:
        return
    
    state = admin_states[user_id]
    step = state.get("step")

    if step == "name":
        state["name"] = message.text.strip()
        state["step"] = "code"
        await message.answer("💻 *Отправь LUA код:*", parse_mode="Markdown")
    elif step == "code":
        db.add_script(state["name"], message.text)
        await message.answer(f"✅ Скрипт *{state['name']}* добавлен!", parse_mode="Markdown")
        del admin_states[user_id]
    elif step == "channel_id":
        try:
            state["channel_id"] = int(message.text)
            state["step"] = "channel_username"
            await message.answer("📢 Введи username канала (или 'нет'):")
        except ValueError:
            await message.answer("❌ Введи число!")
    elif step == "channel_username":
        username = message.text.lower()
        if username == "нет":
            username = ""
        state["channel_username"] = username
        state["step"] = "channel_name"
        await message.answer("📢 Введи название канала:")
    elif step == "channel_name":
        db.add_channel(state["channel_id"], state["channel_username"], message.text)
        await message.answer("✅ Канал добавлен!")
        del admin_states[user_id]
    elif step == "premium":
        try:
            uid = int(message.text)
            db.set_premium(uid, True)
            await message.answer(f"✅ Премиум выдан {uid}!")
        except ValueError:
            await message.answer("❌ Введи ID!")
        del admin_states[user_id]
    elif step == "broadcast":
        users = db.get_all_users()
        if not users:
            await message.answer("❌ Нет пользователей!")
            del admin_states[user_id]
            return
        status = await message.answer(f"📡 Рассылка для {len(users)} пользователей...")
        success, fail = 0, 0
        for i, uid in enumerate(users):
            try:
                await message.copy_to(uid[0])
                success += 1
            except:
                fail += 1
            if i % 10 == 0:
                await asyncio.sleep(0.5)
        await status.edit_text(f"✅ Готово! Успешно: {success}, Ошибок: {fail}")
        del admin_states[user_id]

@dp.callback_query(lambda c: c.data and c.data.startswith("del_"))
async def delete_script(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав!", show_alert=True)
        return
    script_id = int(callback.data.replace("del_", ""))
    db.delete_script(script_id)
    await callback.message.edit_text("✅ Скрипт удалён!")
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("delchan_"))
async def delete_channel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав!", show_alert=True)
        return
    channel_id = int(callback.data.replace("delchan_", ""))
    db.remove_channel(channel_id)
    await callback.message.edit_text("✅ Канал удалён!")
    await callback.answer()

# ==================== ЗАПУСК ====================
async def main():
    print("🚀 ROBLOX SCRIPT HUB запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
