import asyncio
import logging
import random
import matplotlib.pyplot as plt
import io

from aiogram.types import BufferedInputFile
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from database import init_db, add_user, save_message, update_message_emotion, save_diary_entry, get_diary_entries, get_emotion_stats, get_week_emotions
from config import BOT_TOKEN
from emotion_analyzer import analyze_text, analyzer

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем БД
init_db()

# Временное хранилище
user_last_emotion = {}
user_last_emotion_display = {}
user_last_bot_message = {}

# ===== ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ КОТИКА =====
def get_cat_url(emotion=None):
    base_url = "https://cataas.com/cat"
    
    tags = {
        'грусть': 'sad',
        'злость': 'angry',
        'страх': 'scared',
        'радость': 'happy',
        'удивление': 'surprised',
        'любовь': 'love',
        'усталость': 'sleep',
        'нейтрально': 'cute',
        'обида': 'sad',
        'вина': 'sad',
        'гордость': 'happy',
        'вдохновение': 'happy',
        'интерес': 'cute',
        'скука': 'sleep',
        'раздражение': 'angry',
        'отвращение': 'angry',
        'надежда': 'happy',
        'спокойствие': 'cute'
    }
    
    if emotion and emotion in tags:
        return f"{base_url}/{tags[emotion]}?{random.randint(1, 1000)}"
    
    return f"{base_url}?{random.randint(1, 1000)}"

def get_random_cat():
    return f"https://cataas.com/cat?{random.randint(1, 1000)}"

# ========== СЛОВАРЬ ФИЛЬМОВ ==========
MOVIES = {
    'радость': [
        "🎬 **1+1 (2011)** — Французская комедия-драма о дружбе, которая заставляет улыбаться",
        "🎬 **Вверх (2009)** — Мультфильм о путешествии и мечтах",
        "🎬 **Ла-Ла Ленд (2016)** — Красочный мюзикл о любви и мечтах",
        "🎬 **Всегда говори «ДА» (2008)** — Комедия с Джимом Керри",
        "🎬 **Амели (2001)** — Добрая французская комедия"
    ],
    'грусть': [
        "🎬 **Великий Гэтсби (2013)** — Трагическая история любви и богатства",
        "🎬 **Вечное сияние чистого разума (2004)** — Грустный фильм о любви и памяти",
        "🎬 **Дневник памяти (2004)** — Пронзительная история любви",
        "🎬 **Зеленая книга (2018)** — Трогательная драма о дружбе",
        "🎬 **Малифисента (2014)** — Красивая грустная сказка"
    ],
    'злость': [
        "🎬 **Джанго освобожденный (2012)** — Тарантино, месть и справедливость",
        "🎬 **Гнев человеческий (2021)** — Боевик с Джейсоном Стэтхэмом",
        "🎬 **Джон Уик (2014)** — Экшен про месть",
        "🎬 **Бойцовский клуб (1999)** — Выплеск агрессии и протест",
        "🎬 **Гладиатор (2000)** — Эпическая история мести"
    ],
    'страх': [
        "🎬 **Молчание ягнят (1991)** — Психологический триллер",
        "🎬 **Побег из Шоушенка (1994)** — Драма о надежде в страшных обстоятельствах",
        "🎬 **Остров проклятых (2010)** — Триллер с неожиданным финалом",
        "🎬 **Начало (2010)** — Сложный сюжет, держащий в напряжении",
        "🎬 **Шестое чувство (1999)** — Мистический триллер"
    ],
    'удивление': [
        "🎬 **Доктор Стрэндж (2016)** — Визуальные эффекты и мультивселенные",
        "🎬 **Матрица (1999)** — Открыла новую реальность",
        "🎬 **Интерстеллар (2014)** — Космос и время",
        "🎬 **Аватар (2009)** — Невероятный мир Пандоры",
        "🎬 **Форрест Гамп (1994)** — Удивительная жизнь простого человека"
    ],
    'любовь': [
        "🎬 **Титаник (1997)** — Эпическая история любви",
        "🎬 **Гордость и предубеждение (2005)** — Красивая экранизация",
        "🎬 **Реальная любовь (2003)** — Несколько историй о любви",
        "🎬 **До встречи с тобой (2016)** — Романтическая драма",
        "🎬 **Вам письмо (1998)** — Романтическая комедия"
    ],
    'усталость': [
        "🎬 **Ешь, молись, люби (2010)** — Путешествие к себе",
        "🎬 **Дикая (2014)** — Поход и поиск себя",
        "🎬 **Мирный воин (2006)** — Фильм про внутренний покой",
        "🎬 **Секрет (2006)** — О силе мысли и отдыхе",
        "🎬 **Джули и Джулия (2009)** — Уютная кулинарная история"
    ],
    'нейтрально': [
        "🎬 **Назад в будущее (1985)** — Классика для хорошего настроения",
        "🎬 **Один дома (1990)** — Семейная комедия",
        "🎬 **Гарри Поттер (любая часть)** — Волшебство для всех",
        "🎬 **Властелин колец (2001)** — Эпическое фэнтези",
        "🎬 **Тайна Коко (2017)** — Красивый мультфильм о семье"
    ]
}

