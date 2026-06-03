import sqlite3

conn = sqlite3.connect("game_mods.db")
cursor = conn.cursor()

# Добавляем новые колонки в таблицу users
try:
    cursor.execute("ALTER TABLE users ADD COLUMN last_subscription_check TEXT")
    print("✅ Добавлена колонка last_subscription_check в users")
except:
    print("Колонка last_subscription_check уже существует")

# Добавляем новые колонки в таблицу channels
try:
    cursor.execute("ALTER TABLE channels ADD COLUMN is_active INTEGER DEFAULT 1")
    print("✅ Добавлена колонка is_active в channels")
except:
    print("Колонка is_active уже существует")

try:
    cursor.execute("ALTER TABLE channels ADD COLUMN in_weekly_rotation INTEGER DEFAULT 1")
    print("✅ Добавлена колонка in_weekly_rotation в channels")
except:
    print("Колонка in_weekly_rotation уже существует")

conn.commit()
conn.close()

print("\n✅ База данных успешно обновлена!")
print("Теперь можно запускать бота.")