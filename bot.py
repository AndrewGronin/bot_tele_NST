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

photos = {}

result_storage_path = 'tmp'


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     '''Привет, я могу перенести стиль с одной картинки на другую.
                     
Чтобы начать, пришли картинку, на которую будем переносить стиль.

Подробности по команде /help''')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id,
                     '''1) Картинки обрезаются до квадратных,размерность понижается
                     
2)Перенос может занять несколько минут(если очень не повезет)
                     ''')


@bot.message_handler(content_types=['photo'])
def handle(message):
    cid = message.chat.id

    photos['content'] = save_image_from_message(message)
    bot.send_message(cid, 'Отлично, теперь пришли фото со стилем')
    bot.register_next_step_handler(message, second_photo)


def second_photo(message):
    try:
        cid = message.chat.id

        photos['style'] = save_image_from_message(message)
        bot.send_message(cid, 'Начинаю перенос, на это уйдет примерно 30 секунд')

        model = NST()
        model.run_model(photos['content'], photos['style'])

        res = open('tmp/res.jpg', 'rb')

        bot.send_photo(cid, res)
        bot.send_message(cid, 'Готово, пришли новое фото если хочешь повторить')

        cleanup_remove_image(photos['content'])
        cleanup_remove_image(photos['style'])
    except:
        bot.send_message(message.chat.id,'Помоему ты сделал что-то не так, давай сначала')


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


bot.remove_webhook()
bot.polling()
