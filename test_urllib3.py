import sys
import time
import random
import datetime
import telepot

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if chat_id != USER_ID:
        return

    if content_type != 'text':
        return

    command = msg['text']

    if command == '/roll':
        bot.sendMessage(chat_id, random.randint(1,6))

TOKEN, USER_ID = sys.argv[1], int(sys.argv[2])

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print('I am listening ...')

while 1:
    bot.sendMessage(USER_ID, 'Heartbeat')
    bot.sendMessage(USER_ID, 'Heartbeat')
    bot.sendMessage(USER_ID, 'Heartbeat')
    bot.sendMessage(USER_ID, 'Heartbeat')
    bot.sendMessage(USER_ID, 'Heartbeat')
    bot.sendMessage(USER_ID, '---------')
    time.sleep(180)
