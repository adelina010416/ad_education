from datetime import datetime

import pytz
from django.core import exceptions

from config.settings import TIME_ZONE
from testing.models import Result


def check_published(obj, user):
    """Проверяет, опубликован ли передаваемый урок/тема
    и является ли пользователь владельцем урока/темы.
    Вызывает ошибку, если пользователь, не являющийся модератором
    или владельцем урока/темы, пытается получить к нему доступ для просмотра.
    Возвращает урок/тему, если всё ок.
    Args: obj: экземпляр класса Lesson или Theme
          user: экземпляр класса User"""
    is_owner = obj.owner == user
    if not obj.is_published and not user.is_staff and not is_owner:
        raise exceptions.PermissionDenied
    return obj


def create_dict(response):
    user_dict = {}
    for key, val in response.items():
        key = int(key)
        if val == 'True':
            val = True
        else:
            val = False
        user_dict[key] = val
    return user_dict


def create_result(test, user_results, user):
    all_answers = []
    for question in test.question_set.all():
        all_answers += list(question.answer_set.all())
    correct_answers = 0
    user_correct_answers = 0
    for answer in all_answers:
        if answer.is_correct:
            correct_answers += 1
    for val in create_dict(user_results).values():
        if val:
            user_correct_answers += 1
    percentage = user_correct_answers * 100 / correct_answers
    result = Result(test=test, user=user,
                    percentage=percentage,
                    date=datetime.now(pytz.timezone(TIME_ZONE)))
    result.save()
    return result


def get_user_answer_dict(test, user_answer):
    all_questions = test.question_set.all()
    user_answer = create_dict(user_answer)
    all_answers = []
    for question in all_questions:
        answers = question.answer_set.all()
        for answer in answers:
            answer_dict = answer.__dict__
            if answer_dict['id'] in user_answer.keys():
                answer_dict['user_answer'] = True
            else:
                answer_dict['user_answer'] = False
            all_answers.append(answer_dict)
    return all_answers
