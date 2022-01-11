from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from keyboards.inline.admin_panel import AdminQuestionInline
from states.admin.admin_panel import AdminPanelStates
from keyboards.inline.callbacks import AdminQuestionAnswer
from . import admin_panel


def setup(dp: Dispatcher):
    dp.register_message_handler(admin_panel.admin_enter, commands=["adminpanel"], state="*")
    dp.register_message_handler(admin_panel.send_to_user, commands=["send"], state="*")
    dp.register_message_handler(admin_panel.add_balance_to_user, commands=["add_balance"], state="*")
    dp.register_message_handler(admin_panel.ban_user, commands=["ban"], state="*")
    dp.register_message_handler(admin_panel.form_detail_view, commands=["check"], state="*")
    dp.register_message_handler(admin_panel.form_approve, commands=["approve"], state="*")
    dp.register_message_handler(admin_panel.form_reject, commands=["reject"], state="*")

    dp.register_message_handler(admin_panel.support_admin, text=["Тех. Поддержка"], state=AdminPanelStates.menu)
    dp.register_message_handler(admin_panel.list_users, text=["Пользователи"], state=AdminPanelStates.menu)

    dp.register_message_handler(admin_panel.forms, text=["Анкеты"], state=AdminPanelStates.menu)
    dp.register_callback_query_handler(admin_panel.form_view_list, AdminQuestionInline.form_select_callback_data.filter(), state="*")

    support_admin_filters = (
        ("Клиентская", "CLIENT"),
        ("Техническая", "TECHNICAL"),
        ("Личный менеджер", "PERSONAL_MANAGER"),
        ("Сотрудничество", "PARTNERSHIP")
    )
    for key_word, backend_name in support_admin_filters:
        dp.register_message_handler(
            admin_panel.get_filtered_support_messages_handler(backend_name),
            text=[key_word],
            state=AdminPanelStates.support_admin
        )

    dp.register_callback_query_handler(admin_panel.answer_question, AdminQuestionAnswer.filter(), state='*')
    dp.register_message_handler(admin_panel.answer_handler, state=AdminPanelStates.support_answer)

    dp.register_message_handler(admin_panel.payment_admin, text=["Пополнения"], state=AdminPanelStates.menu)
    dp.register_callback_query_handler(admin_panel.payment_action, AdminQuestionInline.approve_screenshot_callback_data.filter(), state='*')


