from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from loguru import logger
from contextlib import suppress

import api.base
from api.girl_form import GirlForm
from api.payment import Payment
from api.user import BackendUser, UserSupportQuestion
from handlers.girl.secret_room import display_girl_form
from keyboards.default.admin_panel import AdminMenuKeyboard
from keyboards.inline.admin_panel import AdminQuestionInline
from states.admin.admin_panel import AdminPanelStates
from templates.admin.admin_panel import SUPPORT_QUESTION_TEMPLATE, NO_SUPPORT_QUESTIONS
from templates.user.account import NO_SCREENSHOTS
from templates.user.support import QUESTION_ANSWERED


async def admin_enter(msg: types.Message):
    if not await BackendUser.check_is_admin():  # TODO: Вынести в декоротор
        return

    await AdminPanelStates.menu.set()
    await msg.answer(
        "<b>Добро пожаловать в админку</b> ✋\n\n"
        "Доступны команды:\n"
        "/send - для отправки сообщений пользователю\n"
        "/add_balance - для зачисления на баланс пользователя\n"
        "/ban - для блокировки пользователя\n"
        "/check - для детального просмотра анкеты\n"
        "/approve - для подтверждения анкеты\n"
        "/reject - для отклонения анкеты\n"
        "\n\n<i>Чтобы узнать про использование нажмите на команду</i>"
        ,
        reply_markup=AdminMenuKeyboard.admin_menu()
    )


