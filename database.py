import sqlite3
from datetime import datetime



class Database:
    def __init__(self, db_name="game_mods.db"):
        self.db_name = db_name
        self.create_tables()

    def create_tables(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    is_premium INTEGER DEFAULT 0,
                    joined_date TEXT,
                    last_subscription_check TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER UNIQUE,
                    channel_username TEXT,
                    channel_name TEXT,
                    added_date TEXT,
                    is_active INTEGER DEFAULT 1,
                    in_weekly_rotation INTEGER DEFAULT 1
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    code TEXT,
                    added_date TEXT
                )
            """)

            conn.commit()
            print("✅ База данных готова!")

    # ============ ПОЛЬЗОВАТЕЛИ ============
    def add_user(self, user_id, username, first_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, datetime.now().isoformat()))
            conn.commit()

    def get_all_users(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            return [row[0] for row in cursor.fetchall()]

    def set_premium(self, user_id, is_premium):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_premium = ? WHERE user_id = ?",
                           (1 if is_premium else 0, user_id))
            conn.commit()

    def get_premium(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_premium FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] == 1 if result else False

    def get_user_last_check(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_subscription_check FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_user_check_time(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_subscription_check = ? 
                WHERE user_id = ?
            """, (datetime.now().isoformat(), user_id))
            conn.commit()

    # ============ СКРИПТЫ ============
    def add_script(self, name, code):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scripts (name, code, added_date)
                VALUES (?, ?, ?)
            """, (name, code, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def get_all_scripts(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, code FROM scripts ORDER BY added_date DESC")
            return cursor.fetchall()

    def search_scripts(self, query):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, code 
                FROM scripts 
                WHERE name LIKE ?
                ORDER BY added_date DESC
            """, (f"%{query}%",))
            return cursor.fetchall()

    def get_script_by_id(self, script_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, code FROM scripts WHERE id = ?", (script_id,))
            return cursor.fetchone()

    def delete_script(self, script_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scripts WHERE id = ?", (script_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ============ КАНАЛЫ ============
    def add_channel(self, channel_id, channel_username, channel_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO channels (channel_id, channel_username, channel_name, added_date, is_active, in_weekly_rotation)
                    VALUES (?, ?, ?, ?, 1, 1)
                """, (channel_id, channel_username, channel_name, datetime.now().isoformat()))
                conn.commit()
                return True
            except:
                return False

    def get_all_channels(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, channel_id, channel_username, channel_name, is_active, in_weekly_rotation FROM channels")
            return cursor.fetchall()

    def get_active_channels(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT channel_id, channel_username, channel_name 
                FROM channels WHERE is_active = 1
            """)
            return cursor.fetchall()

    def get_weekly_rotation_channels(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT channel_id, channel_username, channel_name 
                FROM channels 
                WHERE is_active = 1 AND in_weekly_rotation = 1
                ORDER BY RANDOM() LIMIT 3
            """)
            return cursor.fetchall()

    def remove_channel(self, channel_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
            conn.commit()
            return cursor.rowcount > 0


db = Database()