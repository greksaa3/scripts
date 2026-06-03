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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище для поиска
search_results = {}
search_mode = {}

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
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

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

# ==================== ОСНОВНЫЕ КОМАНДЫ ====================
@dp.message(Command("start"))
async def start(message: types.Message):
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    is_admin = (message.from_user.id == ADMIN_ID)
    await message.answer(
        f"🎮 *ROBLOX SCRIPT HUB*\n\nПривет, {message.from_user.first_name}!\n\n📚 Здесь ты найдёшь скрипты для Roblox\n\nИспользуй кнопки ниже:",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(is_admin)
    )

@dp.message(F.text == "📜 Все скрипты")
async def all_scripts(message: types.Message):
    scripts = db.get_all_scripts()
    if not scripts:
        await message.answer("📭 Пока нет скриптов!")
        return
    search_results[message.from_user.id] = scripts
    keyboard, total = get_paginated_keyboard(scripts, 1, 5)
    await message.answer(f"📚 *Все скрипты* - {len(scripts)} шт.\n📄 Страница 1 из {total}", parse_mode="Markdown",
                         reply_markup=keyboard)

@dp.message(F.text == "🔎 Поиск")
async def search_start(message: types.Message):
    search_mode[message.from_user.id] = True
    await message.answer("🔍 *Введи название скрипта:*\n\nПример: `Auto Farm`, `ESP`, `Speed`", parse_mode="Markdown")

@dp.message(F.text == "📖 Помощь")
async def help_command(message: types.Message):
    await message.answer(
        "📚 *Помощь*\n\n"
        "📜 Все скрипты - показать все скрипты\n"
        "🔎 Поиск - найти по названию\n\n"
        "*Как использовать:*\n"
        "1. Скачай executor (Krnl, Synapse, Fluxus)\n"
        "2. Запусти Roblox\n"
        "3. Скопируй скрипт\n"
        "4. Вставь в executor\n"
        "5. Нажми Execute\n\n"
        "⚠️ На свой страх и риск!",
        parse_mode="Markdown"
    )

# ==================== ОБРАБОТЧИК ПОИСКА ====================
@dp.message(F.text)
async def handle_search(message: types.Message):
    user_id = message.from_user.id
    
    # Если пользователь в режиме поиска
    if search_mode.get(user_id):
        del search_mode[user_id]
        
        # Логируем поисковый запрос (если включен LOG_CHANNEL_ID)
        if LOG_CHANNEL_ID and user_id != ADMIN_ID:
            try:
                now = datetime.now().strftime("%H:%M:%S")
                await bot.send_message(
                    chat_id=LOG_CHANNEL_ID,
                    text=f"🔍 *Поиск*\n🕒 {now}\n👤 {message.from_user.first_name}\n📛 @{message.from_user.username or 'нет'}\n💬 `{message.text[:500]}`",
                    parse_mode="Markdown"
                )
            except:
                pass
        
        results = db.search_scripts(message.text)
        if not results:
            await message.answer(f"❌ Ничего не найдено по запросу '{message.text}'")
            return
        search_results[user_id] = results
        keyboard, total = get_paginated_keyboard(results, 1, 5)
        await message.answer(f"🔍 *Результаты:* {len(results)} скриптов\n📄 Страница 1 из {total}", parse_mode="Markdown",
                             reply_markup=keyboard)
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
    await callback.message.answer(
        f"📜 *{name}*\n\n```lua\n{code}\n```",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("page_"))
async def paginate(callback: types.CallbackQuery):
    page = int(callback.data.replace("page_", ""))
    scripts = search_results.get(callback.from_user.id, db.get_all_scripts())
    if not scripts:
        await callback.answer("Устарело", show_alert=True)
        return
    keyboard, total = get_paginated_keyboard(scripts, page, 5)
    await callback.message.edit_text(
        f"📚 *Скрипты*\n📄 Страница {page} из {total}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

# ==================== АДМИН ПАНЕЛЬ (РАБОЧАЯ!) ====================
admin_states = {}

@dp.message(F.text == "👑 Админ панель")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для этого действия!")
        return
    await message.answer("👑 Админ панель", reply_markup=get_admin_keyboard())

@dp.message(F.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Главное меню:", reply_markup=get_main_keyboard(True))

@dp.message(F.text == "➕ Добавить скрипт")
async def add_script_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_states[message.from_user.id] = {"step": "name"}
    await message.answer("📝 *Введи название скрипта:*\nПример: `Auto Farm X`", parse_mode="Markdown")

@dp.message(F.text == "📋 Список скриптов")
async def list_scripts(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    scripts = db.get_all_scripts()
    if not scripts:
        await message.answer("📭 Нет скриптов")
        return
    buttons = []
    for s in scripts:
        short_name = s[1][:30] + "..." if len(s[1]) > 30 else s[1]
        buttons.append([InlineKeyboardButton(text=f"❌ {short_name}", callback_data=f"del_{s[0]}")])
    await message.answer("📋 *Список скриптов* (нажми для удаления):", parse_mode="Markdown",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.message(F.text == "📢 Рассылка")
async def broadcast_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_states[message.from_user.id] = {"step": "broadcast"}
    await message.answer("📢 Отправь сообщение для рассылки:")

# Админский ввод
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
        await message.answer("💻 *Шаг 2/2:* Отправь LUA код скрипта", parse_mode="Markdown")
    elif step == "code":
        db.add_script(state["name"], message.text)
        await message.answer(f"✅ *Скрипт добавлен!*\n\n📜 {state['name']}", parse_mode="Markdown")
        del admin_states[user_id]
    elif step == "broadcast":
        users = db.get_all_users()
        if not users:
            await message.answer("❌ Нет пользователей для рассылки!")
            del admin_states[user_id]
            return
        status = await message.answer(f"📡 Рассылка для {len(users)} пользователей...")
        success, fail = 0, 0
        for i, user in enumerate(users):
            try:
                await message.copy_to(user[0])
                success += 1
            except:
                fail += 1
            if i % 10 == 0:
                await asyncio.sleep(0.5)
        await status.edit_text(f"✅ Рассылка завершена!\n✅ Успешно: {success}\n❌ Ошибок: {fail}")
        del admin_states[user_id]

# Удаление скриптов
@dp.callback_query(lambda c: c.data and c.data.startswith("del_"))
async def delete_script(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав!", show_alert=True)
        return
    script_id = int(callback.data.replace("del_", ""))
    db.delete_script(script_id)
    await callback.message.edit_text("✅ Скрипт удалён!")
    await callback.answer()

# ==================== ЗАПУСК ====================
async def main():
    print("🚀 ROBLOX SCRIPT HUB запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
