import telebot
import requests
import random
from telebot import types
from translate import Translator
from google_images_download import google_images_download

appid = '6c8c44f35a227775cbb6c9fa35c67d2c'
bot = telebot.TeleBot('1038924278:AAHoYHOuNnzlEEh3EH8wjc0Alw9GDXJ2pWI')
        
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    ask = ['привет', 'прив', 'бот', 'чел', 'hey', 'hi', 'hello', 'bot', 'chel', 'нет']
    if message.text.lower() in ask:
        markup = types.InlineKeyboardMarkup()
        weatherBtn = types.InlineKeyboardButton(text='Узнать погоду', callback_data='weather')
        translateBtn = types.InlineKeyboardButton(text='Перевести слово', callback_data='translate')
        markup.add(weatherBtn)
        markup.add(translateBtn)
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
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        yesBtn = types.InlineKeyboardButton(text="Да", callback_data='continueWeather')
        noBtn = types.InlineKeyboardButton(text="Нет")
        #markup.add(yesBtn)
        #markup.add(noBtn)
        markup.row(yesBtn, noBtn)
        bot.send_message(message.from_user.id, text="Продолжить?", reply_markup=markup)
        
       
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
        bot.register_next_step_handler(message, getTranslation)  

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "weather":
        bot.send_message(call.message.chat.id, "Введи город")
        bot.register_next_step_handler(call.message, getWeather)
    elif call.data == "translate":
        bot.send_message(call.message.chat.id, "Введи слово")
        bot.register_next_step_handler(call.message, getTranslation)
    elif call.data == 'continueWeather':
        bot.register_next_step_handler(call.message, getWeather)

bot.polling(none_stop=True, interval=0)


