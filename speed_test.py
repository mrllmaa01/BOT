import time
import logging
import asyncio
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Тестируем скорость импорта библиотек"""
    logger.info("="*50)
    logger.info("ТЕСТИРОВАНИЕ СКОРОСТИ ИМПОРТОВ")
    logger.info("="*50)
    
    # Тест 1: Стандартные библиотеки
    start = time.time()
    import random
    import datetime
    logger.info(f"📦 Стандартные библиотеки: {time.time()-start:.3f}с")
    
    # Тест 2: aiogram
    start = time.time()
    from aiogram import Bot, Dispatcher
    logger.info(f"📦 aiogram: {time.time()-start:.3f}с")
    
    # Тест 3: numpy (тяжелый)
    start = time.time()
    try:
        import numpy
        logger.info(f"📦 numpy: {time.time()-start:.3f}с")
    except ImportError:
        logger.info("❌ numpy не установлен")
    
    # Тест 4: matplotlib (очень тяжелый)
    start = time.time()
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        logger.info(f"📦 matplotlib: {time.time()-start:.3f}с")
    except ImportError:
        logger.info("❌ matplotlib не установлен")
    
    # Тест 5: database
    start = time.time()
    from database import init_db
    logger.info(f"📦 database: {time.time()-start:.3f}с")
    
    # Тест 6: emotion_analyzer
    start = time.time()
    from emotion_analyzer import analyze_text, analyzer
    logger.info(f"📦 emotion_analyzer: {time.time()-start:.3f}с")

def test_disk_speed():
    """Тестируем скорость диска"""
    logger.info("\n" + "="*50)
    logger.info("ТЕСТИРОВАНИЕ СКОРОСТИ ДИСКА")
    logger.info("="*50)
    
    # Тест записи
    start = time.time()
    with open("test_write.tmp", "w") as f:
        for i in range(10000):
            f.write(f"test line {i}\n")
    logger.info(f"💾 Запись 10000 строк: {time.time()-start:.3f}с")
    
    # Тест чтения
    start = time.time()
    with open("test_write.tmp", "r") as f:
        lines = f.readlines()
    logger.info(f"📖 Чтение 10000 строк: {time.time()-start:.3f}с")
    
    os.remove("test_write.tmp")

async def test_network():
    """Тестируем скорость сети"""
    logger.info("\n" + "="*50)
    logger.info("ТЕСТИРОВАНИЕ СЕТИ")
    logger.info("="*50)
    
    import aiohttp
    
    # Тест Telegram API
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.telegram.org") as resp:
                logger.info(f"🌐 Telegram API: {time.time()-start:.3f}с (статус: {resp.status})")
    except Exception as e:
        logger.info(f"❌ Telegram API ошибка: {e}")
    
    # Тест случайного сайта
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://google.com") as resp:
                logger.info(f"🌐 Google: {time.time()-start:.3f}с (статус: {resp.status})")
    except Exception as e:
        logger.info(f"❌ Google ошибка: {e}")

def test_cpu():
    """Тестируем CPU"""
    logger.info("\n" + "="*50)
    logger.info("ТЕСТИРОВАНИЕ CPU")
    logger.info("="*50)
    
    # Простой тест
    start = time.time()
    result = 0
    for i in range(10_000_000):
        result += i
    logger.info(f"⚙️ 10 млн операций: {time.time()-start:.3f}с")

if __name__ == "__main__":
    logger.info("🚀 ЗАПУСК ПОЛНОЙ ДИАГНОСТИКИ\n")
    
    test_imports()
    test_disk_speed()
    asyncio.run(test_network())
    test_cpu()
    
    logger.info("\n" + "="*50)
    logger.info("ДИАГНОСТИКА ЗАВЕРШЕНА")
    logger.info("="*50)