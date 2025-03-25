import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from arbitrage import ArbitrageScanner

API_TOKEN = "7726968232:AAHL0sl84733e69DXld2E0bWTyOvsf8ReaE"
CHAT_ID = "7726968232"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scanner = ArbitrageScanner()

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("🔍 СКАН"), KeyboardButton("📡 Мониторинг"))

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("🚀 Добро пожаловать в арбитражный сканер!", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "🔍 СКАН")
async def manual_scan(message: types.Message):
    await message.answer("🔍 Запускаю сканирование...")
    results = await scanner.scan()
    if results:
        for res in results:
            await message.answer(res, parse_mode="HTML")
    else:
        await message.answer("❌ Подходящих связок не найдено.")

@dp.message_handler(lambda message: message.text == "📡 Мониторинг")
async def toggle_monitoring(message: types.Message):
    if not scanner.monitoring:
        await message.answer("📡 Мониторинг запущен.")
        await scanner.start_monitoring(bot, CHAT_ID)
    else:
        scanner.stop_monitoring()
        await message.answer("🛑 Мониторинг остановлен.")

if __name__ == "__main__":
    executor.start_polling(dp)