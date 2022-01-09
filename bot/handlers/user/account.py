import re
from io import BytesIO

from aiogram import types, Bot
from aiogram.dispatcher import FSMContext

from api.user import BackendUser
from keyboards.inline.account import AccountInline
from states.user.account import AccountStates
from templates.user.account import ACCOUNT_MENU, TOP_UP_BALANCE, TOP_UP_CUSTOM_AMOUNT, TOP_UP_CUSTOM_AMOUNT_WRONG


async def account_menu(msg: types.Message):
    backend_user = await BackendUser.get()
    await msg.answer(
        ACCOUNT_MENU.format(
            user_id=backend_user.id, balance=int(backend_user.balance), status=("админ" if backend_user.is_admin else "пользователь")
        ), reply_markup=AccountInline.menu()
    )


async def account_menu_query(query: types.CallbackQuery, state: FSMContext):
    backend_user = await BackendUser.get()
    await query.message.edit_text(
        ACCOUNT_MENU.format(
            user_id=backend_user.id, balance=int(backend_user.balance), status=("админ" if backend_user.is_admin else "пользователь")
        ), reply_markup=AccountInline.menu()
    )
    await state.finish()


async def top_up_balance_menu(query: types.CallbackQuery, state: FSMContext):
    backend_user = await BackendUser.get()
    await query.message.edit_text(
        TOP_UP_BALANCE.format(
            balance=int(backend_user.balance)
        ), reply_markup=AccountInline.top_up_balance_menu()
    )


async def top_up_selected_amount(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    print(callback_data)
    if callback_data["amount"] == "custom_amount":
        await query.message.edit_text(
            TOP_UP_CUSTOM_AMOUNT,
            reply_markup=AccountInline.back_to_menu()
        )
        await AccountStates.enter_custom_amount.set()
        async with state.proxy() as data:
            data["question_message"] = query.message
        return
    await query.message.edit_text(query.message.text)
    await send_select_payment(int(callback_data["amount"]))


async def top_up_custom_amount(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not re.fullmatch(r"\d+", msg.text):
            await msg.delete()
            await msg.answer(TOP_UP_CUSTOM_AMOUNT_WRONG)
            return

        if question_message := data.get("question_message"):
            await question_message.edit_text(TOP_UP_CUSTOM_AMOUNT)

        await state.finish()
        await send_select_payment(int(msg.text))


async def send_select_payment(amount):
    user = types.User.get_current()
    bot = Bot.get_current()
    await bot.send_message(
        user.id,
        "<b>Выбрана сумма</b>:\n{} SRC 🪙\n\n Выберите тип оплаты 👇".format(amount),
        reply_markup=AccountInline.payment_menu(amount)
    )


async def screenshot_payment(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    amount = int(callback_data["amount"])
    await query.message.edit_text(
        f"Пришлите скриншот оплаты на номер <b>XXXXXXXXX</b>.\n\nСумма <b>{amount*74} руб.</b>",
        reply_markup=AccountInline.back_to_menu()
    )
    await AccountStates.wait_screenshot.set()

    async with state.proxy() as data:
        data["screenshot_amount"] = amount
        data["screenshot_ask_message"] = query.message


async def screenshot_payment_get_screenshot(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        bot = Bot.get_current()
        if not msg.photo:
            await msg.answer("Нужно отправить картинку 😡")
            return
        downloaded = await bot.download_file_by_id(msg.photo[-1].file_id)
        b = BytesIO()
        b.write(downloaded.getvalue())
        with open('testfile.jpg', 'wb') as f:
            f.write(b.getvalue())
        b.seek(0)
        await bot.send_photo(msg.chat.id, b)

        if screenshot_ask_message := data.get("screenshot_ask_message"):
            await screenshot_ask_message.edit_text(screenshot_ask_message.text)

    await state.finish()