import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

# ----------------------------------------------------
# Переменные окружения и настройки
# ----------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USERS = [1081280942, 1055161917]

if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Переменная BOT_TOKEN не найдена в окружении!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------------------------------------------
# Middleware для защиты бота по ID
# ----------------------------------------------------
class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        
        if not user or user.id not in ALLOWED_USERS:
            if isinstance(event, Message):
                await event.answer("⛔ Доступ запрещен. У вас нет прав для работы с этим ботом.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Доступ запрещен.", show_alert=True)
            return  # Прерываем выполнение

        return await handler(event, data)

# Регистрируем middleware
dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())

# ----------------------------------------------------
# Хэндлеры Telegram Бота
# ----------------------------------------------------
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    kb = [
        [
            types.KeyboardButton(
                text="💰 Семейный бюджет", 
                web_app=types.WebAppInfo(url="https://family-budget-7794.netlify.app/")
            )
        ],
        [
            types.KeyboardButton(
                text="🚗 Учёт авто (Coolray)", 
                web_app=types.WebAppInfo(url="https://coolray775agz05.netlify.app/")
            )
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите нужное приложение для запуска:", reply_markup=keyboard)

# ----------------------------------------------------
# Запуск бота (без aiohttp и БД)
# ----------------------------------------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Запуск Telegram бота в режиме Polling...")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
