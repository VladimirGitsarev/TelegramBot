import telebot
import requests
import random
from bs4 import BeautifulSoup as BS
from telebot import types
from translate import Translator
from google_images_download import google_images_download

appid = '6c8c44f35a227775cbb6c9fa35c67d2c'
bot = telebot.TeleBot('1038924278:AAHoYHOuNnzlEEh3EH8wjc0Alw9GDXJ2pWI')
        
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    ask = ['привет', 'прив', 'бот', 'чел', 'hey', 'hi', 'hello', 'bot', 'chel', 'нет', 'чикибряк']
    if message.text.lower() in ask:
        markup = types.InlineKeyboardMarkup()
        weatherBtn = types.InlineKeyboardButton(text='Узнать погоду', callback_data='weather')
        translateBtn = types.InlineKeyboardButton(text='Перевести слово', callback_data='translate')
        songBtn = types.InlineKeyboardButton(text='Текст песни', callback_data='song')
        jokeBtn = types.InlineKeyboardButton(text='Анек', callback_data='joke')
        markup.add(weatherBtn)
        markup.add(translateBtn)
        markup.add(songBtn)
        markup.add(jokeBtn)
        bot.send_message(message.from_user.id, "Чем я могу тебе помочь?", reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю...")

def getWeather(message):
    translatorToEng = Translator(to_lang="en", from_lang="ru")
    translation = translatorToEng.translate(message.text)
    if message.text.startswith('/'):
        bot.register_next_step_handler(message, get_text_messages)
    else:
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                 params={'q': translation, 'type': 'like', 'units': 'metric', 'APPID': appid})
            data = res.json()
            temp = data['list'][0]['main']['temp']
            wind = data['list'][0]['wind']['speed']
            humidity = data['list'][0]['main']['humidity']
            conditions = data['list'][0]['weather'][0]['description']
            translatorToRus = Translator(to_lang='ru')
            translationRus = translatorToRus.translate(conditions)
            search = translation + " city"
            response = google_images_download.googleimagesdownload()   #class instantiation
            arguments = {"keywords":search,"limit":3,"print_urls":True, "no_download":True}   #creating list of arguments
            paths = response.download(arguments)
            bot.send_photo(message.from_user.id, photo=random.choice(paths[0][search]), caption='Температура: ' + str(temp) +  ' °C' + 
                                                                                            '\nСкорость ветра: ' + str(wind) + ' м/c' +
                                                                                            '\nВлажность: ' + str(humidity) + '%' +
                                                                                            '\n' + translationRus.title())
            bot.send_location(message.from_user.id, data['list'][0]['coord']['lat'], data['list'][0]['coord']['lon'])
        except:
            bot.send_message(message.from_user.id, 'Не могу найти город') 
        #markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        #yesBtn = types.InlineKeyboardButton(text="Да", callback_data='weather')
        #noBtn = types.InlineKeyboardButton(text="Нет")
        #markup.row(yesBtn, noBtn)
        markup = types.InlineKeyboardMarkup()
        weatherBtn = types.InlineKeyboardButton(text='Продолжить', callback_data='weather')
        markup.add(weatherBtn)
        bot.send_message(message.from_user.id, "Продолжить?", reply_markup=markup)
        
       
def getTranslation(message):
    if message.text.startswith('/'):
        bot.register_next_step_handler(message, get_text_messages)
    else:
        try:
            translatorToEng = Translator(to_lang="ru", from_lang="en")
            translation = translatorToEng.translate(message.text)
            arguments = {"keywords":translation,"limit":3,"print_urls":True, "no_download":True}   #creating list of arguments
            response = google_images_download.googleimagesdownload()
            paths = response.download(arguments)
            bot.send_photo(message.from_user.id, photo=random.choice(paths[0][translation]), caption=message.text.title() + " - " + translation)
        except:
            bot.send_message(message.from_user.id, "Что-то пошло не так...\nПопробуй еще раз")
        markup = types.InlineKeyboardMarkup()
        weatherBtn = types.InlineKeyboardButton(text='Продолжить', callback_data='translate')
        markup.add(weatherBtn)
        bot.send_message(message.from_user.id, "Продолжить?", reply_markup=markup)

def getSongText(message):
    urlAdd = message.text.lower().capitalize().replace(' - ', '-').replace(', ', '-').replace(',', '-').replace(' & ', '-and-').replace('&', '-and-').replace(' ', '-') + '-lyrics'
    req = requests.get('https://genius.com/' + urlAdd)
    html = BS(req.content, 'html.parser')
    song = ''
    for el in html.select('.lyrics'):
        song += el.text
    if len(html.select('.lyrics')) > 0:
        bot.send_message(message.from_user.id, song)
    else:
        bot.send_message(message.from_user.id, 'Не могу найти песню...')
    markup = types.InlineKeyboardMarkup()
    conBtn = types.InlineKeyboardButton(text='Продолжить', callback_data='song')
    markup.add(conBtn)
    bot.send_message(message.from_user.id, "Продолжить?", reply_markup=markup)

def getJoke(message):
    addUrl = ['anekdot/random1.html', 'anekdot/today.html', 'anekdot/', 'anekdot/week/', 'anekdot/month/', 'anekdot/blonde/', 'anekdot/vk/', 'anekdot/today/', 'intim/', 'ancomp/', 'anekdot/black']
    req = requests.get('http://anekdotov.net/' + random.choice(addUrl))
    html = BS(req.content, 'html.parser')
    jokes = []
    for el in html.select('form > div'):
        jokes.append(el.text)
    try:
        markup = types.InlineKeyboardMarkup()
        conBtn = types.InlineKeyboardButton(text='Еще анекдот!', callback_data='joke')
        markup.add(conBtn)
        bot.send_message(message.from_user.id, random.choice(jokes), reply_markup=markup)
    except:
        markup = types.InlineKeyboardMarkup()
        conBtn = types.InlineKeyboardButton(text='Еще анекдот!', callback_data='joke')
        markup.add(conBtn)
        bot.send_message(message.from_user.id, 'Что-то пошло не так...', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "weather":
        bot.send_message(call.message.chat.id, "Введи город")
        bot.register_next_step_handler(call.message, getWeather)
    elif call.data == "translate":
        bot.send_message(call.message.chat.id, "Введи слово на английском")
        bot.register_next_step_handler(call.message, getTranslation)
    elif call.data == "song":
        bot.send_message(call.message.chat.id, "Введите название исполнителя и песни")
        bot.register_next_step_handler(call.message, getSongText)
    elif call.data == "joke":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        yesBtn = types.InlineKeyboardButton(text="Да")
        noBtn = types.InlineKeyboardButton(text="Нет")
        markup.row(yesBtn, noBtn)
        bot.send_message(call.message.chat.id, "Хочешь анекдот?", reply_markup=markup)
        bot.register_next_step_handler(call.message, getJoke)
    elif call.data == 'main':
        bot.send_message(call.message.chat.id, "Слушаюсь")
        bot.register_next_step_handler(call.message, get_text_messages)

bot.polling(none_stop=True, interval=0)


