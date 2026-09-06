import asyncio
import json
import logging
import os
import asyncpg
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiohttp import web

# ----------------------------------------------------
# Переменные окружения
# ----------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Переменная BOT_TOKEN не найдена в окружении!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------------------------------------------
# База данных PostgreSQL (Railway)
# ----------------------------------------------------
async def init_db():
    if not DATABASE_URL:
        logging.warning("DATABASE_URL не найден. Работа с PostgreSQL отключена.")
        return
    
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS user_car_data (
            user_id BIGINT PRIMARY KEY,
            data JSONB NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    await conn.close()
    logging.info("База данных PostgreSQL успешно инициализирована.")

async def save_user_data_db(user_id: int, data: dict):
    if not DATABASE_URL:
        return
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO user_car_data (user_id, data, updated_at)
        VALUES ($1, $2, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) 
        DO UPDATE SET data = $2, updated_at = CURRENT_TIMESTAMP;
    ''', user_id, json.dumps(data))
    await conn.close()

async def get_user_data_db(user_id: int):
    if not DATABASE_URL:
        return None
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow('SELECT data FROM user_car_data WHERE user_id = $1', user_id)
    await conn.close()
    if row:
        return json.loads(row['data'])
    return None

# ----------------------------------------------------
# HTTP API для Mini App (загрузка и сохранение)
# ----------------------------------------------------
async def get_car_data_handler(request):
    try:
        user_id = int(request.query.get('userId', 0))
    except ValueError:
        return web.json_response({'error': 'Invalid userId'}, status=400)

    if not user_id:
        return web.json_response({'error': 'No userId provided'}, status=400)

    data = await get_user_data_db(user_id)
    if data:
        return web.json_response(data)
    
    return web.json_response({
        'carInfo': {'initialOdo': 0, 'model': '', 'year': '', 'notes': ''},
        'fuel': [],
        'service': [],
        'rules': []
    })

async def save_car_data_handler(request):
    body = await request.json()
    user_id = int(body.get('userId', 0))
    data = body.get('data')

    if not user_id or data is None:
        return web.json_response({'error': 'Invalid payload'}, status=400)

    await save_user_data_db(user_id, data)
    return web.json_response({'status': 'ok'})

# ----------------------------------------------------
# Хэндлеры Telegram Бота
# ----------------------------------------------------
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    kb = [
        [types.KeyboardButton(
            text="🚗 Открыть учёт авто", 
            web_app=types.WebAppInfo(url="https://coolray775agz05.netlify.app/")
        )]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Нажмите кнопку ниже для управления учётом авто:", reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    raw_json = message.web_app_data.data
    data = json.loads(raw_json)
    user_id = message.from_user.id
    
    # Сохраняем данные в PostgreSQL
    await save_user_data_db(user_id, data)

    fuel_count = len(data.get("fuel", []))
    service_count = len(data.get("service", []))
    car_name = data.get("carInfo", {}).get("model", "Автомобиль")

    await message.answer(
        f"✅ **Данные успешно синхронизированы!**\n\n"
        f"🚘 **Авто:** {car_name}\n"
        f"⛽ **Заправок в базе:** {fuel_count}\n"
        f"🛠 **Записей ТО:** {service_count}\n\n"
        f"📁 Данные обновлены и сохранены в PostgreSQL."
    )

# ----------------------------------------------------
# Запуск aiohttp сервера и aiogram бота
# ----------------------------------------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Инициализируем таблицы в БД
    await init_db()

    # Настраиваем HTTP API сервер
    app = web.Application()
    app.router.add_get('/api/car-data', get_car_data_handler)
    app.router.add_post('/api/car-data', save_car_data_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    
    # Railway передает порт через переменную окружения PORT
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"API сервер запущен на порту {port}")

    # Запускаем поллинг бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
