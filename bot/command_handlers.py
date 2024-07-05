from aiogram import Router, F
import asyncio
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from external_functions import (edit_repeat_text_window, check_user_in_table,
                                insert_new_user_in_table,
                                insert_new_page_in_modified_pagina,
                                go_back_to_beginning,
                                set_new_page,
                                check_bookmarks,
                                edit_help_window,
                                continue_window)

from inline_keyboard import create_pagination_keyboard
from bookmark_kb import create_bookmarks_keyboard
from filters import CHECK_NUMBER, PRE_START
from pagination import pagin_dict
from bookmark_kb import pre_start_clava
from lexicon import LEXICON
from aiogram.exceptions import TelegramBadRequest

command_router = Router()


# @command_router.message()
# async  def return_id_foto(message:Message):
#     await message.answer(text='start')
#     print(message.photo[-1].file_id)

@command_router.message(~F.text)
async def delete_not_text_type_messages(message:Message):
    await message.delete()

@command_router.message(CommandStart())
async def process_start_command(message: Message):
    user_tg_id = message.from_user.id
    user_name = message.from_user.first_name
    if not await check_user_in_table(user_tg_id):
        await insert_new_user_in_table(user_tg_id, user_name)
        first_antwort = await message.answer(text=f'<b>{user_name}</b>, сейчас Вы узнаете много интересного !',
                             reply_markup=ReplyKeyboardRemove())
        start_page = await message.answer_photo(
            photo=pagin_dict[1][0],
            caption=pagin_dict[1][1],
            reply_markup=create_pagination_keyboard()
        )
        str_start_page = start_page.model_dump_json(
            exclude_none=True
        )
        await insert_new_page_in_modified_pagina(user_tg_id, str_start_page)
        await asyncio.sleep(4)
        await first_antwort.delete()
    await message.delete()


@command_router.message(PRE_START())
async def before_start(message:Message):
    prestart_ant = await message.answer(text='Нажми на кнопку <b>start</b> !',
                         reply_markup=pre_start_clava)
    await message.delete()
    await asyncio.sleep(4)
    await prestart_ant.delete()



@command_router.message(Command(commands='help'))
async def process_help_command(message: Message):
    print('help works')
    await edit_help_window(message)  # First usage
    await message.delete()


@command_router.message(Command(commands='beginning'))
async def process_beginning_command(message: Message):
    await go_back_to_beginning(message.from_user.id)
    await edit_repeat_text_window(message)
    await message.delete()

@command_router.message(Command(commands='continue'))
async def process_continue_command(message: Message):
    cont_ant = await message.answer("Продолжаем чтение")
    await message.delete()
    await asyncio.sleep(2)
    await cont_ant.delete()

@command_router.message(Command(commands='continue'))
async def process_continue_command(message: Message):
    user_id = message.from_user.id
    cont_ant = await message.answer("Продолжаем чтение")
    await continue_window(message, user_id)
    await message.delete()
    await asyncio.sleep(1)
    await cont_ant.delete()


@command_router.message(CHECK_NUMBER())
async def set_page_number(message:Message):
    print('set_number works\n message = ', message)
    if message.text.startswith('/'):
        new_page = int(message.text[1:])
    else:
        new_page = int(message.text)
    try:
        await set_new_page(message.from_user.id, new_page)
        await edit_repeat_text_window(message)
        await message.delete()
    except TelegramBadRequest:
        await message.delete()

# Этот хэндлер будет срабатывать на команду "/bookmarks"
# и отправлять пользователю список сохраненных закладок,
# если они есть или сообщение о том, что закладок нет
@command_router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message):
    user_id = message.from_user.id
    book_marks = await check_bookmarks(user_id)
    if book_marks:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *book_marks
            )
        )
    else:
        no_bookmark = await message.answer(text=LEXICON['no_bookmarks'])
        await asyncio.sleep(4)
        await no_bookmark.delete()
    await message.delete()