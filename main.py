import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from datetime import datetime

# Конфигурация
TOKEN = "7923244791:AAG2l0BcB4FCYBqGfKgQc30zIWe8ZrSBcOY"
MAIN_ADMIN = "630043071"  # ID администратора

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище сообщений
messages = {}

# Сохранение сообщений в JSON
def save_message(chat_id, sender, text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if chat_id not in messages:
        messages[chat_id] = []
    messages[chat_id].append({"name": sender, "date": now, "text": text})
    with open("messages.json", "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)

# Обработчики команд
@dp.message(Command("start"))
async def start_command(message: types.Message):
    save_message(message.chat.id, message.from_user.username, message.text)
    save_message(message.chat.id, "BOT", "Привет! Я бот с простыми функциями. Напиши /help для списка команд.")
    await message.answer("Привет! Я бот с простыми функциями. Напиши /help для списка команд.")

@dp.message(Command("help"))
async def help_command(message: types.Message):
    save_message(message.chat.id, message.from_user.username, message.text)
    commands = (
        "/time - Текущее время\n"
        "/date - Сегодняшняя дата\n"
        "/weekday - День недели\n"
        "/echo <текст> - Повторяет текст\n"
        "/messages - История сообщений (только для администратора)"
    )
    save_message(message.chat.id, "BOT", f"Список доступных команд:\n{commands}")
    await message.answer(f"Список доступных команд:\n{commands}")

@dp.message(Command("time"))
async def time_command(message: types.Message):
    save_message(message.chat.id, message.from_user.username, message.text)
    now = datetime.now().strftime("%H:%M:%S")
    save_message(message.chat.id, "BOT", f"Текущее время: {now}")
    await message.answer(f"Текущее время: {now}")

@dp.message(Command("date"))
async def date_command(message: types.Message):
    save_message(message.chat.id, message.from_user.username, message.text)
    today = datetime.now().strftime("%Y-%m-%d")
    save_message(message.chat.id, "BOT", f"Сегодняшняя дата: {today}")
    await message.answer(f"Сегодняшняя дата: {today}")

@dp.message(Command("weekday"))
async def weekday_command(message: types.Message):
    save_message(message.chat.id, message.from_user.username, message.text)
    weekday = datetime.now().strftime("%A")
    save_message(message.chat.id, "BOT", f"Сегодня день недели: {weekday}")
    await message.answer(f"Сегодня день недели: {weekday}")

@dp.message(Command("echo"))
async def echo_command(message: types.Message):
    text = message.text[len("/echo "):].strip()
    save_message(message.chat.id, message.from_user.username, message.text)
    if text:
        await message.answer(text)
    else:
        await message.answer("Введите текст после команды /echo.")


@dp.message(Command("messages"))
async def messages_command(message: types.Message):
    if str(message.from_user.id) == MAIN_ADMIN:
        save_message(message.chat.id, message.from_user.username, message.text)

        # Читаем сообщения из файла
        try:
            with open("messages.json", "r", encoding="utf-8") as file:
                all_messages = json.load(file)
        except FileNotFoundError:
            all_messages = {}

        # Проверяем, есть ли сохраненные сообщения
        if not all_messages:
            await message.answer("Нет сохраненных сообщений.")
            return

        # Создаем кнопки для выбора пользователя
        keyboard_buttons = []
        for user_id, user_messages in all_messages.items():
            if user_messages:  # Проверяем, есть ли сообщения от пользователя
                username = user_messages[0]["name"] or 'none'
                keyboard_buttons.append(
                    [InlineKeyboardButton(text=username, callback_data=f"view_{user_id}")]
                )

        # Добавляем кнопку для удаления всех сообщений
        keyboard_buttons.append(
            [InlineKeyboardButton(text="Удалить все сообщения", callback_data="clear_messages")]
        )

        # Создаем клавиатуру с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await message.answer("Выберите пользователя для просмотра сообщений:", reply_markup=keyboard)
    else:
        await message.answer("У вас нет доступа к этой команде.")


@dp.callback_query(lambda call: call.data.startswith("view_"))
async def view_messages_callback(call: types.CallbackQuery):
    user_id = call.data.split("_")[1]  # Извлекаем ID пользователя из callback_data

    # Читаем сообщения из файла
    try:
        with open("messages.json", "r", encoding="utf-8") as file:
            all_messages = json.load(file)
    except FileNotFoundError:
        await call.message.answer("Сообщений не найдено.")
        return

    # Проверяем, есть ли сообщения от выбранного пользователя
    user_messages = all_messages.get(user_id, [])
    if not user_messages:
        await call.message.answer("Сообщений от данного пользователя не найдено.")
        return

    # Форматируем сообщения
    formatted_messages = "\n".join(
        f"{msg['name']} - {msg['date']}:\n'{msg['text']}'\n-----\n"
        for msg in user_messages
    )

    await call.message.answer(f"Сообщения от пользователя {user_messages[0]['name']}:\n\n{formatted_messages}")

@dp.callback_query(lambda call: call.data == "clear_messages")
async def clear_messages_callback(call: types.CallbackQuery):
    if str(call.from_user.id) == MAIN_ADMIN:
        global messages
        messages = {}
        with open("messages.json", "w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
        await call.message.answer("Все сообщения удалены.")
    else:
        await call.answer("У вас нет доступа.", show_alert=True)



# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
