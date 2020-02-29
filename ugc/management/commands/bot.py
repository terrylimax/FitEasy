from django.core.management.base import BaseCommand

from django.conf import settings
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, Update
from telegram.utils.request import Request
from emoji import emojize
import logging
import random
from projectb.settings import load_config
import requests
import json
import sys
import time
import uuid

from ugc.models import Profile, Vitamin, Training, Nutrition, Payments

#enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

logger = logging.getLogger(__name__)

NAME, SELECTING_PROGRAM, GENDER, AGE, WEIGHT, PHYS_LOADS_VITAMINS, STRESS_VITAMINS,\
    WEAKNESS_VITAMINS, SUN_OFTEN, GOAL, GAIN_LOSE_KEEP, SPORT_LVL, MEAT, HEIGHT, PHYS_LOADS_NUTR = range(15)


def log_errors(f):

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


def start(update, context):
    blush = emojize(":blush:", use_aliases=True)
    user = update.message.from_user
    update.message.reply_text(
        "Привет! Рад, что ты думаешь о своем здоровье!\nПеред тем, как подобрать программу, напиши свое имя " + blush, reply_markup=ReplyKeyboardRemove())
    return NAME


@log_errors
def name_handler(update, context):
    chat_id = update.message.chat_id
    name = update.message.text
    username = update.message.from_user.username
    if username == None:
        username = 'no username'
    context.user_data[NAME] = update.message.text
    logger.info("Name of %s: %s", username, name)

    p, _ = Profile.objects.update_or_create(
        external_id=chat_id,
        defaults={
            'username': username,
            'name': name,
        }
    )
    reply_keyboard = [['Тренировки'], ['Питание'], ['Витамины']]
    reply_text = f'Привет, {name}! Рад знакомству!\nКакую программу ты хочешь подобрать?'
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))

    return SELECTING_PROGRAM


@log_errors
def program_handler(update, context):
    user = update.message.from_user
    context.user_data[SELECTING_PROGRAM] = update.message.text

    chat_id = update.message.chat_id
    program = update.message.text
    p, _ = Profile.objects.update_or_create(
        external_id=chat_id,
        defaults={
            'program_type': program,
        }
    )
    logger.info("Type of program for %s: %s", user.first_name, update.message.text)
    reply_keyboard = [['Мужчина', 'Женщина']]
    update.message.reply_text(
        'Отлично! Теперь укажи свой пол. ',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True, one_time_keyboard=True))
    return GENDER

@log_errors
def gender_handler(update, context):
    user = update.message.from_user
    context.user_data[GENDER] = update.message.text
    book = emojize(":book:", use_aliases=True)

    chat_id = update.message.chat_id
    gender = update.message.text
    p, _ = Profile.objects.update_or_create(
        external_id=chat_id,
        defaults={
            'gender': gender,
        }
    )

    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Понял, теперь скажи, сколько тебе лет? \n\n'
                              'Нам нужен этот и дальнейшие параметры для определения твоих нагрузок на тренировках'
                              ', объема каллоража питания и необходимых препаратов. \n\n'
                              'Если хочешь узнать, как они используются в наших расчетах, после ответа на все '
                              'вопросы мы дадим ссылку, '
                              'пройдя по которой можно узнать все способы и формулы расчета '
                              'программ питания и витаминов ' + book, reply_markup=ReplyKeyboardRemove())
    return AGE


@log_errors
def age_handler(update, context):
    context.user_data[AGE] = update.message.text

    chat_id = update.message.chat_id
    age = update.message.text
    p, _ = Profile.objects.update_or_create(
        external_id=chat_id,
        defaults={
            'age': age,
        }
    )

    user = update.message.from_user
    logger.info("Age of %s: %s", user.first_name, int(update.message.text))
    update.message.reply_text('Супер! Каков твой вес сейчас в килограммах? ')
    return WEIGHT


