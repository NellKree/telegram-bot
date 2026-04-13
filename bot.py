import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties

from drive_downloader import download_google_drive_file
from transcriber import transcribe_file
from gemini import generate_summary

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_FILE_SIZE_GB = float(os.getenv("MAX_FILE_SIZE_GB", 20))

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

SUPPORTED_FORMATS = {".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".mov", ".avi", ".mkv"}

# временное хранилище (MVP)
user_transcripts = {}


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Отправь ссылку Google Drive на аудио/видео.\n"
        "Я сделаю транскрипт и дам summary."
    )


@dp.message(F.text)
async def handle_link(message: Message):
    url = message.text.strip()

    if "drive.google.com" not in url:
        await message.answer("Это не ссылка Google Drive.")
        return

    status = await message.answer("Загрузка файла...")

    try:
        file_path, file_size_gb = await asyncio.to_thread(download_google_drive_file, url)

        if file_size_gb > MAX_FILE_SIZE_GB:
            os.remove(file_path)
            await status.edit_text("Файл слишком большой.")
            return

        ext = os.path.splitext(file_path)[1].lower()

        if ext not in SUPPORTED_FORMATS:
            os.remove(file_path)
            await status.edit_text("Неподдерживаемый формат.")
            return

        await status.edit_text("Транскрибация...")

        transcript = await asyncio.to_thread(transcribe_file, file_path)

        user_transcripts[message.from_user.id] = transcript

        # сохраняем файл
        output_file = "transcript.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)

        file_to_send = FSInputFile(output_file)

        await message.answer_document(
            document=file_to_send,
            caption="Транскрипция готова"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📄 Сделать summary", callback_data="summary")]
        ])

        await message.answer("Что дальше?", reply_markup=keyboard)

        os.remove(output_file)
        os.remove(file_path)

    except Exception as e:
        await status.edit_text(f"Ошибка: {e}")


@dp.callback_query(F.data == "summary")
async def summary_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    transcript = user_transcripts.get(user_id)

    if not transcript:
        await callback.message.answer("Транскрипт не найден. Загрузите файл заново.")
        return

    await callback.message.edit_text("Генерирую summary...")

    summary = await asyncio.to_thread(generate_summary, transcript)

    await callback.message.answer(summary)


async def main():
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())