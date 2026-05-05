print("ШАГ 1: Скрипт начал работу")
import sys
print("ШАГ 2: sys импортирован")
sys.stdout.flush()

print("ШАГ 3: Пытаюсь импортировать asyncio")
import asyncio
print("ШАГ 4: asyncio импортирован")

print("ШАГ 5: Пытаюсь импортировать logging")
import logging
print("ШАГ 6: logging импортирован")

print("ШАГ 7: Пытаюсь импортировать aiogram")
try:
    from aiogram import Bot, Dispatcher
    print("ШАГ 8: aiogram импортирован")
except Exception as e:
    print(f"ОШИБКА при импорте aiogram: {e}")

print("ШАГ 9: Пытаюсь импортировать config")
try:
    from config import BOT_TOKEN
    print(f"ШАГ 10: Токен загружен, длина: {len(BOT_TOKEN)} символов")
except Exception as e:
    print(f"ОШИБКА при импорте config: {e}")

print("ШАГ 11: Скрипт завершен")
sys.stdout.flush()

input("Нажми Enter для выхода...")