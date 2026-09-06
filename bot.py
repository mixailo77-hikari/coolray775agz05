import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command

# Замените на ваш токен от BotFather
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Команда /start отправляет кнопку для открытия Mini App
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

# Прием данных из Mini App (когда пользователь нажимает "📤 В бот")
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    # Распаковываем JSON от веб-страницы
    raw_json = message.web_app_data.data
    data = json.loads(raw_json)
    
    # Сохраняем данные в файл с привязкой к ID пользователя
    user_id = message.from_user.id
    filename = f"user_{user_id}_data.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Формируем сводку для ответа
    fuel_count = len(data.get("fuel", []))
    service_count = len(data.get("service", []))
    car_name = data.get("carInfo", {}).get("model", "Автомобиль")

    await message.answer(
        f"✅ **Данные успешно синхронизированы!**\n\n"
        f"🚘 **Авто:** {car_name}\n"
        f"⛽ **Заправок в базе:** {fuel_count}\n"
        f"🛠 **Записей ТО:** {service_count}\n\n"
        f"📁 Файл с бекапом сохранен на сервере."
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())