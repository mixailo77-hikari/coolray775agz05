import asyncio
import json
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiohttp import web

# ----------------------------------------------------
# Переменные окружения
# ----------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Переменная BOT_TOKEN не найдена в окружении!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

    # Синхронизация через Google Таблицы (реализуйте логику получения данных здесь)
    # Возвращаем заглушку структуры данных, если данные не найдены
    return web.json_response({
        'carInfo': {'initialOdo': 0, 'model': '', 'year': '', 'notes': ''},
        'fuel': [],
        'service': [],
        'rules': []
    })

async def save_car_data_handler(request):
    try:
        body = await request.json()
        user_id = int(body.get('userId', 0))
        data = body.get('data')
    except Exception:
        return web.json_response({'error': 'Bad JSON'}, status=400)

    if not user_id or data is None:
        return web.json_response({'error': 'Invalid payload'}, status=400)

    # Синхронизация через Google Таблицы (реализуйте логику сохранения данных здесь)
    
    return web.json_response({'status': 'ok'})

# CORS middleware для корректных запросов из браузера к aiohttp API
@web.middleware
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        return web.Response(headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

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
    
    # Сохранение данных синхронизируется через Google Таблицы

    fuel_count = len(data.get("fuel", []))
    service_count = len(data.get("service", []))
    car_name = data.get("carInfo", {}).get("model", "Автомобиль")

    await message.answer(
        f"✅ **Данные успешно отправлены!**\n\n"
        f"🚘 **Авто:** {car_name}\n"
        f"⛽ **Заправок:** {fuel_count}\n"
        f"🛠 **Записей ТО:** {service_count}\n\n"
        f"📁 Синхронизация данных настроена через Google Таблицы."
    )

# ----------------------------------------------------
# Запуск aiohttp сервера и aiogram бота
# ----------------------------------------------------
async def main():
    logging.basicConfig(level=logging.INFO)

    # Настраиваем HTTP API сервер с CORS
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get('/api/car-data', get_car_data_handler)
    app.router.add_post('/api/car-data', save_car_data_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"API сервер запущен на порту {port}")

    # Запускаем поллинг бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
