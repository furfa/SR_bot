from aiogram.utils.callback_data import CallbackData

from keyboards.inline.consts import InlineConstructor
from templates.user.support import FAQ_CONTENT


class SupportKeyboardInline(InlineConstructor):
    SupportOption = CallbackData("SupportOption", "type")
    PartnerOption = CallbackData("PartnerOption", "type")
    UserTyping = CallbackData("UserTyping", "type")
    FaqOption = CallbackData("FaqOption", "question_num")
    FaqBack = CallbackData("FaqBack",)

    @staticmethod
    def menu():
        actions = [
            {'text': 'ℹ️ FAQ', 'callback_data': ({"type": "FAQ"}, SupportKeyboardInline.SupportOption)},
            {'text': '👥 Клиентская поддержка',
             'callback_data': ({"type": "client_support"}, SupportKeyboardInline.SupportOption)},
            {'text': '💻 Техническая поддержка',
             'callback_data': ({"type": "tech_support"}, SupportKeyboardInline.SupportOption)},
            {'text': '💰️ Партнерская поддержка',
             'callback_data': ({"type": "partner_support_info"}, SupportKeyboardInline.SupportOption)},
        ]
        schema = [1] * len(actions)
        return SupportKeyboardInline._create_kb(actions, schema)

    @staticmethod
    def partner_support_menu():
        actions = [
            {'text': 'Связаться', 'callback_data': ({"type": "partner_support"}, SupportKeyboardInline.PartnerOption)},
            {'text': '⬅️ Назад', 'callback_data': ({"type": "back"}, SupportKeyboardInline.PartnerOption)},
        ]
        schema = [1] * len(actions)
        return SupportKeyboardInline._create_kb(actions, schema)

    @staticmethod
    def back_to_support_menu():
        actions = [
            {'text': '⬅️ Назад', 'callback_data': ({"type": "back"}, SupportKeyboardInline.UserTyping)},
        ]
        schema = [1] * len(actions)
        return SupportKeyboardInline._create_kb(actions, schema)

    @staticmethod
    def back_to_faq_menu():
        actions = [
            {'text': '⬅️ Назад', 'callback_data': ({}, SupportKeyboardInline.FaqBack)},
        ]
        schema = [1] * len(actions)
        return SupportKeyboardInline._create_kb(actions, schema)

    @staticmethod
    def faq_menu():
        actions = []
        for i, row in enumerate(FAQ_CONTENT):
            actions.append(
                {'text': row["question"],
                 'callback_data': ({"question_num": str(i)}, SupportKeyboardInline.FaqOption)},
            )

        actions.append(
            {'text': '⬅️ Назад', 'callback_data': ({"type": "back"}, SupportKeyboardInline.PartnerOption)}
        )
        schema = [1] * len(actions)
        return SupportKeyboardInline._create_kb(actions, schema)
