from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import load_data_tasks

router = Router()


@router.message(Command(commands=['load_tasks_from_googlesheets']))
async def send_echo(message: Message, database, google_sheet_key):
    await message.answer(load_data_tasks(database, google_sheet_key))