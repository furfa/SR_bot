from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.types import InlineKeyboardButton

from filters.sex_filter import SexFilter
from keyboards.inline.girl_secret_room import SrMenuInline
from . import form, secret_room


async def setup(dp: Dispatcher):
    girl_form = await form.GirlForm.create()
    dp.register_message_handler(girl_form.message_handler, text=["/girl_register_form"])
    girl_form.register_internal_handlers(dp)

    dp.register_message_handler(secret_room.welcome, SexFilter(is_girl=True))
    dp.register_callback_query_handler(secret_room.welcome_query, SrMenuInline.back_to_secret_room.filter(), SexFilter(is_girl=True), state="*")
    dp.register_callback_query_handler(secret_room.form_menu, SrMenuInline.form_callback_data.filter(), SexFilter(is_girl=True), state="*")

    dp.register_callback_query_handler(girl_form.enter_inline, SrMenuInline.fill_form.filter(),
                                       SexFilter(is_girl=True), state="*")

    dp.register_callback_query_handler(secret_room.delete_form, SrMenuInline.delete_form.filter(),
                                       SexFilter(is_girl=True), state="*")

    girl_name_form = await form.GirlChangeName.create()
    girl_name_form.register_internal_handlers(dp)
    dp.register_callback_query_handler(girl_name_form.enter_inline, SrMenuInline.change_name.filter(),
                                       SexFilter(is_girl=True), state="*")

    girl_price_form = await form.GirlChangePrice.create()
    girl_price_form.register_internal_handlers(dp)
    dp.register_callback_query_handler(girl_price_form.enter_inline, SrMenuInline.change_price.filter(),
                                       SexFilter(is_girl=True), state="*")
