import asyncio
import re

from aiogram import Dispatcher
from loguru import logger

from backend_constants.location import COUNTRY_LIST
from handlers.girl.base_questions import TextQuestion, ChoicesQuestion, MulticheckboxQuestion, BinaryQuestion, \
    MediaQuestion
import api.girl_form


class CountryQuestion(ChoicesQuestion):
    question_id = "CountryQuestion"
    question_text = "Укажите, пожалуйста, вашу страну!"

    async def choices(self):
        return [country["name"] for country in COUNTRY_LIST]

    async def processor(self, msg, choice):
        for i in COUNTRY_LIST:
            if i["name"] == choice:
                asyncio.create_task(api.girl_form.GirlForm.update(country=i["id"]))

        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["CountryQuestion"] = choice


class CityQuestion(ChoicesQuestion):
    question_id = "CityQuestion"
    question_text = "Укажите, пожалуйста, ваш город проживания!"

    async def choices(self):
        gf = await api.girl_form.GirlForm.get()
        for country in COUNTRY_LIST:
            if country["id"] == gf.country:
                return [city["name"] for city in country["cities"]]

        return []

    async def processor(self, msg, choice):
        city_list = []
        for country in COUNTRY_LIST:
            city_list.extend(country["cities"])

        for i in city_list:
            if i["name"] == choice:
                asyncio.create_task(api.girl_form.GirlForm.update(city=i["id"]))


class NameQuestion(TextQuestion):
    question_id = "NameQuestion"
    question_text = "Укажите, пожалуйста, вашe имя!"

    async def validator(self, text):
        return len(text) <= 64


class AgeQuestion(TextQuestion):
    question_id = "AgeQuestion"
    question_text = "Укажите, пожалуйста, ваш возраст! \n\n <i>♦️ От 18 лет</i>"

    async def validator(self, x):
        return re.fullmatch(r"\d+", x) and 18 <= int(x) <= 100


class BodyParamsQuestion(TextQuestion):
    question_id = "BodyParamsQuestion"
    question_text = "Укажите, пожалуйста, ваши параметры!\n\n<i>🔹 Например, 90/60/90</i>"

    async def validator(self, params):
        return re.fullmatch(r"(\d+)[ \\/](\d+)[ \\/](\d+)", params)

    async def processor(self, msg, choice):
        match = re.fullmatch(r"(\d+)[ \\/](\d+)[ \\/](\d+)", msg.text)
        body_params = match.group(1) + "/" + match.group(2) + "/" + match.group(3)
        asyncio.create_task(
            api.girl_form.GirlForm.update_additional_data_key("BodyParamsQuestion", body_params)
        )


class NationalityQuestion(TextQuestion):
    question_id = "NationalityQuestion"
    question_text = "Укажите, пожалуйста, вашу национальность!"


class PurposeQuestion(MulticheckboxQuestion):
    question_id = "PurposeQuestion"
    question_text = "Какие у вас цели в боте?"

    async def choices(self):
        return [
            "Легкие отношения",
            "Разовые встречи",
            "Путешествия",
            "Серьёзные отношения"
        ]

    async def processor_task(self, choice):
        gf = await api.girl_form.GirlForm.get()
        gf.additional_data[self.question_id] = choice
        for field in ["LongFinanceQuestion", "ShortFinanceQuestion", "DocumentsQuestion"]:
            if gf.additional_data.get(field):
                gf.additional_data.pop(field)
        await api.girl_form.GirlForm.update(additional_data=gf.additional_data)

    async def processor(self, msg, choice: list[str]):
        asyncio.create_task(
            self.processor_task(choice)
        )

        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["PurposeQuestion"] = choice

    async def next(self):
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["PurposeQuestion"] = data.get("PurposeQuestion", [])

            if "Серьёзные отношения" in data["PurposeQuestion"]:
                return "LongFinanceQuestion"

            if "Разовые встречи" in data["PurposeQuestion"]:
                return "ShortFinanceQuestion"

            if "Путешествия" in data["PurposeQuestion"]:
                return "DocumentsQuestion"

        return self.next_id


class AbstractFinanceQuestion(TextQuestion):
    async def get_currency(self):
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            country = data.get("CountryQuestion", None)
            if country is None:
                gf = await api.girl_form.GirlForm.get()
                country = ""
                for cntry_obj in COUNTRY_LIST:
                    if cntry_obj["id"] == gf.country:
                        country = cntry_obj["name"]

            if "россия" in country.lower():
                return "рублях"
        return "долларах"

    async def text(self):
        currency = await self.get_currency()
        return self.question_text.format(currency)

    async def validator(self, text):
        return re.fullmatch(r"\d+", text)

    async def processor(self, msg, choice):
        currency = await self.get_currency()
        text = msg.text + " "+("₽" if currency == "рублях" else "$")
        asyncio.create_task(
            api.girl_form.GirlForm.update_additional_data_key(self.question_id, text)
        )