# ========== СЛОВАРЬ УПРАЖНЕНИЙ ==========
EXERCISES = {
    'злость':[
        "😤 **«Разрывание ткани»**\n\nВозьми старое полотенце или простыню. Встань, ноги на ширине плеч. Представь, что это то, что тебя сдерживает. С рыком или мощным выдохом пытайся разорвать ткань руками, скручивая ее в жгут. Делай это 1–2 минуты. Если ткань не рвется — это даже лучше: ты вкладываешь силу в действие, а не в разрушение.",
        "💢 **«Гневный топот»**\n\nВстань прямо. Начинай поочередно с силой опускать ноги на пол, как будто ты что-то утрамбовываешь. Каждый удар — с громким «Ха!» или «А ну!». Через 30 секунд добавь руки: кулаки сжаты, ударяешь ими по воздуху перед собой. 2 минуты интенсивного топота с криком снимают мышечный панцирь в ногах и челюсти.",
        "🧊 **«Сжимание-разжимание»**\n\nСядь на стул. С силой сожми кулаки, напряги все тело — лицо, плечи, ноги. Посчитай до 5, чувствуя, как дрожат мышцы. Затем резко выдохни «Фууух!», полностью расслабься, откинься на спинку стула, встряхни кистями. Повтори 10 раз. Это учит управлять включением и выключением злости."
    ],
    'грусть':[
        "🌧 **«Обними себя в наклоне»**\n\nСядь на пол, согни колени к груди, обхвати их руками. Спрячь лицо в коленях. Медленно покачивайся вперед-назад, как будто тебя укачивают. Дыши глубоко, в живот. Можно тихонько мычать или вздыхать. Это поза эмбриона, она дает разрешение на уязвимость.",
        "☀️ **«Медленное распрямление»**\n\nЛяг на спину. Очень медленно, позвонок за позвонком, начинай подниматься в положение сидя. Каждое движение — на выдохе. Не используй руки, если можешь. Дойдя до сидячего положения, посиди 30 секунд с закрытыми глазами, положив руку на сердце. Это метафора: «я поднимаюсь из тяжести, но не спешу».",
        "📝 **«Письмо телом»**\n\nВключи медленную, печальную музыку. Стоя на месте, «рисуй» в воздухе руками большие круги, как будто обводишь что-то невидимое. Добавь наклоны корпуса. Представь, что ты лепишь из воздуха форму своей грусти, а потом аккуратно отпускаешь ее вверх. 3–5 минут."
    ],
    'страх': [
        "😨 **«Застывший лучник»**\n\nВстань в широкий выпад. Медленно, с дрожью в руках, тяни воображаемый лук. На выдохе — резкий выстрел с громким звуком. Повтори 8 раз на каждую сторону. Страх превращается в сфокусированную силу.",
        "🤲 **«Дрожь зверя»**\n\nЛяг на спину, сожмись в комок. Начинай медленно трястись всем телом, как будто от холода или страха. Постепенно увеличивай амплитуду, добавляй звуки (дрожащий стон). Через 1–2 минуты резко распрямись, раскинь руки и ноги, сделай глубокий вдох — «вышел из укрытия».",
        "💪 **«Пять шагов в неизвестность»**\n\nЗавяжи глаза или закрой их. Сделай пять медленных шагов вперед, выставив руки перед собой. Каждый шаг — на вдохе. На выдохе — ощупай пространство вокруг себя ладонями. После пятого шага стой 30 секунд, слушая свое тело. Это тренировка доверия к себе в моменте неопределенности."
    ],
    'радость': [
        "🎉 **«Прыжки-обнимашки»**\n\nПрыгай на месте. Каждый третий прыжок — резко обними себя руками, сильно сжимая плечи, и громко скажи «Я тебя люблю!» или «Как же классно!». 1 минута. Соединяет взрывную радость с телесным теплом.",
        "💞 **«Дурная походка»**\n\nПридумай самую нелепую походку: на полусогнутых, с подпрыгиванием, с хлопками под коленкой. Пройди так по комнате туда-обратно 4 раза. Смысл — разрешить себе быть смешным и глупым без цели кого-то развлекать.",
        "💃 **«Танец маленьких побед»**\n\nВключи любую музыку. Танцуй, но каждые 15 секунд останавливайся и делай «победный жест» (руки вверх, кулак к груди) с громким «Да!». Даже если ты просто почесал нос в паузе — это повод для «победы». 2 минуты поднимают дофамин быстрее, чем любые тренажеры."
    ],
    'нейтрально': [
        "🚶 **«Медленная ходьба слона»**\n\nХоди по комнате очень медленно, делая полный перекат стопы с пятки на носок. Руки свободно висят или сложены на животе. Представь, что ты большое спокойное животное, которому некуда спешить. 3 минуты. Возвращает в тело, убирает ментальную суету.",
        "⚖️ **«Взвешивание рук»**\n\nВстань прямо. Подними руки в стороны на уровень плеч. Медленно, как весы, начинай переносить вес тела с одной ноги на другую, слегка наклоняя корпус. Руки остаются прямыми и расслабленными. 1–2 минуты. Создает ощущение внутреннего равновесия.",
        "🪑 **«Точка опоры»**\n\nСядь на стул, стопы плотно на полу. Закрой глаза. На вдохе мягко прижимай стопы в пол, чувствуя, как ноги становятся тяжелее. На выдохе расслабляй верхнюю часть тела (плечи, челюсть). Повтори 10 циклов дыхания. Ничего не менять, просто быть."
    ],
    'любовь':[
        "💕 **«Пульс в ладонях»**\n\nВстань лицом к стене на расстоянии вытянутой руки. Положи ладони на стену. Медленно, с нажимом, «отталкивай» стену, но не руками, а всем телом — словно пытаешься приблизиться к ней грудью. Делай это 1–2 минуты, сохраняя мягкий взгляд и улыбку. Это упражнение на принятие опоры и тепло контакта.",
        "💞 **«Качели с партнером (или с собой)»**\n\nЕсли есть партнер: встаньте спиной к спине, сцепитесь руками в локтях. Медленно приседайте и вставайте, чувствуя надежность друг друга.Если один: сядь на пол, обними колени. Медленно покачивайся из стороны в сторону, напевая тихую мелодию или просто дыша с закрытыми глазами. Любовь начинается с принятия своего тела.",
        "💗 **«Передача тепла»**\n\nПотри ладони друг о друга до сильного тепла. Положи горячие ладони на грудь (в центр), на живот, на лицо. Задерживайся в каждой точке на 20–30 секунд. Мысленно говори каждой части тела: «Я здесь, я с тобой». Простое, но мощное упражнение на саморегуляцию."
    ],
    'удивление': [
        "😲 **«Взрывные хлопки»**\n\nВстань, ноги на ширине плеч. На счет «раз-два-три» медленно приседай в глубокий присед. На счет «ЧЕТЫРЕ!» — резко выпрыгни вверх, широко раскинув руки и ноги в стороны, открыв рот и широко раскрыв глаза, как будто ты увидел нечто невероятное. 10 повторений.",
        "🤯 **«Смена ракурсов»**\n\nКаждые 10 секунд резко меняй положение тела: был стоя — сел на корточки, был на корточках — лег на спину, лежал — встал в мостик (или наклон). С каждым новым положением издавай звук удивления: «О!», «Вау!», «Ах!». 1 минута. Тренирует нейропластичность и легкое отношение к переменам.",
        "✨ **«Смотрю по сторонам»**\n\nСядь на стул. Очень быстро и резко поворачивай голову и корпус влево, фиксируя взгляд на какой-то точке (как будто там что-то интересное), затем так же резко — вправо. Поворачивайся всем корпусом, будто ты ищешь источник звука. 1 минута быстрых поворотов с широко открытыми глазами."
    ],
    'усталость': [
        "💧 **«Стряхивание»**\n\nВстань. Начни трясти кистями рук, потом локтями, потом всем телом, как будто ты выходишь из воды и стряхиваешь капли. Можно добавить звук «Ш-ш-ш» на выдохе. 2 минуты легкой тряски выводят молочную кислоту и снимают остаточное напряжение.",
        "🛌 **«Вис на невидимой ветке»**\n\nПодойди к дверному косяку или устойчивой опоре. Повисни на руках, расслабив нижнюю часть тела. Ноги чуть согнуты, спина расслаблена. Просто виси 30–60 секунд, позволяя позвоночнику вытянуться. Если опоры нет — наклонись вперед, положи руки на стол и повисни корпусом, расслабив шею.",
        "😴 **«Сонное дыхание с наклоном»**\n\nСядь на пол на колени (или на стул). Медленно наклонись вперед, положи лоб на пол (или на сложенные руки на столе). Ягодицы остаются на пятках (если сидишь на коленях). Дыши животом 2–3 минуты. Поза полного отдыха, которая позволяет телу «выключить» режим бодрствования без сна."
    ]

}

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="📝 Анализ настроения")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📔 Дневник")],
        [KeyboardButton(text="📈 График"), KeyboardButton(text="🧘 Упражнения")],
        [KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_emotion_inline_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🧘 Хочу упражнение", callback_data="exercise")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(text="💾 Сохранить в дневник", callback_data="save")],
        [InlineKeyboardButton(text="🎬 Фильм под настроение", callback_data="movie")],
        [InlineKeyboardButton(text="🎵 Искать через @fmusbot", url="https://t.me/fmusbot")],
        [InlineKeyboardButton(text="😺 Ещё котика", callback_data="more_cat")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ========== ФУНКЦИИ УДАЛЕНИЯ ==========
async def delete_previous_bot_message(user_id: int, chat_id: int):
    if user_id in user_last_bot_message:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=user_last_bot_message[user_id])
        except:
            pass
        del user_last_bot_message[user_id]

async def delete_user_message(message: Message):
    try:
        await message.delete()
    except:
        pass

# ========== КОМАНДА /START ==========
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    
    add_user(user_id, username, first_name, last_name)
    
    welcome_text = (
        f"🌟 **Привет, {first_name}!** 🌟\n\n"
        "Я твой личный помощник для работы с эмоциями.\n"
        "Просто напиши, что ты чувствуешь — "
        "я проанализирую и пришлю котика под настроение! 😺\n\n"
        "👇 **Выбери действие в меню снизу:**"
    )
    
    sent_message = await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    user_last_bot_message[user_id] = sent_message.message_id

# ========== ОБРАБОТКА КНОПОК МЕНЮ ==========
async def handle_menu_command(message: Message, response_text: str):
    user_id = message.from_user.id
    await delete_previous_bot_message(user_id, message.chat.id)
    await delete_user_message(message)
    sent_message = await message.answer(response_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    user_last_bot_message[user_id] = sent_message.message_id

@dp.message(F.text == "📝 Анализ настроения")
async def analyze_menu(message: Message):
    await handle_menu_command(message, "📝 **Режим анализа настроения**\n\nНапиши мне, что ты сейчас чувствуешь!")

@dp.message(F.text == "📊 Статистика")
async def stats_menu(message: Message):
    user_id = message.from_user.id
    stats, total = get_emotion_stats(user_id)
    if not stats:
        text = "📊 У тебя пока нет статистики."
    else:
        text = "📊 **Твоя статистика:**\n\n"
        for emotion, count in stats:
            percent = (count / total) * 100
            emoji = emotion.split()[0] if ' ' in emotion else '📝'
            text += f"{emoji} {count} раз ({percent:.1f}%)\n"
        text += f"\nВсего сообщений: {total}"
    await handle_menu_command(message, text)

@dp.message(F.text == "📔 Дневник")
async def diary_menu(message: Message):
    user_id = message.from_user.id
    entries = get_diary_entries(user_id, 10)
    if not entries:
        text = "📔 **Дневник пуст**"
    else:
        text = "📔 **Твой дневник:**\n\n"
        for emotion, msg, date in entries:
            date_str = date[:16] if date else "неизвестно"
            text += f"• {date_str} — {emotion}\n"
    await handle_menu_command(message, text)

@dp.message(F.text == "📈 График")
async def graph_menu(message: Message):
    user_id = message.from_user.id
    await delete_previous_bot_message(user_id, message.chat.id)
    await delete_user_message(message)
    await cmd_graph(message, from_menu=True)

@dp.message(F.text == "🧘 Упражнения")
async def exercises_menu(message: Message):
    await handle_menu_command(message, "🧘 **Упражнения для релаксации**\n\nПосле анализа появится кнопка «Хочу упражнение».")

@dp.message(F.text == "❓ Помощь")
async def help_menu(message: Message):
    help_text = (
        "🤖 **Помощь по командам:**\n\n"
        "/start — Начать работу\n"
        "/help — Показать это сообщение\n"
        "/graph — Показать график настроения\n\n"
        "📝 **Как пользоваться:**\n"
        "Напиши, что чувствуешь — я покажу котика и подберу фильм под настроение!\n\n"
        "🔄 **После анализа появятся кнопки:**\n"
        "• 🧘 Хочу упражнение\n"
        "• 🎬 Фильм под настроение\n"
        "• 📊 Моя статистика\n"
        "• 💾 Сохранить в дневник\n"
        "• 🎵 Искать через @song\n"
        "• 😺 Ещё котика"
    )
    await handle_menu_command(message, help_text)

# ========== КОМАНДА /HELP ==========
@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🤖 **Помощь по командам:**\n\n"
        "/start — Начать работу\n"
        "/help — Показать это сообщение\n"
        "/graph — Показать график настроения\n\n"
        "📝 **Как пользоваться:**\n"
        "Напиши, что чувствуешь — я покажу котика и подберу фильм под настроение!\n\n"
        "🔄 **После анализа появятся кнопки:**\n"
        "• 🧘 Хочу упражнение\n"
        "• 🎬 Фильм под настроение\n"
        "• 📊 Моя статистика\n"
        "• 💾 Сохранить в дневник\n"
        "• 🎵 Искать через @song\n"
        "• 😺 Ещё котика"
    )
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# ========== КОМАНДА /GRAPH ==========
@dp.message(Command("graph"))
async def cmd_graph(message: Message, from_menu: bool = False):
    user_id = message.from_user.id
    emotions_data = get_week_emotions(user_id)
    
    if len(emotions_data) < 3:
        await message.answer("📊 Для графика нужно хотя бы 3 сообщения за неделю.")
        return
    
    emotion_to_num = {
        '😠 Злость': 1, '😨 Страх': 2, '😢 Грусть': 3,
        '😐 Нейтрально': 4, '😊 Радость': 5, '😲 Удивление': 6, '😴 Усталость': 7, '❤️ Любовь': 8
    }
    
    dates = []
    values = []
    for emotion, date_str in emotions_data:
        try:
            if not date_str:
                continue
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            dates.append(date)
            val = 4
            for key, num in emotion_to_num.items():
                if key in emotion:
                    val = num
                    break
            values.append(val)
        except:
            continue
    
    if len(dates) < 2:
        await message.answer("📊 Недостаточно данных для графика.")
        return
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, 'b-o', linewidth=2, markersize=8)
    plt.fill_between(dates, values, alpha=0.3)
    plt.title('Твоё настроение за последние дни', fontsize=16, pad=20)
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Эмоции', fontsize=12)
    
    y_labels = ['😠 Злость', '😨 Страх', '😢 Грусть', '😐 Нейтрально', '😊 Радость', '😲 Удивление', '❤️ Любовь']
    plt.yticks(range(1, 8), y_labels)
    plt.ylim(0.5, 7.5)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    photo_file = BufferedInputFile(buf.getvalue(), filename="graph.png")
    plt.close()
    
    sent_message = await message.answer_photo(photo=photo_file, caption="📈 **Твой график настроения**", reply_markup=get_main_keyboard())
    if from_menu:
        user_last_bot_message[user_id] = sent_message.message_id

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text
    
    if text.startswith('/'):
        return
    
    menu_buttons = ["📝 Анализ настроения", "📊 Статистика", "📔 Дневник", "📈 График", "🧘 Упражнения", "❓ Помощь"]
    if text in menu_buttons:
        return
    
    if not text:
        return
    
    message_id = save_message(user_id, text)
    thinking_msg = await message.answer("🤔 Анализирую твоё настроение...")
    
    try:
        analysis = analyze_text(text)
        emotion_display = analysis['emotion']
        emotion_raw = analysis.get('emotion_raw', '')
        confidence = analysis['confidence']
        source = analysis.get('source', 'unknown')
        
        user_last_emotion[user_id] = emotion_raw
        user_last_emotion_display[user_id] = emotion_display
        update_message_emotion(message_id, emotion_display, confidence)
        
        cat_url = get_cat_url(emotion_raw)
        
        response = f"📊 **Анализ настроения:**\n"
        response += f"\nЭмоция: {emotion_display}\n"
        response += f"Уверенность: {confidence}%\n"
        
        if 'грусть' in emotion_raw or '😢' in emotion_display:
            response += "\n▫ **Интересный факт: Во время грусти мы инстинктивно замедляем дыхание и наклоняем голову вниз. Это древний механизм, связанный с работой слезных желез. Слезы, вызванные грустью, содержат гормоны стресса (пролактин, адренокортикотропный гормон), которых нет в слезах от лука или соринки. Организм буквально выводит стресс через жидкость.\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "😣 Сядь в наклон, опусти плечи и обними себя. Позволить телу принять позу грусти — значит разрешить эмоции завершиться естественно.\n"
            response += "⏰ Скажи «я побуду в этом 10 минут» и поставь таймер. Разрешение на эмоцию без чувства вины снижает внутреннее сопротивление.\n"
            response += "📝 Напиши на бумаге всё, что чувствуешь, но не отправляй. Грусть часто связана с недосказанностью, вывод в текст освобождает."
        elif 'злость' in emotion_raw or '😠' in emotion_display:
            response += "\n▫ **Интересный факт: Злость — единственная эмоция, которая буквально нагревает тело. Во время приступа гнева температура кистей рук может повышаться на 2–3 градуса (это зафиксировано в экспериментах). Биологический смысл: тело готовит руки к «действию» (удару, защите). Если злость подавляется, кровь остается в руках, но импульс не реализуется, что приводит к хроническому ощущению «ватных» или наоборот «сжатых» кистей, а также к проблемам с давлением.\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "😡 Потопай ногами или покричи в подушку. Физический выход энергии позволяет злости не застревать в теле.\n"
            response += "😤 Скажи, какая твоя ценность нарушена. Это переводит фокус с обвинения на понимание себя.\n"
            response += "⏸️ Отойди на 10 минут. В состоянии гнева рациональное мышление отключается, пауза позволяет мозгу вернуться к адекватной оценке."
        elif 'страх' in emotion_raw or '😨' in emotion_display:
            response += "\n▫ **Интересный факт: Когда мы испытываем страх, мышцы задней поверхности тела (спина, задняя часть шеи, ягодицы) напрягаются первыми. Это эволюционный механизм «приготовления к бегству». Если страх не переходит в действие, эти мышцы остаются в хроническом напряжении, формируя «панцирь страха». Именно поэтому при затяжном стрессе болит поясница и немеет затылок — тело продолжает готовиться к опасности, которой уже нет.\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "🌬️ Сделай глубокий выдох длиннее вдоха. Это переключает нервную систему из режима тревоги в режим покоя.\n"
            response += "👂 Назови страх вслух. Когда страх получает имя, мозг перестает воспринимать его как неопределенную угрозу.\n"
            response += "🪑 Коснись трех предметов вокруг. Возвращение в физическое пространство прерывает панический цикл и возвращает чувство опоры."
        elif 'радость' in emotion_raw or '😊' in emotion_display:
            response += "\n▫ **Интересный факт: В состоянии искренней радости наши мимические мышцы работают в унисон с внутренними органами. Когда мы улыбаемся не «вежливо», а по-настоящему (задействуя не только рот, но и мышцы вокруг глаз — «улыбка Дюшенна»), мозг посылает сигнал блуждающему нерву, который замедляет сердцебиение и снижает уровень кортизола быстрее, чем любой релаксационный протокол. Радость — это самый быстрый способ переключить нервную систему из «стресса» в «восстановление».\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "😁 Замри и скажи про себя «я радуюсь». Осознанное закрепление момента продлевает положительный эффект.\n"
            response += "📱 Напиши кому-то «мне сейчас хорошо». Разделенная радость усиливается через зеркальные нейроны.\n"
            response += "👏 Сделай спонтанное движение — прыжок или хлопок. Радость — это избыток энергии, и ей нужен простой выход."
        elif 'удивление' in emotion_raw or '😲' in emotion_display:
            response += "\n▫ **Интересный факт: Интересный факт: При удивлении брови поднимаются, увеличивая поле зрения на 15–20%. Это эволюционный механизм: чем шире глаза, тем больше информации попадает в мозг за долю секунды. Параллельно блокируется работа вкусовых рецепторов — пока длится удивление, человек физически не может почувствовать вкус пищи. Организм переключает все ресурсы на анализ нового.\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "☑️ Сделай что-то по-новому — поменяй маршрут или порядок действий. Удивление — реакция на новизну, и небольшое изменение рутины включает внимание.\n"
            response += "❔  Спроси себя «а что, если?». Один открытый вопрос запускает исследовательский режим мозга.\n"
            response += "👀 Задержи взгляд на том, что удивило, на 10 секунд. Удивление длится всего 1–2 секунды, но его можно продлить через осознанное внимание."
        elif 'усталость' in emotion_raw or '🥱' in emotion_display:
            response += "\n▫ **Интересный факт: При сильной усталости мозг принудительно «отключает» мышцы век, вызывая микросон — непроизвольные засыпания на 1–3 секунды. Это защитный механизм: нейроны таламуса входят в режим торможения, чтобы предотвратить истощение коры головного мозга. Организм жертвует вниманием, чтобы сохранить базовые функции жизнеобеспечения.\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "😴 Ляг на пол на 5 минут. Пол — самая стабильная опора, это снимает напряжение с позвоночника быстрее, чем кресло.\n"
            response += "📋 Отмени или перенеси одну задачу. Усталость часто возникает от перегрузки обязательствами, а контроль над нагрузкой восстанавливает энергию.\n"
            response += "👤 Спроси себя: тело устало или мозгу нужно переключиться? Иногда смена активности отменяет усталость за минуты — значит, она была не физической, а ментальной."
        elif 'любовь' in emotion_raw or '❤️' in emotion_display:
            response += "\n▫ **Интересный факт: Интересный факт: Во время влюбленности миндалевидное тело (центр страха) временно подавляется, а зрительные зоны, напротив, гиперчувствительны. Именно поэтому влюбленные не замечают недостатков партнера, но при этом способны найти его лицо в толпе за доли секунды. Организм буквально «выключает» критику ради размножения.\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "❤️ Сделай одно доброе дело для своего тела. Любовь начинается с контакта с собой — выпей воды, погладь себя по руке.\n"
            response += "🙏 Скажи кому-то спасибо за что-то конкретное. Благодарность — форма любви, которая не требует взаимности.\n"
            response += "🫶 Убери одну вещь на место. Любовь — это внимание, и простое действие по уходу за пространством возвращает ощущение заботы."
        else:
            response += "\n▫ **Интересный факт: Состояние полной нейтральности сопровождается микродвижениями — микровибрациями мышц частотой 8–12 Гц. Это физиологический маркер готовности: тело не отдыхает, а «сканирует» пространство в ожидании любого сигнала. Когда нет ни радости, ни печали, организм тратит энергию на поддержание этой скрытой боеготовности.\n**"
            response += "\n▫ Рекомендую тебе\n\n"
            response += "😋 Сделай одно простое движение. Нейтральность часто замораживает тело — потянись, сожми и разожми ладони, это вернет сигнал «я жив» в мозг.\n"
            response += "🫂 Заметь что-то одно вокруг. Не оценивая, не «нравится/не нравится» — просто назови про себя цвет, звук, форму. Это выводит мозг из режима «холостого хода».\n"
            response += "😌 Сделай паузу между мыслью и следующим действием. Нейтральность — не пустота, а чистая доска. Остановись на 5 секунд и позволь следующему шагу быть осознанным, а не автоматическим.\n\n"
        
        response += f"❓ Нажми кнопку ниже — получу упражнение или фильм!"
        
        # Проверяем длину
        if len(response) > 1024:
            logging.warning(f"Подпись: {len(response)} символов")
            response = response[:1000] + "...\n\n❓ Нажми кнопку ниже!"
        
        try:
            await thinking_msg.delete()
        except:
            pass
        
        try:
            sent_message = await message.answer_photo(
                photo=cat_url,
                caption=response,
                parse_mode="Markdown",
                reply_markup=get_emotion_inline_keyboard()
            )
        except Exception as e:
            logging.error(f"Ошибка отправки котика: {e}")
            sent_message = await message.answer(
                response,
                parse_mode="Markdown",
                reply_markup=get_emotion_inline_keyboard()
            )
        
        user_last_bot_message[user_id] = sent_message.message_id

    except Exception as e:
        logging.error(f"Ошибка анализа: {e}")
        try:
            await thinking_msg.delete()
        except:
            pass
        error_msg = await message.answer("📝 Произошла ошибка. Попробуй ещё раз!", reply_markup=get_main_keyboard())
        user_last_bot_message[user_id] = error_msg.message_id

