from database import db

# Добавляем тестовые материалы
db.add_material("minecraft", "⭐ Супер мод на алмазы", "diamonds = 1000\niron = 500\ngold = 300\nemerald = 50")

db.add_material("minecraft", "⚡ Оптимизация FPS", "render_distance = 16\nmax_fps = 144\nvsync = false\nsmooth_lighting = false")

db.add_material("roblox", "🤖 Автоферма скрипт", """while true do
    wait(1)
    local args = {[1] = "Collect"}
    game:GetService("ReplicatedStorage"):WaitForChild("Events"):WaitForChild("Collect"):FireServer(unpack(args))
    print("Собрано ресурсов!")
end""")

db.add_material("roblox", "📖 Гайд по установке скриптов", """1. Скачай executor (Krnl, Synapse, Fluxus)
2. Запусти Roblox и войди в игру
3. Открой executor
4. Вставь скрипт в поле ввода
5. Нажми Execute (Inject)
6. Готово! Скрипт работает автоматически""")

db.add_material("terraria", "🏆 Лучшая экипировка", """Броня: Solar Flare
Оружие: Zenith, Last Prism
Аксессуары: 
- Celestial Shell
- Ankh Shield
- Master Ninja Gear
- Wings (Solar или Fishron)""")

print("✅ Тестовые материалы добавлены!")
print("\n📋 Список игр в базе:")
for game in db.get_all_games():
    print(f"  • {game.capitalize()}")