from aiogram import F, Router
from filters import *
import asyncio
from pagination import pagin_dict
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
from inline_keyboard import create_pagination_keyboard
from bookmark_kb import create_edit_keyboard
from external_functions import (page_listai,
                                return_current_page_index,
                                add_new_bookmarks,
                                set_new_page,
                                return_last_nod_from_modified_pagina,
                                insert_new_page_in_modified_pagina,
                                return_bookmark_list,
                                remove_bookmark)
from lexicon import LEXICON
from bot_instance import bot
import json
from aiogram.exceptions import TelegramBadRequest
lese_router = Router()

# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед-назад"
# во время взаимодействия пользователя с сообщением-книгой
@lese_router.callback_query(MOVE_PAGE())
async def page_moving(callback: CallbackQuery):
    print(f'{callback.data = }')
    shift = -1 if callback.data == 'backward' else 1
    user_id = callback.from_user.id
    await page_listai(user_id, shift)
    pagin_index = await return_current_page_index(user_id)
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=pagin_dict[pagin_index][0], caption=pagin_dict[pagin_index][1]),
            reply_markup=create_pagination_keyboard(pagin_index)
        )
    except TelegramBadRequest:
        print('Into Exeption')
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с номером текущей страницы и добавлять текущую страницу в закладки
@lese_router.callback_query(lambda x: '/' in x.data and x.data.replace(' / ', '').isdigit())
async def process_page_press(callback: CallbackQuery):
    await add_new_bookmarks(callback.from_user.id)
    await callback.answer('Страница добавлена в закладки!')


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок
@lese_router.callback_query(IS_DIGIT_CALLBACK_DATA())
async def process_bookmark_press(callback: CallbackQuery):
    # print("Process_bookmark_press works")
    user_id = callback.from_user.id
    go_to_page_on_bookmark = int(callback.data)
    try:
        await set_new_page(user_id, go_to_page_on_bookmark)
        current_index = go_to_page_on_bookmark
        last_message = await return_last_nod_from_modified_pagina(user_id) # возвращает строку

        return_to_message = Message(**json.loads(last_message))

        # print('type return_to_message = ', type(return_to_message), '\n\n', return_to_message)
        valid_with_bot_msg = Message.model_validate(return_to_message).as_(bot)

        modifying_msg = await valid_with_bot_msg.edit_media(
            media=InputMediaPhoto(
                media=pagin_dict[current_index][0], caption=pagin_dict[current_index][1]),
            reply_markup=create_pagination_keyboard(current_index))

        str_modifying_msg = modifying_msg.model_dump_json(exclude_none=True)
        # print('str_modifying_msg = ', str_modifying_msg,'\n type (str_modifying_msg)', type(str_modifying_msg))
        await insert_new_page_in_modified_pagina(user_id, str_modifying_msg)
    except TelegramBadRequest:
        await callback.answer()
    await callback.message.delete()

# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "редактировать" под списком закладок
@lese_router.callback_query(F.data == 'edit_bookmarks')
async def process_edit_press(callback: CallbackQuery):
    user_id = callback.from_user.id
    print('process_edit_press works')
    book_marks_list = await return_bookmark_list(user_id)
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *book_marks_list
        ))
    await callback.answer()
    # await callback.message.delete()

# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "отменить" во время работы со списком закладок (просмотр и редактирование)
@lese_router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.delete()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок к удалению
@lese_router.callback_query(IS_DEL_BUCKMARK())
async def process_del_bookmark_press(callback: CallbackQuery):
    user_id = callback.from_user.id
    I_want_to_del = int(callback.data[:-3])
    await remove_bookmark(user_id, I_want_to_del)
    my_bookmarks_list = await return_bookmark_list(user_id)
    print('my_bookmarks_list = ', my_bookmarks_list)
    if my_bookmarks_list:
        await (
                callback.message.edit_text(
                text=LEXICON['/bookmarks'],
                reply_markup=create_edit_keyboard(
                    *my_bookmarks_list)))
    else:
        no_marks_respond = await callback.message.edit_text(text=LEXICON['no_bookmarks'])
        await asyncio.sleep(2)
        await no_marks_respond.delete()
    await callback.answer()


@lese_router.message()
async def send_echo(message: Message):
    print("Works send_echo")
    if message.text.isdigit():
        antwort = await message.reply(f'В книге только  <b>{len(pagin_dict)}</b>  страниц')
        await asyncio.sleep(3)
        await message.delete()
        await antwort.delete()
    else:
        antwort = await message.reply(f'Давайте лучше продолжим чтение ?')
        await asyncio.sleep(3)
        await message.delete()
        await antwort.delete()
