from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp

import states.user.start
from keyboards.inline.support import SupportKeyboardInline
from templates.user.start import BACK_BUTTON
from templates.user.support import BACK_TO_SUPPORT
from . import support, start, help


def setup(dp: Dispatcher):
    dp.register_message_handler(help.bot_help, CommandHelp())
    # start.py
    dp.register_message_handler(start.bot_start, CommandStart(), state='*')
    dp.register_message_handler(start.bot_start, text=[BACK_BUTTON], state='*')

    dp.register_message_handler(start.selected_male, text=['Мужчина'], state=states.user.start.MainMenuStates.select_sex)
    dp.register_message_handler(start.selected_girl, text=['Девушка'], state=states.user.start.MainMenuStates.select_sex)

    # support.py
    dp.register_message_handler(support.support_start, text=['📤 Связь'])
    dp.register_callback_query_handler(support.faq_info,
                                       SupportKeyboardInline.SupportOption.filter(type="FAQ"), state="*")
    dp.register_callback_query_handler(support.faq_info,
                                       SupportKeyboardInline.FaqBack.filter(), state="*")
    dp.register_callback_query_handler(support.faq_display_question_answer,
                                       SupportKeyboardInline.FaqOption.filter(), state="*")
    dp.register_callback_query_handler(support.support_callback_handler,
                                       SupportKeyboardInline.SupportOption.filter(type="tech_support"), state="*")
    dp.register_callback_query_handler(support.support_callback_handler,
                                       SupportKeyboardInline.SupportOption.filter(type="client_support"), state="*")
    dp.register_callback_query_handler(support.partnership_support_info,
                                       SupportKeyboardInline.SupportOption.filter(type="partner_support_info"), state="*")
    dp.register_callback_query_handler(support.back_to_support,
                                       SupportKeyboardInline.PartnerOption.filter(type="back"), state="*")
    dp.register_callback_query_handler(support.support_callback_handler,
                                       SupportKeyboardInline.PartnerOption.filter(type="partner_support"), state="*")
    dp.register_callback_query_handler(support.back_to_support,
                                       SupportKeyboardInline.UserTyping.filter(type="back"), state="*")

    for state in (
        states.user.support.SupportStates.partnership,
        states.user.support.SupportStates.client,
        states.user.support.SupportStates.technical,
    ):
        dp.register_message_handler(support.question_handler, state=state)

