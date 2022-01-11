from . import user


def setup(eventbus_listener):
    eventbus_listener.add_handler("new_question", user.support.question_created)
    eventbus_listener.add_handler("question_answered", user.support.question_answered)

    eventbus_listener.add_handler("new_payment_screenshot", user.account.new_payment_screenshot)
    eventbus_listener.add_handler("payment_screenshot_processed", user.account.payment_screenshot_processed)

    eventbus_listener.add_handler("new_filled_form", user.girl_form.new_form)
    eventbus_listener.add_handler("form_status_updated", user.girl_form.form_status_updated)
