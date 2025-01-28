import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from keyboards.set_menu import set_main_menu
from handlers.admin_handlers import router
from database.database import db_start


async def main():
    config: Config = load_config()
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    await db_start(config.db.database)

    await set_main_menu(bot)

    dp.include_router(router)

    dp.workflow_data.update({'database': config.db.database, 'google_sheet_key': config.google_sheet.key})

    await dp.start_polling(bot)


asyncio.run(main())