async def support_admin(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return

    await AdminPanelStates.support_admin.set()
    await msg.answer("Выберите на какой тип поддержки вы хотите отвечать",
                     reply_markup=AdminMenuKeyboard.support_menu())


def get_filtered_support_messages_handler(filter_word):
    async def inner(msg: types.Message, state: FSMContext = None):
        questions = await UserSupportQuestion.list(type_filter=filter_word)

        if not questions:
            await msg.answer(
                NO_SUPPORT_QUESTIONS
            )
            return

        for question in questions:
            await msg.answer(
                SUPPORT_QUESTION_TEMPLATE.format(question=question.question_body, user=question.user),
                reply_markup=AdminQuestionInline.answer(question.id)
            )

    return inner


async def answer_question(query: types.CallbackQuery, callback_data: dict):
    from app import bot
    text = query.message.text
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(query.from_user.id, text=text + "\n" + ("=" * 10) + "\n Напишите ответ 👇", )
    await AdminPanelStates.support_answer.set()

    state = Dispatcher.get_current().current_state()
    async with state.proxy() as data:
        data['id'] = callback_data["id"]


async def answer_handler(msg: types.Message, state: FSMContext = None):
    async with state.proxy() as data:
        await UserSupportQuestion.update(id_=data['id'], answer_body=msg.text)

    await msg.answer("Записано👌")
    await AdminPanelStates.support_admin.set()


async def payment_admin(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return

    payments = await Payment.list(status="CREATED")

    if not payments:
        await msg.answer(
            NO_SCREENSHOTS
        )
        return

    for payment in payments:
        image = await api.base.get_image(payment.screenshot)
        text = (
            f"id: {payment.id}\n"
            f"пользователь: {payment.user}\n"
            f"статус: {payment.status}\n"
            f"сумма: <b>{payment.amount}</b>"
        )
        await msg.answer_photo(image, caption=text, reply_markup=AdminQuestionInline.approve_screenshot(payment.id))


async def payment_action(query: types.CallbackQuery, callback_data: dict):
    if not await BackendUser.check_is_admin():
        return

    if callback_data["type"] == "approve":
        backend_status = "APPROVED"
    else:
        backend_status = "REJECTED"

    await Payment.update(callback_data["id"], status=backend_status)
    await query.message.delete()


async def send_to_user(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return
    try:
        text = msg.text
        text = text.removeprefix("/send").strip()
        user_id, message_text = text.split(" ", 1)

        bot = Bot.get_current()

        await bot.send_message(user_id, message_text)
        await msg.answer("Отправлено")

    except Exception:
        await msg.answer((
            "Неверный формат или пользователь не найден\n"
            "Правильное использование команды:\n"
            "/send (идентификатор пользователя) (сообщение)"
        ))


async def add_balance_to_user(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return
    try:
        text = msg.text
        text = text.removeprefix("/add_balance").strip()
        user_id, amount = text.split(" ", 1)
        amount = float(amount)
        be = await BackendUser.get(tg_user_id=user_id)

        await BackendUser.update(tg_user_id=user_id, balance=be.balance + amount)

        await msg.answer("Баланс пополнен")

    except Exception:
        await msg.answer((
            "Неверный формат или пользователь не найден\n"
            "Правильное использование команды:\n"
            "/add_balance (идентификатор пользователя) (сумма зачисления)"
        ))



async def ban_user(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return
    try:
        text = msg.text
        text = text.removeprefix("/ban").strip()
        user_id = int(text)
        be = await BackendUser.get(tg_user_id=user_id)
        await BackendUser.update(tg_user_id=user_id, has_access=not be.has_access)
        await msg.answer(f"Пользователь {user_id} {'разбанен' if not be.has_access else 'забанен'}")

    except Exception:
        await msg.answer((
            "Неверный формат или пользователь не найден\n"
            "Правильное использование команды:\n"
            "/add_balance (идентификатор пользователя)\n"
            "При повторном использовании пользователь будет разблокирован"
        ))


async def list_users(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return
    text = ""
    for user in await BackendUser.list():
        user_text = (
            f"<b>id:</b> {user.id}\n"
            f"<b>пол:</b> {user.sex}\n"
            f"<b>баланс:</b> {user.balance}\n"
            f"<b>есть доступ:</b> {'Да' if user.has_access else 'Нет'}\n"
        )
        text += user_text
        text += "\n"

    await msg.answer(text)


async def forms(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return
    await msg.answer("Выберите какие анкеты отобразить", reply_markup=AdminQuestionInline.form_select())


async def form_view_list(query: types.CallbackQuery, callback_data: dict):
    if not await BackendUser.check_is_admin():
        return

    await query.message.edit_text(query.message.text)

    gf_list = await GirlForm.list({"status": callback_data.get("type", "")})
    if not gf_list:
        await query.message.answer("Нет анкет для проверки")
        return

    text = ""

    for gf in gf_list:
        text += (
            f"id пользователя: {gf.user}\n"
            f"статус: {gf.status}\n"
            f"топ статус: {'Да' if gf.has_top_status else 'Нет'}\n"
            f"цена: {gf.price if gf.price is not None else 'Не установлен'}"
        )
        text += "\n\n"
    await query.message.answer(
        text
    )


async def admin_gf_view(gf):
    text = await display_girl_form(gf)
    if not text:
        text = "Анкета пустая"
    else:
        text += f"\n\n<b>ID:</b> {gf.user}\n"
        text += f"<b>Статус:</b> {gf.status}\n"
        text += f"<b>Цена:</b> {gf.price}\n"
        text += f"<b>Топ статус:</b> {gf.has_top_status}\n"
    return text


async def form_detail_view(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return
    try:
        text = msg.text
        text = text.removeprefix("/check").strip()
        user_id = int(text)
        gf = await GirlForm.get(user_id)

        for photo_obj in gf.photos:
            b = await api.base.get_image(photo_obj.photo)
            caption = None
            if photo_obj.is_approve:
                caption = "Фото для подтверждения"
            await msg.answer_photo(b, caption=caption)

        await msg.answer(
            await admin_gf_view(gf)
        )
    except Exception:
        logger.exception("Error while getting detail form")
        await msg.answer((
            "Ошибка\n"
            "Правильное использование команды:\n"
            "/check (идентификатор пользователя)\n"
        ))


async def form_approve(msg: types.Message):
    if not await BackendUser.check_is_admin():
        return
    try:
        text = msg.text
        text = text.removeprefix("/approve").strip()

        user_id, price, top_status = text.split()

        user_id = int(user_id)
        price = float(price)
        if top_status not in ["+", "-"]:
            raise ValueError
        top_status = (top_status == "+")
        gf = await GirlForm.update(tg_user_id=user_id, price=price, has_top_status=top_status, status="CONFIRMED")

        await msg.answer(
            "Изменено\n\n"+
            await admin_gf_view(gf)
        )
    except Exception:
        logger.exception(f"Error while approving {msg.text=}")
        await msg.answer((
            "Ошибка\n"
            "Правильное использование команды:\n"
            "/approve (идентификатор пользователя) (прайс:число) (топ статус: +- )\n"
        ))


async def form_reject(msg: types.Message):
    try:
        text = msg.text
        text = text.removeprefix("/reject").strip()

        user_id = int(text)

        gf = await GirlForm.update(tg_user_id=user_id, status="REJECTED")

        await msg.answer(
            "Изменено\n\n"+
            await admin_gf_view(gf)
        )

    except Exception:
        logger.exception(f"Error while approving {msg.text=}")
        await msg.answer((
            "Ошибка\n"
            "Правильное использование команды:\n"
            "/reject (идентификатор пользователя)\n"
        ))