import json
import os

import telebot
from telebot import types
from telebot.types import InputMediaPhoto

TOKEN = '6821254499:AAENsdxcciqoQdukgkCptVqEODd99nqd8gE'
bot = telebot.TeleBot(TOKEN)

user_states = {}

with open('locations.json', 'r', encoding='utf-8') as file:
    story = json.load(file)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_states[message.chat.id] = '1'
    send_welcome_message(message.chat.id)
    send_story(message.chat.id)

def send_welcome_message(chat_id):
    bot.send_message(chat_id, "Привет! Добро пожаловать в игру!")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_states[call.message.chat.id] = call.data
    send_story(call.message.chat.id)


from telebot import types

def send_story(chat_id):
    current_state = user_states.get(chat_id)
    if not current_state:
        bot.send_message(chat_id, "Что-то пошло не так. Начните игру заново.")
        return

    current_story = story.get(current_state, {})
    if not current_story:
        bot.send_message(chat_id, "Что-то пошло не так. Начните игру заново.")
        return

    # Send images
    if 'image_urls' in current_story:
        media_group = []
        for image_url in current_story['image_urls']:
            image_path = os.path.join('images', image_url)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    media_group.append(types.InputMediaPhoto(media=image_file.read()))

        # Send images as a media group
        if media_group:
            bot.send_media_group(chat_id, media=media_group)

    # Send text message and buttons
    markup = types.InlineKeyboardMarkup()
    if 'options' in current_story:
        for option in current_story['options']:
            button = types.InlineKeyboardButton(option['text'], callback_data=option['next'])
            markup.add(button)

        text_message = current_story.get('text', '')
        if text_message:
            bot.send_message(chat_id, text_message, reply_markup=markup)

        # Check if it's a final location
        if not current_story['options']:
            del user_states[chat_id]
            send_story(chat_id)
    else:
        text_message = current_story.get('text', '')
        if text_message:
            bot.send_message(chat_id, text_message)

if __name__ == "__main__":
    bot.polling(none_stop=True)






