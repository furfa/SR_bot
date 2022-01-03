from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from states.admin.admin_panel import AdminPanelStates
from keyboards.inline.callbacks import AdminQuestionAnswer
from . import admin_panel


def setup(dp: Dispatcher):
    dp.register_message_handler(admin_panel.admin_enter, text=["/adminpanel"], state='*')
    dp.register_message_handler(admin_panel.support_admin, text=["Тех. Поддержка"], state=AdminPanelStates.menu)

    support_admin_filters = (
        ("Клиентская", "CLIENT"),
        ("Техническая", "TECHNICAL"),
        ("Личный менеджер","PERSONAL_MANAGER"),
        ("Сотрудничество","PARTNERSHIP")
    )
    for key_word, backend_name in support_admin_filters:
        dp.register_message_handler(
            admin_panel.get_filtered_support_messages_handler(backend_name),
            text=[key_word],
            state=AdminPanelStates.support_admin
        )

    dp.register_callback_query_handler(admin_panel.answer_question, AdminQuestionAnswer.filter(), state='*')
    dp.register_message_handler(admin_panel.answer_handler, state=AdminPanelStates.support_answer)
