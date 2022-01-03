from keyboards.default.consts import DefaultConstructor
from templates.user.start import BACK_BUTTON

class AdminMenuKeyboard(DefaultConstructor):

    @staticmethod
    def admin_menu():

        actions = [
            "Тех. Поддержка",
            BACK_BUTTON
        ]
        schema = [1] * len(actions)

        return AdminMenuKeyboard._create_kb(actions, schema)

    @staticmethod
    def support_menu():
        actions = [
            "Клиентская",
            "Техническая",
            "Личный менеджер",
            "Сотрудничество",
            BACK_BUTTON
        ]
        schema = [1] * len(actions)

        return AdminMenuKeyboard._create_kb(actions, schema, one_time_keyboard=True)