@log_errors
def weight_handler(update, context):
    context.user_data[WEIGHT] = update.message.text

    chat_id = update.message.chat_id
    weight = update.message.text
    p, _ = Profile.objects.update_or_create(
        external_id=chat_id,
        defaults={
            'weight': weight,
        }
    )

    user = update.message.from_user
    logger.info("Weight of %s: %s", user.first_name, int(update.message.text))
    if context.user_data[SELECTING_PROGRAM] == 'Витамины':
        reply_keyboard = [['Очень большие - хожу в зал 5 раз/неделю или моя работа требует физических нагрузок'],
                          ['Хожу в тренажерный зал 2-3 раза в неделю'],
                          ['Иногда бегаю'],
                          ['Нет физических нагрузок']]
        update.message.reply_text(
            "Отлично! Какие у тебя есть физические нагрузки?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return PHYS_LOADS_VITAMINS

    elif context.user_data[SELECTING_PROGRAM] != 'Витамины':
        reply_keyboard = [['Набрать вес'],
                          ['Сбросить вес'],
                          ['Поддерживать форму']]
        update.message.reply_text(
            "Отлично! Какая у тебя цель?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return GOAL
        
        
#def uniqid(prefix = ''):
    #return prefix + hex(int(time()))[2:10] + hex(int(time()*1000000) % 0x100000)[2:7]

@log_errors
def phys_loads_handler(update, context):
    user = update.message.from_user
    logger.info("%s's loads are: %s", user.first_name, update.message.text)

    if context.user_data[SELECTING_PROGRAM] == 'Питание':
        context.user_data[PHYS_LOADS_NUTR] = update.message.text

        chat_id = update.message.chat_id
        loads = update.message.text
        p, _ = Profile.objects.get_or_create(external_id=chat_id)
        Nutrition.objects.update_or_create(
            profile=p,
            defaults={
                'phys_loads': loads,
            }
        )
        global pr
        global carbs
        global fat
        if context.user_data[GENDER] == "Мужчина":
            s = 5
            m = float(context.user_data[WEIGHT])
            h = float(context.user_data[HEIGHT])
            a = float(context.user_data[AGE])
            # standart BMR calculation
            bmr = 10 * m + 6.25 * h - 5 * a + s
            bmr_in_motion = bmr * PAL_convertation(context.user_data[PHYS_LOADS_NUTR])
            list_result = percent_deficit_surplus(context.user_data[GOAL])
            deficit_surplus_keep = list_result[2] * bmr_in_motion
            pr = round ((list_result[0] * deficit_surplus_keep)/4)
            carbs = round((list_result[1] * deficit_surplus_keep)/4)
            fat = round((0.25 * deficit_surplus_keep)/9)
            reply_text = f'Поздравляю! Ты прошел весь опрос!\nБазовый уровень твоего метаболизма: {round(bmr)} ' \
                         f'калорий/день\n' \
                         f'Твоя норма калорий для поддержки веса: {round(bmr_in_motion)} калорий/день\n' \
                         f'{list_result[3]} {round(deficit_surplus_keep)} калорий/день\n' \
                         f'БЖУ соотношение: \n' \
                         f'*Белков*: {pr}\n' \
                         f'*Углеводов*: {carbs}\n' \
                         f'*Жиров*: {fat}\n' \
                         f'Подсчет BMR проводился в соответсвии с формулой Миффлина-Сан Жеора и исполь' \
                         f'зовании коэффициента физической активности.\n' \
                         f'Источники: \n' \
                         f'[Wikipedia BMR](https://en.wikipedia.org/wiki/Basal_metabolic_rate)\n' \
                         f'[Wikipedia PAL](https://en.wikipedia.org/wiki/Physical_activity_level)\n' \
                         f'[GoodLooker](https://goodlooker.ru/podschet-kalorij.html)\n' \
                         f'[статья Дениса Гусева](https://the-challenger.ru/eda/kak-pravilno-eda-new/kak-rasschityvat-bzhu-i-zachem-eto-nuzhno/)'

        else:
            s = -161
            m = float(context.user_data[WEIGHT])
            h = float(context.user_data[HEIGHT])
            a = float(context.user_data[AGE])
            bmr = 10 * m + 6.25 * h - 5 * a + s
            bmr_in_motion = bmr * PAL_convertation(context.user_data[PHYS_LOADS_NUTR])
            list_result = percent_deficit_surplus(context.user_data[GOAL])
            deficit_surplus_keep = list_result[2] * bmr_in_motion
            pr = round((list_result[0] * deficit_surplus_keep) / 4)
            carbs = round((list_result[1] * deficit_surplus_keep) / 4)
            fat = round((0.25 * deficit_surplus_keep) / 9)
            reply_text = f'Поздравляю! Ты прошла весь опрос!\nБазовый уровень твоего метаболизма: {round(bmr)} ' \
                         f'калорий/день\n' \
                         f'Твоя норма калорий для поддержки веса: {round(bmr_in_motion)} калорий/день\n' \
                         f'{list_result[3]} {round(deficit_surplus_keep)} калорий/день\n' \
                         f'БЖУ соотношение: \n' \
                         f'*Белки*: {pr}\n' \
                         f'*Углеводы*: {carbs}\n' \
                         f'*Жиры*: {fat}\n' \
                         f'Подсчет BMR проводился в соответсвии с формулой Миффлина-Сан Жеора и исполь' \
                         f'зовании коэффициента физической активности.\n' \
                         f'Источники: \n' \
                         f'[Wikipedia BMR](https://en.wikipedia.org/wiki/Basal_metabolic_rate)\n' \
                         f'[Wikipedia PAL](https://en.wikipedia.org/wiki/Physical_activity_level)\n' \
                         f'[GoodLooker](https://goodlooker.ru/podschet-kalorij.html)\n' \
                         f'[статья Дениса Гусева](https://the-challenger.ru/eda/kak-pravilno-eda-new/kak-rasschityvat-bzhu-i-zachem-eto-nuzhno/)'

        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN,
                                  disable_web_page_preview=True)
        update.message.reply_photo('https://drive.google.com/file/d/17k8McHat1qcqFrp_isTiO48w0D9hgiXx/view?usp=sharing',
                                       caption = 'Это *примерный список продуктов*, который можно использовать '
                                                 'в твоем рационе при составлении плана питания', parse_mode = ParseMode.MARKDOWN)
        plans = nutrition()
        text_plans = f'*ВНИМАНИЕ! Продукты взвешиваются в СУХОМ(неприготовленном) виде* \n\n' \
                     f'*Твоя программа питания на первый день:* \n\n' \
                     f'{plans[0]}' \
                     f'*Твоя программа питания на второй день:* \n\n' \
                     f'{plans[1]}'
        

        client_id = 'D39B135760893C3E1EF5F5FBA1C006CC744BE79959883217490829F70D1B9D59'
        h = requests.post('https://money.yandex.ru/api/instance-id',  data={'client_id': client_id})
        req = json.loads(h.text)
       # print(req)
        instance_id = req['instance_id']
        account_number = '4100110996845190'
        amount_due = 1
        k = requests.post('https://money.yandex.ru/api/request-external-payment',  data={'pattern_id': 'p2p','instance_id': instance_id,'to': account_number,'amount_due': amount_due})
        rek = json.loads(k.text)
       # print(rek)
        request_id = rek['request_id']
        #при успешной оплате человека переносит на сервер, чтобы обработать успешную или неудачную оплату
        key_succ = str(uuid.uuid4())
        key_fail = str(uuid.uuid4())
        payment = Payments(
            profile = Profile.objects.get(external_id = update.message.chat_id),
            key_succ = key_succ, 
            is_activated = False,
            product_id = 2,
        )
        payment.save()
        process_payment = requests.post('https://money.yandex.ru/api/process-external-payment', data={'request_id': request_id,'instance_id': instance_id, 'ext_auth_success_uri': 'http://51.38.83.214:8081/?key='+key_succ,'ext_auth_fail_uri': 'http://51.38.83.214:8081/?key='+key_fail})
        #сделать на питоне веб-сервер, который будет обрабатывать все запросы (с правильными портами)
        process_payment_json = json.loads(process_payment.text)
       # print(process_payment_json)
        acs_params = process_payment_json['acs_params']
        acs_url = str(process_payment_json['acs_uri']) + '?'+ 'cps_context_id=' + acs_params['cps_context_id'] + '&paymentType=' + acs_params['paymentType'] 
       # print(acs_params)
       # print(acs_url)
        #Кнопка оплаты
        keyboard = [[InlineKeyboardButton(text = "Получить программу", url=acs_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f'Для получения подробной программы перейди по ссылке'
        update.message.reply_text(text, reply_markup=reply_markup,
                                  disable_web_page_preview=True)
        return ConversationHandler.END

    elif context.user_data[SELECTING_PROGRAM] == 'Витамины':
        context.user_data[PHYS_LOADS_VITAMINS] = update.message.text

        chat_id = update.message.chat_id
        loads = update.message.text
        p, _ = Profile.objects.get_or_create(external_id=chat_id)
        Vitamin.objects.update_or_create(
            profile = p,
            defaults={
                'phys_loads': loads,
            }
        )

        reply_keyboard = [['Часто'],
                          ['Нечасто'],
                          ['Нету стресса']]
        update.message.reply_text(
            "Как часто ты испытываешь стресс?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return STRESS_VITAMINS


@log_errors
def nutrition():
    text1 = f'text1'
    text2 = f'text2'
    text3 = f'text3'
    text4 = f'text4'
    # Наименование продукта,Б,Ж,У
    nutrition_dict = {1: ['Овсянка', 11.9, 5.8, 65.4], 2: ['Тунец', 22.4, 1.29, 0.11],
                      3: ['Бездрожжевой хлеб', 5.77, 0.51, 37.54],
                      4: ['Бурый рис', 7.8, 2.2, 76.7], 5: ['Куриное филе', 23.6, 1.9, 0.4],
                      6: ['Греча', 12.6, 3.3, 62.1],
                      7: ['Филе индейки', 19.2, 0.7, 0.0], 8: ['Грецкий орех', 15.2, 65.2, 7.0],
                      9: ['Гречневая каша', 4.5, 2.3, 25.0],
                      10: ['Макароны твердых сортов', 10.4, 1.1, 71.5], 11: ['Баранина', 15.6, 16.3, 0.0],
                      12: ['Арахисовая паста', 26.3, 45.2, 9.9], 13: ['Малиновое варенье', 0.6, 0.2, 70.4],
                      14: ['Рис белый', 6.7, 0.7, 78.9],
                      15: ['Перловая крупа', 9.3, 1.1, 73.7], 16: ['Говядина', 18.9, 12.4, 0.0],
                      17: ['Абрикосовый джем', 0.6, 0.1, 41.6]}

    dict_weight_lose = {1: text1, 2: text2, 3: text3, 4: text4}
    chosen_key1 = random.choice(list(dict_weight_lose.keys()))
    if chosen_key1 == 1:
        dict_weight_lose[1] = f'Первый прием пищи \n' \
                           f'Овсянка ({round(((0.15*carbs)*100)/nutrition_dict.get(1)[3])} г) с сухофруктами\n' \
                           f'Бутерброд: тунец({round(((0.05*pr)*100)/nutrition_dict.get(2)[1])} г) и ' \
                           f'бездрожжевой хлеб ({round(((0.1*carbs)*100)/nutrition_dict.get(3)[3])} г) \n' \
                           f'Фрукты: банан \n' \
                           f'Арахисовая паста ({round(((0.1*fat)*100)/nutrition_dict.get(12)[2])} г) \n\n' \
                           f'Второй прием пищи: \n' \
                           f'Бурый рис ({round(((0.25*carbs)*100)/nutrition_dict.get(4)[3])} г) \n' \
                           f'Куриная грудка ({round(((0.3*pr)*100)/nutrition_dict.get(5)[1])} г) \n' \
                           f'Баклажаны\Кабачки \n\n' \
                           f'Третий прием пищи: \n' \
                           f'Гречка ({round(((0.25*carbs)*100)/nutrition_dict.get(6)[3])} г) \n' \
                           f'Индейка ({round(((0.3*pr)*100)/nutrition_dict.get(7)[1])} г) \n' \
                           f'Перец\морковь тушеные \n\n' \
                           f'Четвертый прием: \n' \
                           f'Грецкий орех ({round(((0.3*fat)*100)/nutrition_dict.get(8)[2])} г) \n' \
                           f'Гречка ({round(((0.25*carbs)*100)/nutrition_dict.get(6)[3])} г) \n' \
                           f'Куриная грудка ({round(((0.35  *pr)*100)/nutrition_dict.get(5)[1])} г) \n\n'
    elif chosen_key1 == 2:
        dict_weight_lose[2] = f'Первый прием пищи: \n' \
                           f'Гречневая каша ({round(((0.2*carbs)*100)/nutrition_dict.get(9)[3])} г) \n' \
                           f'Бутерброд: тосты и абрикосовый джем({round(((0.1*carbs)*100)/nutrition_dict.get(17)[3])} г) \n' \
                           f'Яйца (1-2 шт) \n\n' \
                           f'Второй прием пищи: \n' \
                           f'Макароны твердых сортов ({round(((0.3*carbs)*100)/nutrition_dict.get(10)[3])} г) \n' \
                           f'Стейк из баранины ({round(((0.3*pr)*100)/nutrition_dict.get(11)[1])} г) \n' \
                           f'Салат с оливковым маслом, огурцами и помидорами \n\n' \
                           f'Третий прием пищи: \n' \
                           f'Бурый рис ({round(((0.3*carbs)*100)/nutrition_dict.get(4)[3])} г) \n' \
                           f'Куриная грудка ({round(((0.3*pr)*100)/nutrition_dict.get(5)[1])} г) \n' \
                           f'Кабачки\баклажаны\морковь тушеные \n\n' \
                           f'Четвертый прием: \n' \
                           f'Грецкие орехи ({round(((0.3*fat)*100)/nutrition_dict.get(8)[2])} г) \n' \
                            f'Бурый рис ({round(((0.1 * carbs) * 100) / nutrition_dict.get(4)[3])} г) \n' \
                            f'Пита с тунцом ({round(((0.3*pr)*100)/nutrition_dict.get(2)[1])} г) \n\n'
    elif chosen_key1 == 3:
        dict_weight_lose[3] = f'Первый прием пищи: \n' \
                            f'Овсяный блин: оливковое масло (15 г) + яйца (2 шт) ' \
                            f'+ овсяные хлопья ({round(((0.17*carbs)*100)/nutrition_dict.get(1)[3])} г) \n' \
                            f'Арахисовая паста ({round(((0.1*fat)*100)/nutrition_dict.get(12)[2])} г) \n' \
                            f'Варенье малиновое ({round(((0.1*carbs)*100)/nutrition_dict.get(13)[3])} г) \n\n' \
                            f'Второй прием пищи: \n' \
                            f'Рис ({round(((0.3*carbs)*100)/nutrition_dict.get(14)[3])} г) \n' \
                            f'Куриное филе ({round(((0.3*pr)*100)/nutrition_dict.get(5)[3])} г) \n' \
                            f'Бананы 1шт \n\n' \
                            f'Третий прием пищи: \n' \
                            f'Перловка ({round(((0.3*carbs)*100)/nutrition_dict.get(15)[3])} г) \n' \
                            f'Запеченное филе индейки ({round(((0.3*pr)*100)/nutrition_dict.get(7)[1])} г) \n' \
                            f'Брокколи и пекинская капуста с соусом \n\n' \
                            f'Четвертый прием пищи: \n' \
                            f'Рис ({round(((0.13*carbs)*100)/nutrition_dict.get(14)[3])} г) \n' \
                            f'Куриное филе ({round(((0.3*pr)*100)/nutrition_dict.get(5)[3])} г) \n\n'
    else:
        dict_weight_lose[4] = f'Первый прием пищи: \n' \
                            f'Омлет: яйца + творог + сыр  \n\n' \
                            f'Второй прием пищи: \n' \
                            f'Рис ({round(((0.3*carbs)*100)/nutrition_dict.get(14)[3])} г) \n' \
                            f'Курица({round(((0.2*pr)*100)/nutrition_dict.get(5)[3])} г) с грибами  \n' \
                            f'Цезарь \n\n' \
                            f'Третий прием пищи: \n' \
                            f'Гречка ({round(((0.3*carbs)*100)/nutrition_dict.get(6)[3])} г) \n' \
                            f'Стейк говяжий ({round(((0.3*pr)*100)/nutrition_dict.get(16)[1])} г) \n\n' \
                              f'Четвертый прием: \n' \
                              f'Салат с тунцом({round(((0.15*pr)*100)/nutrition_dict.get(2)[1])} г) и овощами\n' \
                              f'Курица({round(((0.15*pr)*100)/nutrition_dict.get(5)[1])} г) с морковью по-корейски\n' \
                              f'Рис ({round(((0.35*carbs)*100)/nutrition_dict.get(14)[3])} г) \n\n'
    plan1 = dict_weight_lose.get(chosen_key1)
    del dict_weight_lose[chosen_key1]
    chosen_key2 = random.choice(list(dict_weight_lose.keys()))
    if chosen_key2 == 1:
        dict_weight_lose[1] = f'Первый прием пищи \n' \
                           f'Овсянка ({round(((0.15*carbs)*100)/nutrition_dict.get(1)[3])} г) с сухофруктами\n' \
                           f'Бутерброд: тунец({round(((0.05*pr)*100)/nutrition_dict.get(2)[1])} г) и ' \
                           f'бездрожжевой хлеб ({round(((0.1*carbs)*100)/nutrition_dict.get(3)[3])} г) \n' \
                           f'Фрукты: банан \n' \
                           f'Арахисовая паста ({round(((0.1*fat)*100)/nutrition_dict.get(12)[2])} г) \n\n' \
                           f'Второй прием пищи: \n' \
                           f'Бурый рис ({round(((0.25*carbs)*100)/nutrition_dict.get(4)[3])} г) \n' \
                           f'Куриная грудка ({round(((0.3*pr)*100)/nutrition_dict.get(5)[1])} г) \n' \
                           f'Баклажаны\Кабачки \n\n' \
                           f'Третий прием пищи: \n' \
                           f'Гречка ({round(((0.25*carbs)*100)/nutrition_dict.get(6)[3])} г) \n' \
                           f'Индейка ({round(((0.3*pr)*100)/nutrition_dict.get(7)[1])} г) \n' \
                           f'Перец\морковь тушеные \n\n' \
                           f'Четвертый прием: \n' \
                           f'Грецкий орех ({round(((0.3*fat)*100)/nutrition_dict.get(8)[2])} г) \n' \
                           f'Гречка ({round(((0.25*carbs)*100)/nutrition_dict.get(6)[3])} г) \n' \
                           f'Куриная грудка ({round(((0.35  *pr)*100)/nutrition_dict.get(5)[1])} г) \n\n'
    elif chosen_key2 == 2:
        dict_weight_lose[2] = f'Первый прием пищи: \n' \
                           f'Гречневая каша ({round(((0.2*carbs)*100)/nutrition_dict.get(9)[3])} г) \n' \
                           f'Бутерброд: тосты и абрикосовый джем({round(((0.1*carbs)*100)/nutrition_dict.get(17)[3])} г) \n' \
                           f'Яйца (1-2 шт) \n\n' \
                           f'Второй прием пищи: \n' \
                           f'Макароны твердых сортов ({round(((0.3*carbs)*100)/nutrition_dict.get(10)[3])} г) \n' \
                           f'Стейк из баранины ({round(((0.3*pr)*100)/nutrition_dict.get(11)[1])} г) \n' \
                           f'Салат с оливковым маслом, огурцами и помидорами \n\n' \
                           f'Третий прием пищи: \n' \
                           f'Бурый рис ({round(((0.3*carbs)*100)/nutrition_dict.get(4)[3])} г) \n' \
                           f'Куриная грудка ({round(((0.3*pr)*100)/nutrition_dict.get(5)[1])} г) \n' \
                           f'Кабачки\баклажаны\морковь тушеные \n\n' \
                           f'Четвертый прием: \n' \
                           f'Грецкие орехи ({round(((0.3*fat)*100)/nutrition_dict.get(8)[2])} г) \n' \
                            f'Бурый рис ({round(((0.1 * carbs) * 100) / nutrition_dict.get(4)[3])} г) \n' \
                            f'Пита с тунцом ({round(((0.3*pr)*100)/nutrition_dict.get(2)[1])} г) \n\n'
    elif chosen_key2 == 3:
        dict_weight_lose[3] = f'Первый прием пищи: \n' \
                            f'Овсяный блин: оливковое масло (15 г) + яйца (2 шт) ' \
                            f'+ овсяные хлопья ({round(((0.17*carbs)*100)/nutrition_dict.get(1)[3])} г) \n' \
                            f'Арахисовая паста ({round(((0.1*fat)*100)/nutrition_dict.get(12)[2])} г) \n' \
                            f'Варенье малиновое ({round(((0.1*carbs)*100)/nutrition_dict.get(13)[3])} г) \n\n' \
                            f'Второй прием пищи: \n' \
                            f'Рис ({round(((0.3*carbs)*100)/nutrition_dict.get(14)[3])} г) \n' \
                            f'Куриное филе ({round(((0.3*pr)*100)/nutrition_dict.get(5)[3])} г) \n' \
                            f'Бананы 1шт \n\n' \
                            f'Третий прием пищи: \n' \
                            f'Перловка ({round(((0.3*carbs)*100)/nutrition_dict.get(15)[3])} г) \n' \
                            f'Запеченное филе индейки ({round(((0.3*pr)*100)/nutrition_dict.get(7)[1])} г) \n' \
                            f'Брокколи и пекинская капуста с соусом \n\n' \
                            f'Четвертый прием пищи: \n' \
                            f'Рис ({round(((0.13*carbs)*100)/nutrition_dict.get(14)[3])} г) \n' \
                            f'Куриное филе ({round(((0.3*pr)*100)/nutrition_dict.get(5)[3])} г) \n\n'
    else:
        dict_weight_lose[4] = f'Первый прием пищи: \n' \
                            f'Омлет: яйца + творог + сыр  \n\n' \
                            f'Второй прием пищи: \n' \
                            f'Рис ({round(((0.3*carbs)*100)/nutrition_dict.get(14)[3])} г) \n' \
                            f'Курица({round(((0.2*pr)*100)/nutrition_dict.get(5)[3])} г) с грибами  \n' \
                            f'Цезарь \n\n' \
                            f'Третий прием пищи: \n' \
                            f'Гречка ({round(((0.3*carbs)*100)/nutrition_dict.get(6)[3])} г) \n' \
                            f'Стейк говяжий ({round(((0.3*pr)*100)/nutrition_dict.get(16)[1])} г) \n\n' \
                              f'Четвертый прием: \n' \
                              f'Салат с тунцом({round(((0.15*pr)*100)/nutrition_dict.get(2)[1])} г) и овощами\n' \
                              f'Курица({round(((0.15*pr)*100)/nutrition_dict.get(5)[1])} г) с морковью по-корейски\n' \
                              f'Рис ({round(((0.35*carbs)*100)/nutrition_dict.get(14)[3])} г) \n\n'
    plan2 = dict_weight_lose.get(chosen_key2)

    return [plan1, plan2]


@log_errors
def percent_deficit_surplus(nutr_goal):
    if nutr_goal == 'Набрать вес':
        deficit_surplus = 1.2
        pr_percentage = 0.3
        carb_percent = 0.45
        text = 'Твоя норма калорий для набора веса:'
    if nutr_goal == 'Сбросить вес':
        deficit_surplus = 0.85
        pr_percentage = 0.45
        carb_percent = 0.3
        text = 'Твоя норма калорий для сброса веса:'
    if nutr_goal == 'Поддерживать форму':
        deficit_surplus = 1.0
        pr_percentage = 0.375
        carb_percent = 0.375
        text = 'Тебе нужно потреблять:'
    list = [pr_percentage, carb_percent,deficit_surplus, text]
    return list

@log_errors
def PAL_convertation(a):
    if a == 'Нет физических нагрузок':
        pal = 1.2
    if a == 'Иногда бегаю':
        pal = 1.25
    if a == 'Хожу в тренажерный зал 2-3 раза в неделю':
        pal = 1.375
    if a == 'Очень большие - хожу в зал 5 раз/неделю или моя работа требует физических нагрузок':
        pal = 1.55
    return pal


@log_errors
def stress_handler(update, context):
    context.user_data[STRESS_VITAMINS] = update.message.text

    chat_id = update.message.chat_id
    stress = update.message.text
    p, _ = Profile.objects.get_or_create(external_id=chat_id)
    Vitamin.objects.update_or_create(
        profile=p,
        defaults={
            'stress': stress,
        }
    )

    user = update.message.from_user
    logger.info("%s's stress level is: %s", user.first_name, update.message.text)
    if context.user_data[SELECTING_PROGRAM] == 'Витамины':
        reply_keyboard = [['Часто'],
                          ['Нечасто'],
                          ['Нету слабости']]
        update.message.reply_text(
            "Как часто ты испытываешь слабость?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return WEAKNESS_VITAMINS


@log_errors
def weakness_handler(update, context):
    user = update.message.from_user

    chat_id = update.message.chat_id
    weakness = update.message.text
    p, _ = Profile.objects.get_or_create(external_id=chat_id)
    Vitamin.objects.update_or_create(
        profile=p,
        defaults={
            'weakness': weakness,
        }
    )

    logger.info("%s's weakness level is: %s", user.first_name, update.message.text)
    context.user_data[WEAKNESS_VITAMINS] = update.message.text
    if context.user_data[SELECTING_PROGRAM] == 'Витамины':
        reply_keyboard = [['Да'],
                          ['Нет']]
        update.message.reply_text(
            "В твоем городе часто светит солнце?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return SUN_OFTEN


@log_errors
def sun_handler(update, context):
    context.user_data[SUN_OFTEN] = update.message.text

    chat_id = update.message.chat_id
    sun_frequency = update.message.text
    p, _ = Profile.objects.get_or_create(external_id=chat_id)
    Vitamin.objects.update_or_create(
        profile=p,
        defaults={
            'sun_frequency': sun_frequency,
        }
    )

    user = update.message.from_user
    logger.info("if sun occurs often in %s's city: %s", user.first_name, update.message.text)
    reply_text_program = vitamin_program(context)
    update.message.reply_text(reply_text_program, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN,
                              disable_web_page_preview=False)
    return ConversationHandler.END

@log_errors
def vitamin_program(context):
    if context.user_data[GENDER] == 'Женщина':
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Programma-vitaminov-01-20) ' \
                     f'витаминов уже сформирована!\n'
    else:
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Programma-vitaminov-01-20-2) ' \
                     f'витаминов уже сформирована!\n'
    return reply_text

@log_errors
def goal_handler(update, context):
    context.user_data[GOAL] = update.message.text
    if context.user_data[SELECTING_PROGRAM] == 'Тренировки':
        chat_id = update.message.chat_id
        goal = update.message.text
        p, _ = Profile.objects.get_or_create(external_id=chat_id)
        Training.objects.update_or_create(
            profile=p,
            defaults={
                'train_goal': goal,
            }
        )

    elif context.user_data[SELECTING_PROGRAM] == 'Питание':
        chat_id = update.message.chat_id
        goal = update.message.text
        p, _ = Profile.objects.get_or_create(external_id=chat_id)
        Nutrition.objects.update_or_create(
            profile=p,
            defaults={
                'nutrition_goal': goal,
            }
        )

    user = update.message.from_user
    logger.info("%s's goal is: %s", user.first_name, update.message.text)
    if context.user_data[GOAL] == 'Набрать вес':
        reply_keyboard = [['0-3','3-7'],
                          ['7-15','> 15']]
        update.message.reply_text(
            "Сколько килограмм примерно ты хочешь набрать в ближайший месяц?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return GAIN_LOSE_KEEP

    elif context.user_data[GOAL] == 'Сбросить вес':
        reply_keyboard = [['0-3','3-7'],
                          ['7-15','> 15']]
        update.message.reply_text(
            "Сколько килограмм примерно ты хочешь сбросить в ближайший месяц?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return GAIN_LOSE_KEEP


@log_errors
def keep_handler(update, context):
    context.user_data[GOAL] = 'Поддерживать форму'
    user = update.message.from_user
    logger.info("%s goal is: %s", user.first_name, update.message.text)
    if context.user_data[SELECTING_PROGRAM] == 'Тренировки':
        chat_id = update.message.chat_id
        goal = update.message.text
        p, _ = Profile.objects.get_or_create(external_id=chat_id)
        Training.objects.update_or_create(
            profile=p,
            defaults={
                'train_goal': goal,
                'how_much': '0',
            }
        )

        reply_keyboard = [['Новичок'],
                          ['Опытный'],
                          ['Профи']]
        update.message.reply_text(
            "Каков твой уровень как спортсмена? \n\n"
            "Новичок - не имею/имею очень малое представление о технике выполнения большинства упражнений \n\n"
            "Опытный - часто хожу в тренажерный зал и имею представление о технике выполнения большинства упражнений \n\n"
            "Профи - я тренер или профессиональный спортсмен",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return SPORT_LVL
    elif context.user_data[SELECTING_PROGRAM] == 'Питание':
        chat_id = update.message.chat_id
        goal = update.message.text
        p, _ = Profile.objects.get_or_create(external_id=chat_id)
        Nutrition.objects.update_or_create(
            profile=p,
            defaults={
                'nutrition_goal': goal,
                'how_much': '0',
            }
        )

        reply_keyboard = [['Да'],
                          ['Нет']]
        update.message.reply_text(
            "Ты ешь мясо?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return MEAT

@log_errors
def gain_lose_handler(update, context):
    if context.user_data[GOAL] == 'Набрать вес':
        context.user_data[GAIN_LOSE_KEEP] = update.message.text
        user = update.message.from_user
        logger.info("%s wants to gain: %s kilos", user.first_name, update.message.text)
        if context.user_data[SELECTING_PROGRAM] == 'Тренировки':
            chat_id = update.message.chat_id
            how_much = update.message.text
            p, _ = Profile.objects.get_or_create(external_id=chat_id)
            Training.objects.update_or_create(
                profile=p,
                defaults={
                    'how_much': how_much,
                }
            )
            reply_keyboard = [['Новичок'],
                              ['Опытный'],
                              ['Профи']]
            update.message.reply_text(
                "Каков твой уровень как спортсмена? \n\n"
                "Новичок - не имею/имею очень малое представление о технике выполнения большинства упражнений \n\n"
                "Опытный - часто хожу в тренажерный зал и имею представление о технике выполнения большинства упражнений \n\n"
                "Профи - я тренер или профессиональный спортсмен",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return SPORT_LVL

        elif context.user_data[SELECTING_PROGRAM] == 'Питание':
            chat_id = update.message.chat_id
            how_much = update.message.text
            p, _ = Profile.objects.get_or_create(external_id=chat_id)
            Nutrition.objects.update_or_create(
                profile=p,
                defaults={
                    'how_much': how_much,
                }
            )

            reply_keyboard = [['Да'],
                              ['Нет']]
            update.message.reply_text(
                "Ты ешь мясо?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return MEAT

    elif context.user_data[GOAL] == 'Сбросить вес':
        context.user_data[GAIN_LOSE_KEEP] = update.message.text
        user = update.message.from_user
        logger.info("%s wants to lose: %s kilos", user.first_name, update.message.text)
        if context.user_data[SELECTING_PROGRAM] == 'Тренировки':
            chat_id = update.message.chat_id
            how_much = update.message.text
            p, _ = Profile.objects.get_or_create(external_id=chat_id)
            Training.objects.update_or_create(
                profile=p,
                defaults={
                    'how_much': how_much,
                }
            )
            reply_keyboard = [['Новичок'],
                              ['Опытный'],
                              ['Профи']]
            update.message.reply_text(
                "Каков твой уровень как спортсмена? \n\n"
                "Новичок - не имею/имею очень малое представление о технике выполнения большинства упражнений \n\n"
                "Опытный - часто хожу в тренажерный зал и имею представление о технике выполнения большинства упражнений \n\n"
                "Профи - я тренер или профессиональный спортсмен",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return SPORT_LVL

        elif context.user_data[SELECTING_PROGRAM] == 'Питание':
            chat_id = update.message.chat_id
            how_much = update.message.text
            p, _ = Profile.objects.get_or_create(external_id=chat_id)
            Nutrition.objects.update_or_create(
                profile=p,
                defaults={
                    'how_much': how_much,
                }
            )

            reply_keyboard = [['Да'],
                              ['Нет']]
            update.message.reply_text(
                "Ты ешь мясо?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return MEAT


@log_errors
def sport_lvl_handler(update, context):
    context.user_data[SPORT_LVL] = update.message.text

    chat_id = update.message.chat_id
    sport_lvl = update.message.text
    p, _ = Profile.objects.get_or_create(external_id=chat_id)
    Training.objects.update_or_create(
        profile=p,
        defaults={
            'sport_lvl': sport_lvl,
        }
    )

    user = update.message.from_user
    logger.info("%s level is: %s ", user.first_name, update.message.text)
    reply_text = train_advice(update, context)
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN,
                              disable_web_page_preview = True)
    client_id = 'D39B135760893C3E1EF5F5FBA1C006CC744BE79959883217490829F70D1B9D59'
    h = requests.post('https://money.yandex.ru/api/instance-id',  data={'client_id': client_id})
    req = json.loads(h.text)
   # print(req)
    instance_id = req['instance_id']
    account_number = '4100110996845190'
    amount_due = 1
    k = requests.post('https://money.yandex.ru/api/request-external-payment',  data={'pattern_id': 'p2p','instance_id': instance_id,'to': account_number,'amount_due': amount_due})
    rek = json.loads(k.text)
   # print(rek)
    request_id = rek['request_id']
    #при успешной оплате человека переносит на сервер, чтобы обработать успешную или неудачную оплату
    key_succ = str(uuid.uuid4())
    key_fail = str(uuid.uuid4())
    payment = Payments(
        profile = Profile.objects.get(external_id = update.message.chat_id),
        key_succ = key_succ, 
        is_activated = False,
        product_id = 1,
    )
    payment.save()
    process_payment = requests.post('https://money.yandex.ru/api/process-external-payment', data={'request_id': request_id,'instance_id': instance_id, 'ext_auth_success_uri': 'http://51.38.83.214:8081/?key='+key_succ,'ext_auth_fail_uri': 'http://51.38.83.214:8081/?key='+key_fail})
    #сделать на питоне веб-сервер, который будет обрабатывать все запросы (с правильными портами)
    process_payment_json = json.loads(process_payment.text)
   # print(process_payment_json)
    acs_params = process_payment_json['acs_params']
    acs_url = str(process_payment_json['acs_uri']) + '?'+ 'cps_context_id=' + acs_params['cps_context_id'] + '&paymentType=' + acs_params['paymentType'] 
   # print(acs_params)
   # print(acs_url)

    #Кнопка оплаты
    keyboard = [[InlineKeyboardButton(text = "Получить программу", url=acs_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f'Для получения подробной программы перейди по ссылке'
    update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN,
                                  disable_web_page_preview=True)
    

    return ConversationHandler.END


@log_errors
def train_program(update, context):
    if (context.user_data[GENDER]=='Женщина'
            and context.user_data[SPORT_LVL] == 'Новичок'):
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20) ' \
                     f'уже сформирована!\n'
    elif (context.user_data[GENDER]=='Женщина' and (context.user_data[SPORT_LVL] == 'Опытный' or
                                                    context.user_data[SPORT_LVL] == 'Профи')):
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20-2)' \
                     f' уже сформирована!\n'
    else:
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20-3)' \
                     f' уже сформирована!\n'
    return reply_text


@log_errors
def train_advice(update, context):
    if context.user_data[GENDER] == 'Женщина':
        if context.user_data[GOAL] == 'Сбросить вес':
            reply_text = f'Если твоя цель - похудение, то здесь нужно в первую очередь обратить свое внимание на ' \
                         f'питание, чтобы сбросить вес качественно и без пыток собственного тела в зале ' \
                         f'продолжительными кардио-тренировками или тяжелыми силовыми.\n' \
                         f'Но, все же, тренировки могут помочь в похудении при грамотном подходе.\n\n' \
                         f'Любые тренировки в тренажерном зале приводят к расходу калорий,следовательно, чем бы ты ни ' \
                         f'занималась, это будет так или иначе приводить к снижению массы тела, но силовые тренировки ' \
                         f'с отягощением расходуют очень много калорий, и часто проводить ' \
                         f'их не получится, так как они нагружают нервную систему и выматывают, если заниматься так слишком часто.\n' \
                         f'А длительные нагрузки в среднем темпе (такие как бег, работа с легкими весами в большом количестве повторов) ' \
                         f'не выматывают организм настолько сильно, поэтому при сбросе веса можно отдать приоритет именно' \
                         f' таким нагрузкам.\nТаким образом, нужно стремиться к ' \
                         f'тому, чтобы умеренно дозировать силовые упражнения и не забывать про нагрузки в среднем темпе.\n\n' \
                         f'Вот на что стоит обратить внимание:\n' \
                         f'1. *Формат тренировок*: нужно решить, сколько свободного времени ты ' \
                         f'готова потратить на то, чтобы уделять его своим тренировкам и, исходя из того, ' \
                         f'какие у тебя цели и уровень подготовки, подобрать ' \
                         f'себе оптимальный формат тренировок - тренировки на все тело, двухдневный, ' \
                         f'трехдневный или же четырехдневный сплит.\n\n' \
                         f'2. Тебе нужно подобрать *основное упражнение* для каждой группы мышц - оно будет являться базовым, ' \
                         f'и к его выполнению стоит подходить в первую очередь.\nНужно выполнять в силовом стиле с максимальной ' \
                         f'нагрузкой, которая позволить технично выполнить 4-8 повторений.\nВ среднем, на это упражнение ' \
                         f'тратится 3 подхода, но , конечно, нужно ориентироваться на свое самочувствие: ' \
                         f'если чувствуешь, что можешь сделать больше и энергии хоть отбавляй - можно сделать 4 подхода, ' \
                         f'если чувствуешь слабость и сильно устаешь уже после второго подхода - можешь остановиться и на этом.\n' \
                         f'Например, для квадрицепса это могут быть приседания со штангой.\n\n' \
                         f'3. После главного упражнения стоит подобрать *дополнительное упражнение* ' \
                         f'- оно также должно являться базовым и к нему ты будешь подходить немного ' \
                         f'уставшей после главного. Рабочий вес в этом упражнении снижается и должен позволить ' \
                         f'тебе выполнить 6-12 техничных повторений. Обычно 3-4 подходов достаточно.\nДля ' \
                         f'квадрицепса это может быть жим платформы ногами лежа.\n\n' \
                         f'4. Последнее упражнение является *вспомогательным*, чтобы "добить" ' \
                         f'целевую группу мышц - оно должно быть изолирующим и односуставным. ' \
                         f'Также, оно нацелено на множество повторов и в этом случае вес необходимо подобрать ' \
                         f'для 12-20 качественных повторов.\n' \
                         f'Для квадрицепса, например, это будут разгибания ног в тренажере.\n\n' \
                         f'Источники: \n\n' \
                         f'[статья FitNavigator](https://fitnavigator.ru/trenirovki/programmy/dlja-pohudenija-dlja-devushek-v-trenazhernom-zale.html) \n' \
                         f'[Пост Димы Путылина](https://www.instagram.com/p/B5-N5wzpnoR/) \n' \
                         f'[статья SportWiki](http://sportwiki.to/%D0%A1%D0%BF%D0%BB%D0%B8%D1%82-%D1%82%D1%80%D0%B5%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0) \n'
        else:
            reply_text = f'Если твоя цель - набор массы или поддержание формы, то в ' \
                         f'своих тренировках нужно отдать приоритет силовым упражнениям, ' \
                         f'а в питании сделать профицит - это поспособствует хорошему восстановлению ' \
                         f'и компенсирует нагрузки на тренировках.\n\n' \
                         f'Вот на что стоит обратить внимание:\n' \
                         f'1. *Формат тренировок*: нужно решить, сколько свободного времени ты ' \
                         f'готова потратить на то, чтобы уделять его своим тренировкам и, исходя из того, ' \
                         f'какие у тебя цели и уровень подготовки, подобрать ' \
                         f'себе оптимальный формат тренировок - тренировки на все тело, двухдневный, ' \
                         f'трехдневный или же четырехдневный сплит.\n\n' \
                         f'2. Тебе нужно подобрать *основное упражнение* для каждой группы мышц - оно будет являться базовым, ' \
                         f'и к его выполнению стоит подходить в первую очередь.\nНужно выполнять в силовом стиле с максимальной ' \
                         f'нагрузкой, которая позволить технично выполнить 4-8 повторений.\nВ среднем, на это упражнение ' \
                         f'тратится 3 подхода, но , конечно, нужно ориентироваться на свое самочувствие: ' \
                         f'если чувствуешь, что можешь сделать больше и энергии хоть отбавляй - можно сделать 4 подхода, ' \
                         f'если чувствуешь слабость и сильно устаешь уже после второго подхода - можешь остановиться и на этом.\n' \
                         f'Например, для квадрицепса это могут быть приседания со штангой.\n\n' \
                         f'3. После главного упражнения стоит подобрать *дополнительное упражнение* ' \
                         f'- оно также должно являться базовым и к нему ты будешь подходить немного ' \
                         f'уставшей после главного. Рабочий вес в этом упражнении снижается и должен позволить ' \
                         f'тебе выполнить 6-12 техничных повторений. Обычно 3-4 подходов достаточно.\nДля ' \
                         f'квадрицепса это может быть жим платформы ногами лежа.\n\n' \
                         f'4. Последнее упражнение является *вспомогательным*, чтобы "добить" ' \
                         f'целевую группу мышц - оно должно быть изолирующим и односуставным. ' \
                         f'Также, оно нацелено на множество повторов и в этом случае вес необходимо подобрать ' \
                         f'для 12-20 качественных повторов.\n' \
                         f'Для квадрицепса, например, это будут разгибания ног в тренажере.\n\n' \
                         f'Источники: \n\n' \
                         f'[Пост Путылина](https://www.instagram.com/p/B5-N5wzpnoR/)'
    else:
        if context.user_data[GOAL] == 'Сбросить вес':
            reply_text = f'Если твоя цель - похудение, то здесь нужно в первую очередь обратить ' \
                         f'свое внимание на питание, чтобы сбросить вес качественно и без пыток ' \
                         f'собственного тела в зале продолжительными кардио-тренировками или тяжелыми силовыми.\n' \
                         f'Но, все же, тренировки могут помочь в похудении при грамотном подходе.\n\n' \
                         f'Для похудения нужно сначала привести свою сердечно-сосудистую систему ' \
                         f'в боеспособное состояние. Если ты сразу встанешь на дорожку на 30 минут, ' \
                         f'это может перегрузить сердце.\n' \
                         f'Кардио - это первый элемент тренировки, который можно ' \
                         f'начать с 5-10 минут бега. Если это эллипсоид ' \
                         f'или велотренажер - можно работать и больше уже в первые тренировки. ' \
                         f'Очень важно при беге дозировать нагрузку.\n' \
                         f'После кардио идет основная часть ' \
                         f'тренировки, состоящая из силовых упражнений. ' \
                         f'Здесь твоя задача - потратить максимум энергии.\n\n' \
                         f'Вот на что стоит обратить внимание:\n' \
                         f'1. *Формат тренировок*: нужно решить, сколько свободного времени ты ' \
                         f'готов потратить на то, чтобы уделять его своим тренировкам и, исходя из того, ' \
                         f'какие у тебя цели и уровень подготовки, подобрать ' \
                         f'себе оптимальный формат тренировок - тренировки на все тело, двухдневный, ' \
                         f'трехдневный или же четырехдневный сплит.\n\n' \
                         f'2. Тебе нужно подобрать *основное упражнение* для каждой группы ' \
                         f'мышц - оно будет являться базовым, ' \
                         f'и к его выполнению стоит подходить в первую очередь.\nНужно ' \
                         f'выполнять в силовом стиле с максимальной ' \
                         f'нагрузкой, которая позволить технично выполнить 4-8 ' \
                         f'повторений.\nВ среднем, на это упражнение ' \
                         f'тратится 3 подхода, но , конечно, нужно ориентироваться на свое самочувствие: ' \
                         f'если чувствуешь, что можешь сделать больше и энергии хоть ' \
                         f'отбавляй - можно сделать 4 подхода, ' \
                         f'если чувствуешь слабость и сильно устаешь уже после второго ' \
                         f'подхода - можешь остановиться и на этом.\n' \
                         f'Например, для квадрицепса это могут быть приседания со штангой.\n\n' \
                         f'3. После главного упражнения стоит подобрать *дополнительное упражнение* ' \
                         f'- оно также должно являться базовым и к нему ты будешь подходить немного ' \
                         f'уставшим после главного. Рабочий вес в этом упражнении снижается и должен позволить ' \
                         f'тебе выполнить 6-12 техничных повторений. Обычно 3-4 подходов достаточно.\nДля ' \
                         f'квадрицепса это может быть жим платформы ногами лежа.\n\n' \
                         f'4. Последнее упражнение является *вспомогательным*, чтобы "добить" ' \
                         f'целевую группу мышц - оно должно быть изолирующим и односуставным. ' \
                         f'Также, оно нацелено на множество повторов и вес необходимо подобрать ' \
                         f'для 12-20 качественных повторов.\n' \
                         f'Для квадрицепса, например, это будут разгибания ног в тренажере.\n\n' \
                         f'Источники: \n\n' \
                         f'[Пост Путылина](https://www.instagram.com/p/B5-N5wzpnoR/)'
        else:
            reply_text = f'Если твоя цель - набор массы или поддержание формы, то здесь ' \
                         f'стоит сделать акцент на силовых тренировках и профиците ' \
                         f'калорий в твоей диете (это не менее важно, чем сами тренировки при наборе массы).\n\n' \
                         f'Вот на что стоит обратить внимание:\n' \
                         f'1. *Формат тренировок*: нужно решить, сколько свободного времени ты ' \
                         f'готов потратить на то, чтобы уделять его своим тренировкам и, исходя из того, ' \
                         f'какие у тебя цели и уровень подготовки, подобрать ' \
                         f'себе оптимальный формат тренировок - тренировки на все тело, двухдневный, ' \
                         f'трехдневный или же четырехдневный сплит.\n\n' \
                         f'2. Тебе нужно подобрать *основное упражнение* для каждой группы ' \
                         f'мышц - оно будет являться базовым, ' \
                         f'и к его выполнению стоит подходить в первую очередь.\nНужно ' \
                         f'выполнять в силовом стиле с максимальной ' \
                         f'нагрузкой, которая позволить технично выполнить 4-8 ' \
                         f'повторений.\nВ среднем, на это упражнение ' \
                         f'тратится 3 подхода, но , конечно, нужно ориентироваться на свое самочувствие: ' \
                         f'если чувствуешь, что можешь сделать больше и энергии хоть ' \
                         f'отбавляй - можно сделать 4 подхода, ' \
                         f'если чувствуешь слабость и сильно устаешь уже после второго ' \
                         f'подхода - можешь остановиться и на этом.\n' \
                         f'Например, для квадрицепса это могут быть приседания со штангой.\n\n' \
                         f'3. После главного упражнения стоит подобрать *дополнительное упражнение* ' \
                         f'- оно также должно являться базовым и к нему ты будешь подходить немного ' \
                         f'уставшим после главного. Рабочий вес в этом упражнении снижается и должен позволить ' \
                         f'тебе выполнить 6-12 техничных повторений. Обычно 3-4 подходов достаточно.\nДля ' \
                         f'квадрицепса это может быть жим платформы ногами лежа.\n\n' \
                         f'4. Последнее упражнение является *вспомогательным*, чтобы "добить" ' \
                         f'целевую группу мышц - оно должно быть изолирующим и односуставным. ' \
                         f'Также, оно нацелено на множество повторов и в этом случае вес необходимо подобрать ' \
                         f'для 12-20 качественных повторов.\n' \
                         f'Для квадрицепса, например, это будут разгибания ног в тренажере.\n\n' \
                         f'Источники: \n\n' \
                         f'[Пост Путылина](https://www.instagram.com/p/B5-N5wzpnoR/) \n'

    return reply_text



@log_errors
def meat_handler(update, context):
    context.user_data[MEAT] = update.message.text

    chat_id = update.message.chat_id
    if_meat = update.message.text
    p, _ = Profile.objects.get_or_create(external_id=chat_id)
    Nutrition.objects.update_or_create(
        profile=p,
        defaults={
            'if_meat': if_meat,
        }
    )

    user = update.message.from_user
    logger.info("Does %s eats meat?: %s ", user.first_name, update.message.text)

    update.message.reply_text(
        "Укажи свой рост в сантиметрах",
        reply_markup= ReplyKeyboardRemove())
    return HEIGHT


@log_errors
def height_handler(update,context):
    context.user_data[HEIGHT] = update.message.text

    chat_id = update.message.chat_id
    height = update.message.text
    p, _ = Profile.objects.get_or_create(external_id=chat_id)
    Nutrition.objects.update_or_create(
        profile=p,
        defaults={
            'height': height,
        }
    )

    user = update.message.from_user
    logger.info("%s's height: %s ", user.first_name, update.message.text)
    reply_keyboard = [['Очень большие - хожу в зал 5 раз/неделю или моя работа требует физических нагрузок'],
                      ['Хожу в тренажерный зал 2-3 раза в неделю'],
                      ['Иногда бегаю'],
                      ['Нет физических нагрузок']]
    update.message.reply_text(
        "Отлично! Какие у тебя есть физические нагрузки?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return PHYS_LOADS_NUTR


@log_errors
def cancel(update, context):
    cry = emojize(":cry:", use_aliases=True)
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Пока! Надеюсь, когда-нибудь я получу возможность составить тебе программу '+cry,
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        # 1 -- правильное подключение
        request = Request(
            connect_timeout=3000, #2
            read_timeout=3000, #2.5
        )
        config = load_config()
        bot = Bot(
            request=request,
            token=config.TOKEN,
            base_url=config.PROXY_URL,
        )
        print(bot.get_me())

        # 2 -- обработчики
        updater = Updater(
            bot=bot,
            use_context=True,
        )
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={
                NAME: [MessageHandler(Filters.text, name_handler, pass_user_data=True)],

                SELECTING_PROGRAM: [
                    MessageHandler(Filters.regex('^(Тренировки)|(Питание)|(Витамины)$'), program_handler,
                                   pass_user_data=True)],

                GENDER: [MessageHandler(Filters.regex('^(Мужчина)|(Женщина)$'), gender_handler, pass_user_data=True)],

                AGE: [MessageHandler(Filters.text, age_handler, pass_user_data=True)],

                WEIGHT: [MessageHandler(Filters.text, weight_handler, pass_user_data=True)],

                PHYS_LOADS_VITAMINS: [MessageHandler(Filters.regex('^(Очень большие - хожу в зал 5 раз/неделю или '
                                                                   'моя работа требует физических нагрузок)|'
                                                                   '(Хожу в тренажерный зал 2-3 раза в неделю)|'
                                                                   '(Иногда бегаю)|'
                                                                   '(Нет физических нагрузок)$'), phys_loads_handler,
                                                     pass_user_data=True)],

                STRESS_VITAMINS: [MessageHandler(Filters.regex('^(Часто)|(Нечасто)|(Нету стресса)$'), stress_handler,
                                                 pass_user_data=True)],

                WEAKNESS_VITAMINS: [
                    MessageHandler(Filters.regex('^(Часто)|(Нечасто)|(Нету слабости)$'), weakness_handler,
                                   pass_user_data=True)],

                SUN_OFTEN: [MessageHandler(Filters.regex('^(Да)|(Нет)$'), sun_handler, pass_user_data=True)],

                GOAL: [
                    MessageHandler(Filters.regex('^(Набрать вес)|(Сбросить вес)$'), goal_handler, pass_user_data=True),
                    MessageHandler(Filters.regex('^(Поддерживать форму)$'), keep_handler, pass_user_data=True)],

                GAIN_LOSE_KEEP: [MessageHandler(Filters.regex('^(0-3)|(3-7)|(7-15)|(> 15)$'), gain_lose_handler,
                                                pass_user_data=True)],

                SPORT_LVL: [MessageHandler(Filters.regex('^(Новичок)|(Опытный)|(Профи)$'), sport_lvl_handler,
                                           pass_user_data=True)],

                MEAT: [MessageHandler(Filters.regex('^(Да)|(Нет)$'), meat_handler, pass_user_data=True)],

                HEIGHT: [MessageHandler(Filters.text, height_handler, pass_user_data=True)],

                PHYS_LOADS_NUTR: [MessageHandler(Filters.regex('^(Очень большие - хожу в зал 5 раз/неделю или '
                                                               'моя работа требует физических нагрузок)|'
                                                               '(Хожу в тренажерный зал 2-3 раза в неделю)|'
                                                               '(Иногда бегаю)|'
                                                               '(Нет физических нагрузок)$'), phys_loads_handler,
                                                 pass_user_data=True)]

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        updater.dispatcher.add_handler(conv_handler)

        # 3 -- запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    Command.handle()

