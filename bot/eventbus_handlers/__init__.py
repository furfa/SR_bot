from . import user


def setup(eventbus_listener):
    eventbus_listener.add_handler("new_question", user.support.question_answered)