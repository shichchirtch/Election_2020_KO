from aiogram.types import CallbackQuery, Message
from aiogram.filters import BaseFilter
from pagination import pagin_dict
from external_functions import check_user_in_table

class MOVE_PAGE(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data in ['forward', 'backward']:
            return True
        return False

class CHECK_NUMBER(BaseFilter):
    async def __call__(self, message: Message):
        print("WORKs check number filter")
        if (message.text.startswith('/') and message.text[1:].isdigit()
                and 0 < int(message.text[1:]) < len(pagin_dict)):
            return True
        elif message.text.isdigit() and 0 < int(message.text) <= len(pagin_dict):
            return True
        else:
            print('CHECK NUMBER RETURN FALSE')
            return False


class PRE_START(BaseFilter):
    async def __call__(self, message: Message):
        print("PRE_START Filter works")
        user_tg_id = message.from_user.id
        if await check_user_in_table(user_tg_id):
            return False
        return True


class IS_DIGIT_CALLBACK_DATA(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.isdigit()


class IS_DEL_BUCKMARK(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        print('Works IS_DEL_BUCKMARK')
        return callback.data.endswith('del') and callback.data[:-3].isdigit()