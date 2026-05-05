# Пробуем импортировать токен
try:
    from config import BOT_TOKEN
    print(f"✅ Импорт успешен! Токен: {BOT_TOKEN[:10]}...")
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")