from . import user


def setup(eventbus_listener):
    eventbus_listener.add_handler("new_question", user.support.question_answered)

    eventbus_listener.add_handler("new_payment_screenshot", user.account.new_payment_screenshot)
    eventbus_listener.add_handler("payment_screenshot_processed", user.account.payment_screenshot_processed)