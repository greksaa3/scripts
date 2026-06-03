import sqlite3

conn = sqlite3.connect("game_mods.db")
cursor = conn.cursor()

# Пересоздаём таблицу scripts (без поля game)
cursor.execute("DROP TABLE IF EXISTS scripts")
cursor.execute("""
    CREATE TABLE scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        code TEXT,
        added_date TEXT
    )
""")

# Тестовые скрипты
test_scripts = [
    ("Dead Rails: Auto Farm X", """
-- Dead Rails Auto Farm
local player = game.Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()

while wait(0.1) do
    for _, v in pairs(workspace:GetChildren()) do
        if v.Name == "Rail" then
            character.HumanoidRootPart.CFrame = v.CFrame
            wait(0.3)
        end
    end
end
"""),
    ("Dead Rails: God Mode", """
-- Dead Rails God Mode
local player = game.Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()
local humanoid = character:WaitForChild("Humanoid")

humanoid.MaxHealth = math.huge
humanoid.Health = math.huge
"""),
    ("Blade Ball: ESP Plus", """
-- Blade Ball ESP
local players = game:GetService("Players")
local localPlayer = players.LocalPlayer

for _, player in pairs(players:GetPlayers()) do
    if player ~= localPlayer then
        local highlight = Instance.new("Highlight")
        highlight.Parent = player.Character
        highlight.FillColor = Color3.new(1, 0, 0)
    end
end
"""),
    ("TSB: Speed Hack", """
-- The Strongest Battlegrounds Speed Hack
local player = game.Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()
local humanoid = character:WaitForChild("Humanoid")

humanoid.WalkSpeed = 50
humanoid.JumpPower = 80
"""),
]

for name, code in test_scripts:
    cursor.execute("""
        INSERT INTO scripts (name, code, added_date)
        VALUES (?, ?, datetime('now'))
    """, (name, code))

conn.commit()
conn.close()

print("✅ База данных готова!")
print(f"📚 Добавлено {len(test_scripts)} скриптов")
print("\n🚀 Запускай бота: python bot.py")