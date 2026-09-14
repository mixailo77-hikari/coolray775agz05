import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.filters import Command
from typing import Callable, Dict, Any, Awaitable

# ----------------------------------------------------
# Настройки
# ----------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USERS = [1081280942, 1055161917]

if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Переменная BOT_TOKEN не найдена в окружении!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------------------------------------------
# Защита по Telegram ID (Middleware)
# ----------------------------------------------------
class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Message | types.CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: types.Message | types.CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        
        if not user or user.id not in ALLOWED_USERS:
            if isinstance(event, types.Message):
                await event.answer("⛔ Доступ запрещен. У вас нет прав для работы с этим ботом.")
            elif isinstance(event, types.CallbackQuery):
                await event.answer("⛔ Доступ запрещен.", show_alert=True)
            return  # Блокируем посторонних пользователей

        return await handler(event, data)

# Регистрируем защиту для сообщений и колбэков
dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())

# ----------------------------------------------------
# Хэндлеры бота
# ----------------------------------------------------
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    kb = [
        [types.KeyboardButton(
            text="🚗 Учёт авто", 
            web_app=types.WebAppInfo(url="https://coolray775agz05.netlify.app/")
        )],
        [types.KeyboardButton(
            text="💰 Семейный бюджет", 
            web_app=types.WebAppInfo(url="https://family-budget-7794.netlify.app/")
        )]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите приложение для запуска:", reply_markup=keyboard)

# ----------------------------------------------------
# Запуск бота
# ----------------------------------------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Бот запущен и ожидает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
