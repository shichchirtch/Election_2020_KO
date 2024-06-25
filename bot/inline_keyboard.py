from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pagination import pagin_dict

def create_pagination_keyboard(page=1) -> InlineKeyboardMarkup:
    forward_button = InlineKeyboardButton(text=f'>>', callback_data='forward')
    middle_button = InlineKeyboardButton(text=f'{page} / {len(pagin_dict)}', callback_data=f'{page} / {len(pagin_dict)}')
    backward_button = InlineKeyboardButton(text='<<', callback_data='backward')
    if page == 1:
        pagination_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[middle_button, forward_button]])
        return pagination_keyboard
    elif 1 < page < len(pagin_dict):
        pagination_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[backward_button, middle_button, forward_button]])
        return pagination_keyboard
    else:
        pagination_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[backward_button, middle_button]])
        return pagination_keyboard
