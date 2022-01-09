from aiogram import types

from .consts import InlineConstructor
from aiogram.utils.callback_data import CallbackData


class AccountInline(InlineConstructor):
    account_callback_data = CallbackData("AccountInline", "action")
    top_up_balance_callback_data = CallbackData("TopUpInline", "amount")
    back_menu = CallbackData("AccountBack", "target")
    screenshot_payment = CallbackData("ScreenshotPayment", "amount")

    @staticmethod
    def menu():
        schema = [1]
        actions = [
            {'text': '💰 Пополнить баланс',
             'callback_data': ({"action": "top_up_balance"}, AccountInline.account_callback_data)}
        ]
        return AccountInline._create_kb(actions, schema)

    @staticmethod
    def back_to_menu():
        schema = [1]
        actions = [
            {'text': f"🔙 Назад",
             'callback_data': ({"target": "menu"}, AccountInline.back_menu)}
        ]
        return AccountInline._create_kb(actions, schema)

    @staticmethod
    def top_up_balance_menu():
        actions = []
        for amount in [20, 50, 100, 200, 500, 1000]:
            actions.append(
                {
                    'text': f"{amount} SRC 🪙",
                    'callback_data': ({"amount": amount}, AccountInline.top_up_balance_callback_data)
                }
            )
        schema = [2, 2, 2]

        actions.append(
            {
                'text': f"Другое количество 🪙",
                'callback_data': ({"amount": "custom_amount"}, AccountInline.top_up_balance_callback_data)
            }
        )
        schema.append(1)

        actions.append(
            {
                'text': f"🔙 Назад",
                'callback_data': ({"target": "menu"}, AccountInline.back_menu)
            }
        )
        schema.append(1)

        return AccountInline._create_kb(actions, schema)

    @staticmethod
    def payment_menu(amount):
        schema = [1, 1]
        actions = [
            {'text': f"📲 Скриншотом",
             'callback_data': ({"amount": amount}, AccountInline.screenshot_payment)},
            {'text': f"🔙 Назад",
             'callback_data': ({"target": "menu"}, AccountInline.back_menu)}
        ]
        return AccountInline._create_kb(actions, schema)