import sys
import time
import threading
import random
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

"""
$ python2.7 skeleton.py <token>
A skeleton for your telepot programs.
"""

message_with_inline_keyboard = None

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print 'Chat:', content_type, chat_type, chat_id

    if content_type != 'text':
        return

    command = msg['text'].lower()

    if command == 'apri':
        markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text=' SI ', callback_data='si')],
                     [InlineKeyboardButton(text=' NO ', callback_data='no')]
                 ])

        global message_with_inline_keyboard
        #markup = ForceReply()
        message_with_inline_keyboard = bot.sendMessage(chat_id, 'Confermi?', reply_markup=markup)
    

def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print 'Callback query:', query_id, from_id, data

    if data == 'si':
        bot.answerCallbackQuery(query_id, text='apro il cancello')
    elif data == 'no':
        bot.answerCallbackQuery(query_id, text='annulllo apertura cancello')
    elif data == 'edit':
        global message_with_inline_keyboard

        if message_with_inline_keyboard:
            msgid = (from_id, message_with_inline_keyboard['message_id'])
            bot.editMessageText(msgid, 'NEW MESSAGE HERE!!!!!')
        else:
            bot.answerCallbackQuery(query_id, text='No previous message to edit')


def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print 'Chosen Inline Result:', result_id, from_id, query_string


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

bot.message_loop({'chat': on_chat_message,
                  'callback_query': on_callback_query,
#                  'inline_query': on_inline_query,
                  'chosen_inline_result': on_chosen_inline_result})
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
