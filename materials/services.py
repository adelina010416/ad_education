from datetime import datetime

import pytz
from django.core import exceptions

from config.settings import TIME_ZONE
from materials.models import Result


def check_published(obj, user):
    """
    Проверяет, опубликован ли передаваемый материал (урок/тема/тест)
    и является ли пользователь владельцем материала.
    Вызывает ошибку, если пользователь, не являющийся модератором
    или владельцем материала, пытается получить к нему доступ для просмотра.
    Возвращает материал, если проверка пройдена успешно.
    :arg
    obj -- экземпляр класса Lesson / Theme / TestPaper
    user -- экземпляр класса User"""
    is_owner = obj.owner == user
    if not obj.is_published and not user.is_staff and not is_owner:
        raise exceptions.PermissionDenied
    return obj


def create_dict(response):
    """
    Меняет тип ключей в словаре с str на int
    и тип значений с str на bool.
    :arg
    response -- словарь типа {'int': 'bool'}
    :return
    user_dict -- словарь типа {int: bool}
    """
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
    """
    Создаёт экземпляр класса Result
    для передаваемых пользователя и результатов
    :arg
    test -- экземпляр класса TestPaper
    user_results -- словарь с ответами пользователя типа {int: bool}
    user -- экземпляр класса User
    :return
    result -- экземпляр класса Result
    """
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
    """
    Создаёт список всех экземпляров класса Answer,
    относящихся к передаваемому экземпляру класса TestPaper.
    Добавляет к словарю экземпляра ключ 'user_answer'
    с Bool значением (True - если пользователь выбирал этот ответ,
    False - если не выбирал).
    :arg
    test -- экземпляр класса TestPaper
    user_answer -- словарь с ответами пользователя типа {'int': 'bool'}
    :return
    all_answers -- список словарей с экземплярами класса Answer
        и дополнительным ключом
    """
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