# ========== ОБРАБОТКА ИНЛАЙН-КНОПОК ==========
@dp.callback_query(F.data == "exercise")
async def send_exercise(callback: CallbackQuery):
    user_id = callback.from_user.id
    emotion_raw = user_last_emotion.get(user_id, 'нейтрально')
    exercises = EXERCISES.get(emotion_raw, EXERCISES['нейтрально'])
    exercise = random.choice(exercises)
    sent_message = await callback.message.answer(exercise, parse_mode="Markdown", reply_markup=get_main_keyboard())
    user_last_bot_message[user_id] = sent_message.message_id
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def send_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    stats, total = get_emotion_stats(user_id)
    if not stats:
        text = "📊 У тебя пока нет статистики."
    else:
        text = "📊 **Твоя статистика:**\n\n"
        for emotion, count in stats:
            percent = (count / total) * 100
            emoji = emotion.split()[0] if ' ' in emotion else '📝'
            text += f"{emoji} {count} раз ({percent:.1f}%)\n"
        text += f"\nВсего сообщений: {total}"
    sent_message = await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    user_last_bot_message[user_id] = sent_message.message_id
    await callback.answer()

@dp.callback_query(F.data == "save")
async def save_to_diary(callback: CallbackQuery):
    user_id = callback.from_user.id
    emotion_display = user_last_emotion_display.get(user_id, '😐 Нейтрально')
    save_diary_entry(user_id, emotion_display, "")
    response = f"💾 **Сохранено в дневник!**\n\nЗапись: {emotion_display}"
    sent_message = await callback.message.answer(response, parse_mode="Markdown", reply_markup=get_main_keyboard())
    user_last_bot_message[user_id] = sent_message.message_id
    await callback.answer()

