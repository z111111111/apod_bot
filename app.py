
import os
from flask import Flask, request
import json
import requests 

import telebot
from telebot import types

TOKEN = 'YOUR_TOKEN' 
NASA_TOKEN = 'YOUR_NASA_TOKEN'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@bot.message_handler(commands=['start', 'help'])
def get_text_messages(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('show')
    markup.add(itembtn1)
    bot.send_message(message.from_user.id, "Привет, я показываю космическую картинку дня (а иногда это может быть и видео) NASA по введенной дате. Напиши мне: \"show\" или нажми кнопку, чтобы посмотреть!", reply_markup=markup)

def randrequest():    
    r = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={NASA_TOKEN}&count=1')
    todos = json.loads(r.text)
    return todos[0]

def get_next(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    
    if message.text == 'Начать сначала.':
        bot.send_message(message.from_user.id, 'Почему бы и нет?', reply_markup=markup)
        get_start(message)
    elif message.text == 'Показать случайную картинку.':
        bot.send_message(message.from_user.id, 'Мне тоже это нравится', reply_markup=markup)
        todos = randrequest()
        give_content(todos,message)
    else:
        bot.send_message(message.from_user.id, '!', reply_markup=markup)
        get_text_messages(message)
def give_content(todos,message):
    try:
        cr = todos['coryright']
    except:
        cr = None
    bot.send_message(message.from_user.id, todos['explanation'])
    try:
        bot.send_message(message.from_user.id, todos['date']+' '+todos['hdurl'])
    except:
        bot.send_message(message.from_user.id, todos['date']+' '+todos['url'])
    if cr:
        bot.send_message(message.from_user.id, 'Изображение защищено авторским правом. За подробностями обращайтесь в NASA.')
        bot.send_message(message.from_user.id, '© '+todos['copyright'])
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Начать сначала.')
    itembtn2 = types.KeyboardButton('Показать случайную картинку.')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.from_user.id, "Что дальше?", reply_markup=markup)
    bot.register_next_step_handler(message, get_next)
    


year = 0
month = 0
day = 0

@bot.message_handler(commands=['show'])
@bot.message_handler(func=lambda msg: msg.text == 'show')
def get_start(message):
    markup = types.ReplyKeyboardRemove(selective=False)

    
    bot.send_message(message.from_user.id, 'Введи какой-нибудь год. Если ввод не потянет на год, покажу случайную картинку.', reply_markup=markup)
    bot.register_next_step_handler(message, get_year)
    
def get_year(message):    
    if len(message.text) == 4:
        try:
            global year
            year = int(message.text)
            bot.send_message(message.from_user.id, 'Введи месяц на тех же условиях.')
            bot.register_next_step_handler(message, get_month)
        except:
            todos = randrequest()
            give_content(todos,message)
    else:
        todos = randrequest()
        give_content(todos,message)
        
def get_month(message): 
    if len(message.text) <= 2:
        try:
            global month
            month = int(message.text)
            bot.send_message(message.from_user.id, 'И так же день.')
            bot.register_next_step_handler(message, get_day)
        except:
            todos = randrequest()
            give_content(todos,message)
    else:
        todos = randrequest()
        give_content(todos,message)

def get_day(message): 
    if len(message.text) <= 2:
        
        try:
            global day
            day = int(message.text)
            r = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={NASA_TOKEN}&date={str(year)}-{str(month)}-{str(day)}')
            
            todos = json.loads(r.text)
            try:
                msg = todos['msg']
            except:
                msg = None
                give_content(todos,message)
            if msg:
                bot.send_message(message.from_user.id, msg)
        except:
            todos = randrequest()
            give_content(todos,message)
    else:
        todos = randrequest()
        give_content(todos,message)
        

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://your-flask-app.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))