from keyboards.default.consts import DefaultConstructor


class MainMenuKeyboard(DefaultConstructor):

    @staticmethod
    def select_sex():
        schema = [2]
        actions = [
            '👨🏽 Мужчина',
            '👩🏽 Девушка',
        ]
        return MainMenuKeyboard._create_kb(actions, schema)

    @staticmethod
    def main_menu():
        schema = [2, 1]
        actions = [
            '👤 Мой аккаунт',
            '⚜️ Secret Room',
            '📤 Связь',
        ]
        return MainMenuKeyboard._create_kb(actions, schema)
