from aiogram import types
from aiogram.dispatcher import FSMContext

from api.base import request
from api.girl_form import GirlForm
from keyboards.inline.girl_secret_room import SrMenuInline
from templates.girl.secret_room import WELCOME_MESSAGE, CREATE_FORM, FORM_ON_MODERATION, FORM_CONFIRMED, FORM_REJECTED


async def display_girl_form(gf: GirlForm):
    text = ""
    if gf.has_top_status:
        text += "🖤 Топ статус\n"

    # Говнокод
    country_list = await request("get", "location/country/")
    city_list = []
    for country in country_list:
        city_list.extend(country["cities"])

    if gf.country:
        text += "<b>Страна:</b> "
        for country in country_list:
            if country["id"] == gf.country:
                text += country["name"]
        text += "\n"

    if gf.city:
        text += "<b>Город:</b> "
        for city in city_list:
            if city["id"] == gf.city:
                text += city["name"]
        text += "\n"

    normal_names = {
        'age': "Возраст",
        'sex': "Сексуальные предпочтения",
        'name': "Имя",
        'about': "О себе",
        'short': "Короткие свидания",
        'abroad': "Поездки за границу",
        'documents': "Документы",
        'body_params': "Параметры тела",
        'short_amount': "Прайс за короткие свидания",
        'finance_support': "Финансовая поддержка",
        'whatsapp_number': "Номер whatsapp",
        'married_relations': "Отношения с женатыми",
        'work_phone_number': "Рабочий номер",
        'sponsorship_relations': "Спонсорские отношения",
        'nationality': "Национальность"
    }
    for k, v in gf.additional_data.items():
        if v is None:
            continue
        if not normal_names.get(k):
            continue
        proc_k = normal_names[k]
        proc_v = ""
        if type(v) == bool:
            proc_v = "Да" if v else "Нет"
        elif type(v) == list:
            proc_v = ", ".join(v)
        else:
            proc_v = v
        text += f"<b>{proc_k}</b>: {proc_v}\n"
    return text


async def welcome(msg: types.Message):
    await msg.answer(WELCOME_MESSAGE, reply_markup=SrMenuInline.menu())


async def welcome_query(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await query.message.edit_text(WELCOME_MESSAGE, reply_markup=SrMenuInline.menu())


async def form_menu(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await query.message.delete()
    try:
        gf = await GirlForm.get()
    except ValueError:
        await query.message.answer(CREATE_FORM, reply_markup=SrMenuInline.ask_to_create_form())
        return
    if gf.status == "CREATED":
        await query.message.answer(CREATE_FORM, reply_markup=SrMenuInline.ask_to_create_form())
        return
    if gf.status == "FILLED":
        await query.message.answer(FORM_ON_MODERATION, reply_markup=SrMenuInline.only_back())
        return

    if gf.status == "CONFIRMED":
        await query.message.answer(FORM_CONFIRMED.format(await display_girl_form(gf)),
                                      reply_markup=SrMenuInline.form_menu())
        return

    if gf.status == "REJECTED":
        await query.message.answer(FORM_REJECTED, reply_markup=SrMenuInline.ask_to_create_form())
        return

    await query.message.answer(CREATE_FORM, reply_markup=SrMenuInline.ask_to_create_form())


async def delete_form(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    gf = await GirlForm.update(status="DELETED")

    await query.message.edit_text("Удалено", reply_markup=SrMenuInline.only_back())
