from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import load_data_tasks, select_data_for_tasks

router = Router()


@router.message(Command(commands=['load_tasks_from_googlesheets']))
async def load_tasks_from_google_sheets(message: Message, database, google_sheet_key, path_images):
    response = await load_data_tasks(database, google_sheet_key, path_images)
    await message.answer(response)

@router.message(Command(commands=['generation_image_tasks']))
async def generate_tasks_images(message: Message, database, path_images, template_json_path):
    await select_data_for_tasks(database, path_images, template_json_path)
    await message.answer("Генерация изображений завершена.")

@router.message()
async def echo(message: Message):
    await message.answer(text='Привет')