from handlers.girl.base_form import GirlFormBase
from handlers.girl.base_questions import QuestionTree
from handlers.girl.questions import CountryQuestion, CityQuestion, NameQuestion, AgeQuestion, BodyParamsQuestion, \
    NationalityQuestion, DocumentsQuestion, PurposeQuestion, ShortFinanceQuestion, LongFinanceQuestion, \
    MarriedRelationsQuestion, AboutQuestion, SexQuestion, WorkPhoneQuestion, WhatsappNumberQuestion, \
    VerificationPhotoQuestion, AddPhotoQuestion, PhotoQuestion
from states.girl.form import GirlFormStates, GirlFormNameStates, GirlFormPriceStates


class GirlChangePrice(GirlFormBase):
    def __init__(self):
        self.enter_state = GirlFormNameStates.entered
        self.need_approve = False

        self.question_handlers = QuestionTree.from_nodes(
            PurposeQuestion(prev_id="ENTER", next_id="MarriedRelationsQuestion"),
            LongFinanceQuestion(prev_id="PurposeQuestion", next_id="EXIT"),
            ShortFinanceQuestion(prev_id="PurposeQuestion", next_id="EXIT"),
            DocumentsQuestion(prev_id="PurposeQuestion", next_id="EXIT"),
        )


class GirlChangeName(GirlFormBase):
    def __init__(self):
        self.enter_state = GirlFormPriceStates.entered
        self.need_approve = False

        self.question_handlers = QuestionTree.from_nodes(
            NameQuestion(prev_id="ENTER", next_id="EXIT"),
        )


class GirlForm(GirlFormBase):
    def __init__(self):
        self.enter_state = GirlFormStates.entered
        self.need_approve = True
        self.question_handlers = QuestionTree.from_nodes(
            CountryQuestion(prev_id="ENTER", next_id="CityQuestion"),
            CityQuestion(prev_id="CountryQuestion", next_id="NameQuestion"),
            NameQuestion(prev_id="CityQuestion", next_id="AgeQuestion"),
            AgeQuestion(prev_id="NameQuestion", next_id="BodyParamsQuestion"),
            BodyParamsQuestion(prev_id="AgeQuestion", next_id="NationalityQuestion"),
            NationalityQuestion(prev_id="BodyParamsQuestion", next_id="PurposeQuestion"),
            PurposeQuestion(prev_id="NationalityQuestion", next_id="MarriedRelationsQuestion"),
            LongFinanceQuestion(prev_id="PurposeQuestion", next_id="MarriedRelationsQuestion"),
            ShortFinanceQuestion(prev_id="PurposeQuestion", next_id="MarriedRelationsQuestion"),
            DocumentsQuestion(prev_id="PurposeQuestion", next_id="MarriedRelationsQuestion"),
            MarriedRelationsQuestion(prev_id="PurposeQuestion", next_id="AboutQuestion"),
            AboutQuestion(prev_id="MarriedRelationsQuestion", next_id="SexQuestion"),
            SexQuestion(prev_id="AboutQuestion", next_id="WorkPhoneQuestion"),
            WorkPhoneQuestion(prev_id="SexQuestion", next_id="WhatsappNumberQuestion"),
            WhatsappNumberQuestion(prev_id="WorkPhoneQuestion", next_id="VerificationPhotoQuestion"),
            VerificationPhotoQuestion(prev_id="WhatsappNumberQuestion", next_id="AddPhotoQuestion"),
            AddPhotoQuestion(prev_id="VerificationPhotoQuestion", next_id="EXIT"),
            PhotoQuestion(prev_id="AddPhotoQuestion", next_id="AddPhotoQuestion")
        )