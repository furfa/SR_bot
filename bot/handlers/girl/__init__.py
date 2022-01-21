from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.types import InlineKeyboardButton

from filters.sex_filter import SexFilter
from keyboards.inline.girl_secret_room import SrMenuInline
from states.girl.form import GirlFormStates
from . import forms, secret_room


def setup(dp: Dispatcher):
    # base_form = form.GirlFormBase(GirlFormStates.entered, need_approve=True)
    # base_form.register_internal_handlers(dp)
    # dp.register_message_handler(base_form.message_handler, text=["/girl_register_form"])

    girl_form = forms.GirlForm()
    girl_form.register_internal_handlers(dp)

    dp.register_message_handler(secret_room.welcome, SexFilter(is_girl=True), text=["⚜️ Secret Room"])
    dp.register_callback_query_handler(secret_room.welcome_query, SrMenuInline.back_to_secret_room.filter(), SexFilter(is_girl=True), state="*")
    dp.register_callback_query_handler(secret_room.form_menu, SrMenuInline.form_callback_data.filter(), SexFilter(is_girl=True), state="*")

    dp.register_callback_query_handler(girl_form.enter_inline, SrMenuInline.fill_form.filter(),
                                       SexFilter(is_girl=True), state="*")

    dp.register_callback_query_handler(secret_room.delete_form, SrMenuInline.delete_form.filter(),
                                       SexFilter(is_girl=True), state="*")

    girl_name_form = forms.GirlChangeName()
    girl_name_form.register_internal_handlers(dp)
    dp.register_callback_query_handler(girl_name_form.enter_inline, SrMenuInline.change_name.filter(),
                                       SexFilter(is_girl=True), state="*")

    girl_price_form = forms.GirlChangePrice()
    girl_price_form.register_internal_handlers(dp)
    dp.register_callback_query_handler(girl_price_form.enter_inline, SrMenuInline.change_price.filter(),
                                       SexFilter(is_girl=True), state="*")
