import asyncio
from aiogram import Dispatcher
from command_handlers import command_router
from lese_handlers import lese_router
from bot_base import init_models
from aiogram.enums import ParseMode
from config import settings
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from bot_instance import bot

# https://github.com/shichchirtch/Election_2020_KO.git


# Функция конфигурирования и запуска бота
async def main():
    await init_models()
    # Инициализируем бот и диспетчер
    # bot = Bot(token=settings.BOT_TOKEN,
    #           default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    async def set_main_menu(bot):
        # Создаем список с командами и их описанием для кнопки menu
        main_menu_commands = [
            BotCommand(command='/3',
                       description='Содержание'),
            BotCommand(command='/continue',
                       description='Продолжить чтение'),
            BotCommand(command='/bookmarks',
                       description='Мои закладки'),
            BotCommand(command='/help',
                       description='Справка по работе бота'),
            BotCommand(command='/beginning',
                       description='В начало книги')]
        await bot.set_my_commands(main_menu_commands)

    # Регистрируем асинхронную функцию в диспетчере,
    # которая будет выполняться на старте бота,
    dp.startup.register(set_main_menu)

    await set_main_menu(bot)
    dp = Dispatcher()
    dp.include_router(command_router)
    dp.include_router(lese_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