@dp.callback_query(F.data == "movie")
async def send_movie(callback: CallbackQuery):
    user_id = callback.from_user.id
    emotion_raw = user_last_emotion.get(user_id, 'нейтрально')
    movies = MOVIES.get(emotion_raw, MOVIES['нейтрально'])
    movie = random.choice(movies)
    response = f"🎬 **Фильм под настроение:**\n\n{movie}"
    sent_message = await callback.message.answer(response, parse_mode="Markdown", reply_markup=get_main_keyboard())
    user_last_bot_message[user_id] = sent_message.message_id
    await callback.answer()

@dp.callback_query(F.data == "more_cat")
async def send_more_cat(callback: CallbackQuery):
    user_id = callback.from_user.id
    cat_url = get_random_cat()
    try:
        sent_message = await callback.message.answer_photo(
            photo=cat_url,
            caption="😻 **Лови ещё котика!**",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logging.error(f"Ошибка отправки котика: {e}")
        sent_message = await callback.message.answer("😻 Котик временно недоступен.", reply_markup=get_main_keyboard())
    user_last_bot_message[user_id] = sent_message.message_id
    await callback.answer()

# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
async def main():
    print("🚀 Запускаем бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Бот запущен и готов к работе!")
    
    try:
        await dp.start_polling(bot)
    finally:
        print("🛑 Бот остановлен")
        await bot.session.close()

# ... (весь остальной код твоего бота)

# --- Добавь этот код ниже ---
from flask import Flask
from threading import Thread
import os

# Создаем простое веб-приложение для проверки здоровья
health_app = Flask(__name__)

@health_app.route('/health')
def health_check():
    # Просто возвращаем "OK", чтобы сообщить Render и UptimeRobot, что все хорошо
    return "OK", 200

def run_health_server():
    # Запускаем веб-сервер на порту, который назначит Render
    port = int(os.environ.get("PORT", 10000))
    health_app.run(host='0.0.0.0', port=port)

# Запускаем сервер для проверки здоровья в отдельном потоке,
# чтобы он не мешал работе основного бота
Thread(target=run_health_server, daemon=True).start()
# --- Код для проверки здоровья закончился ---

# ... (дальше идет твой код для запуска бота, например, bot.polling())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен пользователем")
