# simple_test.py
print("🟢 Запуск simple_test.py")

try:
    from config import BOT_TOKEN
    print(f"🟢 Токен импортирован: {BOT_TOKEN[:10]}...")
    print("✅ Всё работает!")
except Exception as e:
    print(f"🔴 Ошибка импорта: {e}")

input("Нажми Enter для выхода...")