class LongFinanceQuestion(AbstractFinanceQuestion):
    question_id = "LongFinanceQuestion"
    question_text = "Какую финансовую поддержу вы хотели бы получать от мужчины в месяц в {}?  \n\n<i>🔹 Пожалуйста, адекватно оценивайте свою внешность, от этого напрямую зависит сумма обеспечения девушки</i>"

    async def next(self):
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["PurposeQuestion"] = data.get("PurposeQuestion", [])

            if "Разовые встречи" in data["PurposeQuestion"]:
                return "ShortFinanceQuestion"

            if "Путешествия" in data["PurposeQuestion"]:
                return "DocumentsQuestion"

        return self.next_id


class ShortFinanceQuestion(AbstractFinanceQuestion):
    question_id = "ShortFinanceQuestion"
    question_text = "Какую сумму вы хотели бы получать за встречу 2-3 часа с адекватным мужчиной?\n\n<i>🔹 Укажите сумму в {}</i>"

    async def next(self):
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["PurposeQuestion"] = data.get("PurposeQuestion", [])

            if "Путешествия" in data["PurposeQuestion"]:
                return "DocumentsQuestion"

        return self.next_id


class DocumentsQuestion(MulticheckboxQuestion):
    question_id = "DocumentsQuestion"
    question_text = "Что у вас имеется в наличии из документов?"

    async def choices(self):
        return [
            "Только загран паспорт",
            "Виза Шенген",
            "Виза Англия",
            "Виза США"
        ]


class MarriedRelationsQuestion(BinaryQuestion):
    question_id = "MarriedRelationsQuestion"
    question_text = "Рассматриваете ли вы отношения на материальной основе с женатыми мужчинами?"


class AboutQuestion(TextQuestion):
    question_id = "AboutQuestion"
    question_text = "Расскажите немного о себе:\nОбразование, увлечения, хобби\n\n<i>🔹 Максимум 1000 символов</i>"


class SexQuestion(TextQuestion):
    question_id = "SexQuestion"
    question_text = "Расскажите о своих предпочтениях в сексе, желаниях, запретах, часто мужчине это очень важно.\n\n<i>🔹Напишите минус(-) для пропуска.</i>"


class WorkPhoneQuestion(TextQuestion):
    question_id = "WorkPhoneQuestion"
    question_text = "Укажите ваш рабочий номер телефона"

    async def validator(self, phone):
        phone = phone.strip()
        if phone == "-":
            return True
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        if not phone.startswith("+"):
            phone = "+" + phone
        try:
            import phonenumbers
            from phonenumbers import carrier, timezone, geocoder
            from phonenumbers.phonenumberutil import number_type
            return carrier._is_mobile(number_type(phonenumbers.parse(phone)))
        except Exception as e:
            logger.exception("phone number validation error")
            return False


class WhatsappNumberQuestion(TextQuestion):
    question_id = "WhatsappNumberQuestion"
    question_text = "Отправьте ваш номер whatsapp, или минус для пропуска"

    async def validator(self, phone):
        phone = phone.strip()
        if phone == "-":
            return True
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        if not phone.startswith("+"):
            phone = "+" + phone
        try:
            import phonenumbers
            from phonenumbers import carrier, timezone, geocoder
            from phonenumbers.phonenumberutil import number_type
            return carrier._is_mobile(number_type(phonenumbers.parse(phone)))
        except Exception as e:
            logger.exception("phone number validation error")
            return False


class VerificationPhotoQuestion(MediaQuestion):
    question_id = "VerificationPhotoQuestion"
    question_text = "Для того, чтобы найти Вам мужчину мы должны убедится в том, что это ваши фотографии. \nОтправьте пожалуйста в чат ваше селфи с лицом и жестом 🤞🏾, для верификации. \nПроверка проводится роботом, после подтверждения личности ваше фото удаляется из базы данных.\n Для вашего удобства и безопасности, мы боремся за то, чтобы все участники были реальными людьми.\n Спасибо за понимание! Удачных знакомств...♥️"
    is_approve = True


class AddPhotoQuestion(BinaryQuestion):
    question_id = "AddPhotoQuestion"
    question_text = "Пришлите Ваши фото и видео.\nМужчинам уже давно не интересны профессиональные фото, зачастую от того, что девушки часто в жизни выглядят совсем иначе, поэтому просим Вас быть предельно честной. \nПеречень фото, которые нужно предоставить:\n▫️ Фото или видео лица/селфи (минимум макияжа и фильтров)\n▫️ Фигура с разных ракурсов, в полный рост, в обтягивающей одежде или купальнике, где хорошо будут видны: грудь, ягодицы, ноги, живот.\▫️ Разрешается прикрепить несколько фото со студийных съёмок ▫️ Всего не более 10 фото или видео\nСовет. Если хотите найти достойного мужчину, то потратьте 20 минут своего времени и снимите новые фото. \nЕсли они не будут подходить, то Ваша анкета не пройдёт модерацию и наша администрация сообщит Вам об этом.\n Добавляем фото?"

    async def processor(self, msg, choice):
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["AddPhotoQuestion"] = ("Да" in choice)

    async def next(self):
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            if data.get("AddPhotoQuestion", False):
                return "PhotoQuestion"

        return self.next_id


class PhotoQuestion(MediaQuestion):
    question_id = "PhotoQuestion"
    question_text = "Жду фото"
    is_approve = False
