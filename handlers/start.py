from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from database import add_user, init_db

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    
    # Инициализируем БД при первом запуске
    init_db()
    
    # Сохраняем пользователя
    add_user(user_id, username, first_name, last_name)
    
    await message.answer(
        f"Привет, {first_name}! 👋\n"
        "Я бот, который поможет понять твоё настроение "
        "и предложить способы расслабиться.\n\n"
        "Просто напиши мне, что ты чувствуешь, "
        "а я постараюсь помочь!"
    )