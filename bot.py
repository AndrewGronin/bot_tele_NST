# -*- coding: utf-8 -*-

import telebot
import datetime
import requests
import urllib.request
import subprocess
import os
from NST import *
from config import *
from telebot import types
from flask import Flask, request
import logging



bot = telebot.TeleBot(TOKEN)

photos={}

result_storage_path = 'tmp'


# bot.set_webhook()
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(content_types=['photo'])
def handle(message):
    cid = message.chat.id
    bot.send_message(message.chat.id, '1 фото')
    photos['content'] = save_image_from_message(message)
    bot.register_next_step_handler(message, second_photo)


def second_photo(message):
    cid = message.chat.id
    bot.send_message(message.chat.id, '2 фото')

    photos['style'] = save_image_from_message(message)


    model = NST()
    model.run_model(photos['content'] , photos['style'])

    res = open('tmp/res.jpg', 'rb')



    bot.send_photo(cid, res)


    #cleanup_remove_image(image_name_1)


# ----------- Helper functions ---------------

def log_request(message):
    file = open('data/logs.txt', 'a')  # append to file
    file.write("{0} - {1} {2} [{3}]\n".format(datetime.datetime.now(), message.from_user.first_name,
                                              message.from_user.last_name, message.from_user.id))
    print(
        "{0} - {1} {2} [{3}]".format(datetime.datetime.now(), message.from_user.first_name, message.from_user.last_name,
                                     message.from_user.id))
    file.close()


def get_image_id_from_message(message):
    # there are multiple array of images, check the biggest
    return message.photo[len(message.photo) - 1].file_id


def save_image_from_message(message):
    cid = message.chat.id

    image_id = get_image_id_from_message(message)

    bot.send_message(cid, '🔥 Analyzing image, be patient ! 🔥')

    # prepare image for downlading
    file_path = bot.get_file(image_id).file_path

    # generate image download url
    image_url = "https://api.telegram.org/file/bot{0}/{1}".format(TOKEN, file_path)
    print(image_url)

    # create folder to store pic temporary, if it doesnt exist
    if not os.path.exists(result_storage_path):
        os.makedirs(result_storage_path)

    # retrieve and save image
    image_name = "{0}.jpg".format(image_id)
    urllib.request.urlretrieve(image_url, "{0}/{1}".format(result_storage_path, image_name))

    return image_name;


def cleanup_remove_image(image_name):
    os.remove('{0}/{1}'.format(result_storage_path, image_name))


'''if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200
    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url="https://neural-style-transfer-tg-bot.herokuapp.com/bot") # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.
    # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
    bot.remove_webhook()
    bot.polling()'''
bot.remove_webhook()
bot.polling()
