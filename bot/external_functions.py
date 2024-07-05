from bot_base import session_marker, User
from sqlalchemy import select
from aiogram.types import Message, InputMediaPhoto
from inline_keyboard import create_pagination_keyboard
from pagination import pagin_dict, help_command
from bot_instance import bot
import json

async def edit_repeat_text_window(message:Message):
    """Эта асинхронная функция редактирует открытую прежде страницу, если юзер нажал
    на какую нибудь кнопку создающее новое окно, а не редактирующее старое с текстом"""
    print("edit FUNC WORKS")
    user_tg_id = message.from_user.id
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        current_index = needed_data.page
        list_modified_pagins = needed_data.modified_pagina
        needed_message = list_modified_pagins.pop()
        return_to_message = Message(**json.loads(needed_message))
        valid_with_bot_msg = Message.model_validate(return_to_message).as_(bot)
        modified_pag = await valid_with_bot_msg.edit_media(
            media=InputMediaPhoto(
                media=pagin_dict[current_index][0], caption=pagin_dict[current_index][1]),
            reply_markup=create_pagination_keyboard(current_index)
        )
        str_modified_pag = modified_pag.model_dump_json(exclude_none=True)

        needed_data.modified_pagina = list_modified_pagins + [str_modified_pag]
        await session.commit()


def format_bookmark_name_button(pag_dict:dict, page_index:int)-> str:
    print('format works')
    if page_index == 4:
        page_index=3
    page = pag_dict[page_index]
    s = ''
    for x in page[1][:50]:
        if x not in '<bi>/\n🔷':
            s += x
    return s


async def check_user_in_table(user_tg_id:int):
    """Функция проверяет есть ли юзер в БД"""
    async with session_marker() as session:
        print("Work check_user Function")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        print('query = ', query)
        data = query.one_or_none()
        print('data = ', data)
        return data

async def insert_new_user_in_table(user_tg_id: int, name: str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        print('query =', query)
        needed_data = query.scalar()
        print('needed_data = ', needed_data)
        if not needed_data:
            print('Now we are into first function')
            new_us = User(tg_us_id=user_tg_id, user_name=name)
            session.add(new_us)
            await session.commit()

async def insert_new_page_in_modified_pagina(user_tg_id:int, new_page):
    '''Функция работает при старте бота и вставляет в таблицу User первую страницу'''
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('insert_first_page_in_modified_pagina')
        pagina_list = needed_data.modified_pagina
        updated_pagina_list = pagina_list + [new_page]
        needed_data.modified_pagina = updated_pagina_list
        await session.commit()

async def go_back_to_beginning(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('\ngo_back_to_beginning')
        needed_data.page = 1
        await session.commit()

async def set_new_page(user_tg_id:int, index_new_page:int):
    """Функия перелистывает страницу на запрашиваемую"""
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('\nset_new_page')
        needed_data.page = index_new_page
        await session.commit()

async def check_bookmarks(user_tg_id:int):
    """Функция проверяет есть ли у юзера закладки"""
    async with session_marker() as session:
        print("Work check_bookmarks Func")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        return needed_data.bookmarks

async def page_listai(user_id:int, schift:int):
    async with session_marker() as session:
        print("Work page_moving Func")
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        print('data = ', needed_data)
        needed_data.page +=schift
        await session.commit()

async def return_current_page_index(user_tg_id:int):
    async with session_marker() as session:
        print("Work return_current_page_index Func")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('data = ', needed_data)
        return needed_data.page

async def add_new_bookmarks(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('add_new_bookmarks works')
        want_add_this_page = needed_data.page
        bookmark_list = needed_data.bookmarks
        if want_add_this_page not in bookmark_list:
            updated_bookmarks_list = bookmark_list + [want_add_this_page]
            needed_data.bookmarks = updated_bookmarks_list
            print('updated_bookmarks_list =   ', updated_bookmarks_list)
        await session.commit()

async def return_last_nod_from_modified_pagina(user_id):
    async with session_marker() as session:
        print("Works return_last_nod_from_modified_pagina Func")
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        pagina_list = needed_data.modified_pagina
        last_nod = pagina_list.pop()
        needed_data.modified_pagina = pagina_list
        await session.commit()
        print(type(last_nod), last_nod)
        return last_nod

async def return_bookmark_list(user_tg_id:int):
    async with session_marker() as session:
        print("Works return_bookmark_list Func")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('data = ', needed_data)
        return needed_data.bookmarks

async def remove_bookmark(user_id:int, del_index:int):
    async with session_marker() as session:
        print('del_index  =      ', del_index)
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        bookmark_list = needed_data.bookmarks
        temp_arr = []
        for x in bookmark_list:
            if x != del_index:
                temp_arr.append(x)
        needed_data.bookmarks = temp_arr
        await session.commit()

async def edit_help_window(message: Message):
    """Эта асинхронная функция редактирует открытую прежде страницу в страницу help"""
    print("edit HELP FUNC WORKS")
    user_id = message.from_user.id
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        list_modified_pagins = needed_data.modified_pagina
        needed_message = list_modified_pagins.pop()
        return_to_message = Message(**json.loads(needed_message))
        msg = Message.model_validate(return_to_message).as_(bot)
        att = await message.answer_photo(
            photo=help_command[0],
            caption=help_command[1],
            reply_markup=None)
        str_att = att.model_dump_json(exclude_none=True)
        needed_data.modified_pagina = list_modified_pagins + [str_att]
        await msg.delete()
        await session.commit()

async def continue_window(message, user_id):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        list_modified_pagins = needed_data.modified_pagina
        needed_message = list_modified_pagins.pop()
        return_to_message = Message(**json.loads(needed_message))
        page_index = needed_data.page
        msg = Message.model_validate(return_to_message).as_(bot)
        att = await message.answer_photo(
            photo=pagin_dict[page_index][0],
            caption=pagin_dict[page_index][1],
            reply_markup=create_pagination_keyboard(page_index))
        json_att = att.model_dump_json(exclude_none=True)
        needed_data.modified_pagina = list_modified_pagins + [json_att]
        await msg.delete()
        await session.commit()
