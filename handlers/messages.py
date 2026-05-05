from aiogram import Router
from aiogram.types import Message
from database import save_message, get_user_history

router = Router()

@router.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text
    
    if not text:
        await message.answer("Пожалуйста, напиши текстовое сообщение")
        return
    
    # Сохраняем сообщение
    save_message(user_id, text)
    
    await message.answer(
        f"📝 Я записал твоё сообщение: \"{text}\"\n\n"
        "Скоро я научусь понимать твои эмоции!"
    )