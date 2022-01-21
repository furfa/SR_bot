from aiogram import types
from aiogram.dispatcher import FSMContext

from api.base import request
from api.girl_form import GirlForm
from backend_constants.location import COUNTRY_LIST
from base.aiogram_utils import memorize_answer
from base.cleaning import clean_message_decorator
from keyboards.inline.girl_secret_room import SrMenuInline
from templates.girl.secret_room import WELCOME_MESSAGE, CREATE_FORM, FORM_ON_MODERATION, FORM_CONFIRMED, FORM_REJECTED


async def display_girl_form(gf: GirlForm):
    text = ""
    if gf.has_top_status:
        text += "🖤 Топ статус\n"

    city_list = []
    for country in COUNTRY_LIST:
        city_list.extend(country["cities"])

    if gf.country:
        text += "<b>Страна:</b> "
        for country in COUNTRY_LIST:
            if country["id"] == gf.country:
                text += country["name"]
        text += "\n"

    if gf.city:
        text += "<b>Город:</b> "
        for city in city_list:
            if city["id"] == gf.city:
                text += city["name"]
        text += "\n"

    normal_names = [
        ('NameQuestion', "Имя"),
        ('AgeQuestion', "Возраст"),
        ('BodyParamsQuestion', "Параметры тела"),
        ('NationalityQuestion', "Национальность"),
        ('PurposeQuestion', "Цели в боте"),
        ('LongFinanceQuestion', "Прайс в месяц"),
        ('ShortFinanceQuestion', "Прайс за 2-3 часа"),
        ('DocumentsQuestion', "Документы"),
        ('MarriedRelationsQuestion', "Отношения с женатыми"),
        ('AboutQuestion', "О себе"),
        ('SexQuestion', "Сексуальные предпочтения"),
        ('WorkPhoneQuestion', "Рабочий номер"),
        ('WhatsappNumberQuestion', "Номер whatsapp"),
    ]
    for normal_key, normal_name in normal_names:
        v = gf.additional_data.get(normal_key)
        if v is None:
            continue
        proc_k = normal_name
        proc_v = ""
        if type(v) == bool:
            proc_v = "Да" if v else "Нет"
        elif type(v) == list:
            proc_v = "\n  ♦️".join([""]+v)
        else:
            proc_v = v
        text += f"<b>{proc_k}</b>: {proc_v}\n"

    return text


@clean_message_decorator
async def welcome(msg: types.Message, state: FSMContext):
    await memorize_answer(msg, WELCOME_MESSAGE, reply_markup=SrMenuInline.menu())


async def welcome_query(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await query.message.edit_text(WELCOME_MESSAGE, reply_markup=SrMenuInline.menu())


async def form_menu(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await query.message.delete()
    try:
        gf = await GirlForm.get()
    except ValueError:
        await memorize_answer(query.message, CREATE_FORM, reply_markup=SrMenuInline.ask_to_create_form())
        return
    if gf.status == "CREATED":
        await memorize_answer( query.message, reply_markup=SrMenuInline.ask_to_create_form())
        return
    if gf.status == "FILLED":
        await memorize_answer(query.message, FORM_ON_MODERATION, reply_markup=SrMenuInline.only_back())
        return

    if gf.status == "CONFIRMED":
        await memorize_answer(query.message, FORM_CONFIRMED.format(await display_girl_form(gf)),
                              reply_markup=SrMenuInline.form_menu())
        return

    if gf.status == "REJECTED":
        await memorize_answer(query.message, FORM_REJECTED, reply_markup=SrMenuInline.ask_to_create_form())
        return

    await memorize_answer(query.message, CREATE_FORM, reply_markup=SrMenuInline.ask_to_create_form())


async def delete_form(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    gf = await GirlForm.update(status="DELETED")

    await query.message.edit_text("Удалено", reply_markup=SrMenuInline.only_back())
