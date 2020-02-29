from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import ParseMode
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, Update
from telegram.utils.request import Request
from emoji import emojize
import logging
import random
from projectb.settings import load_config
import http.server
import socketserver
from http import HTTPStatus
import urllib.parse as urlparse
from urllib.parse import parse_qs
from ugc.models import Profile, Vitamin, Training, Nutrition, Payments
from urllib import request, parse
from django.http import HttpResponse, HttpResponseRedirect
import django.http.request


class Handler(http.server.SimpleHTTPRequestHandler):
        
    def do_GET(self):
        #self.send_response(HTTPStatus.OK)
        #self.end_headers()
        recieved_url = "{}".format(self.path)
        recieved_url = recieved_url[2:]
        data = recieved_url.split('&')
        print(data)
        key = data[0].split('=')[1]
    
        
        
        #payment = Payments.objects.get(key_succ = key)
        #self.wfile.write(payment.key_succ.encode('utf-8'))
        #проверяем существование неактивированного продукта по ключу
        if Payments.objects.filter(key_succ=key, is_activated = False).exists():
            #self.wfile.write(b'OK')
            
            #активируем продукт и отправляем ответ покупателю
            payment = Payments.objects.get(key_succ = key)
            payment.is_activated = True
            payment.save()
            if payment.product_id == 1:
                #code1
                training = Training.objects.get(profile = payment.profile)
                profile = payment.profile
                reply_text_program = train_program(profile.gender, training.sport_lvl)
                ddict = {'chat_id': profile.external_id, 'text': reply_text_program, 'parse_mode': 'Markdown'}
                data = parse.urlencode(ddict).encode()
                req =  request.Request("https://api.telegram.org/bot998191109:AAESxqYpeF77Usa3cpsiZjmXVL2p2tZWnbU/sendMessage", data=data) # this will make the method "POST"
                resp = request.urlopen(req)
                #user redirect
                self.send_response(302)
                self.send_header('Location', 'https://tmgo.me/fit_easy_bot')
                self.end_headers()
            if payment.product_id == 2:
                #code2
                global pr
                global carbs
                global fat
                nutrition = Nutrition.objects.get(profile = payment.profile)
                profile = payment.profile
                if profile.gender == "Мужчина":
                    s = 5
                    m = float(profile.weight)
                    h = float(nutrition.height)
                    a = float(profile.age)
                    # standart BMR calculation
                    bmr = 10 * m + 6.25 * h - 5 * a + s
                    bmr_in_motion = bmr * PAL_convertation(nutrition.phys_loads)
                    list_result = percent_deficit_surplus(nutrition.nutrition_goal)
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
                    m = float(profile.weight)
                    h = float(nutrition.height)
                    a = float(profile.age)
                    bmr = 10 * m + 6.25 * h - 5 * a + s
                    bmr_in_motion = bmr * PAL_convertation(nutrition.phys_loads)
                    list_result = percent_deficit_surplus(nutrition.nutrition_goal)
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

                plans = nutrition_1()
                text_plans = f'*ВНИМАНИЕ! Продукты взвешиваются в СУХОМ(неприготовленном) виде* \n\n' \
                         f'*Твоя программа питания на первый день:* \n\n' \
                         f'{plans[0]}' \
                         f'*Твоя программа питания на второй день:* \n\n' \
                         f'{plans[1]}'
                ddict = {'chat_id': profile.external_id, 'text': text_plans, 'parse_mode': 'Markdown'}
                data = parse.urlencode(ddict).encode()
                print('HELLO_1')
                req =  request.Request("https://api.telegram.org/bot998191109:AAESxqYpeF77Usa3cpsiZjmXVL2p2tZWnbU/sendMessage", data=data) # this will make the method "POST"
                resp = request.urlopen(req)
                #user redirect
                print('HELLO_2')
                self.send_response(302)
                self.send_header('Location', 'https://tmgo.me/fit_easy_bot')
                self.end_headers()
                #вызвать view
                #success(req)
                #return request.urlopen('')
                
        else:
            text_plans = f'Упс! С оплатой что-то пошло не так.'
            ddict = {'chat_id': profile.external_id, 'text': text_plans, 'parse_mode': 'Markdown'}
            data = parse.urlencode(ddict).encode()
            req =  request.Request("https://api.telegram.org/bot998191109:AAESxqYpeF77Usa3cpsiZjmXVL2p2tZWnbU/sendMessage", data=data) # this will make the method "POST"
            resp = request.urlopen(req)
            self.send_response(302)
            self.send_header('Location', 'https://tmgo.me/fit_easy_bot')
            self.end_headers()

            
            
def train_program(gender, sport_lvl):
    if (gender=='Женщина'
            and sport_lvl == 'Новичок'):
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20) ' \
                     f'уже сформирована!\n'
    elif (gender=='Женщина' and (sport_lvl == 'Опытный' or sport_lvl == 'Профи')):
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20-2)' \
                     f' уже сформирована!\n'
    else:
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20-3)' \
                     f' уже сформирована!\n'
    return reply_text

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
           
def train_program(gender, sport_lvl):
    if (gender=='Женщина'
            and sport_lvl == 'Новичок'):
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20) ' \
                     f'уже сформирована!\n'
    elif (gender=='Женщина' and (sport_lvl == 'Опытный' or sport_lvl == 'Профи')):
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20-2)' \
                     f' уже сформирована!\n'
    else:
        reply_text = f'Твоя индивидуальная [программа](https://telegra.ph/Tvoya-programma-trenirovok-01-20-3)' \
                     f' уже сформирована!\n'
    return reply_text

      
def nutrition_1():
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


httpd = socketserver.TCPServer(('', 8081), Handler)
httpd.serve_forever()



