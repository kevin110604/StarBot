###############################################
# * Title: starbot.py
# * Author: Chen Yijia
# * Updating date: 2018.1.3
###############################################
from flask import Flask, request, send_file
from transitions import State
from transitions.extensions import GraphMachine as Machine
import telegram
import sys
from io import BytesIO
import random

API_TOKEN='YOUR_API_TOKEN'
WEBHOOK_URL='https://YOUR_URL'

app=Flask(__name__)
bot=telegram.Bot(token=API_TOKEN)

#initialize states and transitions
states=['init', 'q1', 'q2', 'q3']
transitions=[
    {'trigger': 'advance',
     'source': 'init',
     'dest': 'q1',
     'conditions': 'if_enter_q1'},

    {'trigger': 'advance',
     'source': 'init',
     'dest': 'q2',
     'conditions': 'if_enter_q2'},

    {'trigger': 'advance',
     'source': 'init',
     'dest': 'q3',
     'conditions': 'if_enter_q3'},

    {'trigger': 'back',
     'source': '*',
     'dest': 'init',
     'conditions': 'go_back'},

    {'trigger': 'q1_loop', 
     'source': 'q1',
     'dest': 'q1',
     'unless': 'go_back'},

    {'trigger': 'q2_loop', 
     'source': 'q2',
     'dest': 'q2',
     'unless': 'go_back'},

    {'trigger': 'q3_loop', 
     'source': 'q3',
     'dest': 'q3',
     'unless': 'go_back'},
]

#create a state machine
class Game(object):
    def print_state(self, update):
        print("current state=", self.state)

    def on_enter_init(self, update):
        update.message.reply_text("Hi, I'm Starbot, you can type in \n\
the following command:\n1. mockingjay\n2. image\n3. predict\n\n\
If you want to find me again, \njust type in 'go to init'")

    def on_enter_q1(self, update):
        re_text=update.message.text
        update.message.reply_text(re_text)

    def on_enter_q2(self, update):
        if (update.message.text=="slut"):
            update.message.reply_text("sending...")
            CHAT_ID=update.message.chat_id
            bot.send_photo(chat_id=CHAT_ID, photo=open('pic1.jpg', 'rb'))
        elif (update.message.text=="scared"):
            update.message.reply_text("sending...")
            CHAT_ID=update.message.chat_id
            bot.send_photo(chat_id=CHAT_ID, photo=open('pic2.jpg', 'rb'))
        elif (update.message.text=="goose"):
            update.message.reply_text("sending...")
            CHAT_ID=update.message.chat_id
            bot.send_photo(chat_id=CHAT_ID, photo=open('pic3.jpg', 'rb'))
        update.message.reply_text("I have three image:\n1. slut\n2. scared\n3. goose")

    def on_enter_q3(self, update):
        if (update.message.text=="future"):
            re_text=random.choice(['very lucky', 'normal', 'bad luck', 'everything shit'])
            update.message.reply_text(re_text)
        elif (update.message.text=="final grade"):
            re_text=random.randint(0, 100)
            update.message.reply_text(re_text)
        update.message.reply_text("You can predict:\n1. future\n2. final grade")

    def if_enter_q1(self, update):
        text=update.message.text
        return text.lower()=='mockingjay'
    def if_enter_q2(self, update):
        text=update.message.text
        return text.lower()=='image'
    def if_enter_q3(self, update):
        text=update.message.text
        return text.lower()=='predict'
    def go_back(self, update):
        text=update.message.text
        return text.lower()=='go to init'


star_bot=Game()
machine=Machine(model=star_bot,
                states=states,
                transitions=transitions,
                initial='init',
                after_state_change='print_state',
                ignore_invalid_triggers=True)

#tell telegram where to send the message it received
def _set_webhook():
    status=bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

#how to handle the message when bot receive
@app.route('/', methods=['POST'])
def webhook_handler():
    update=telegram.Update.de_json(request.get_json(force=True), bot)
    print("receive update.message.text=", update.message.text, "~~~")

    if star_bot.state=="init":
        star_bot.back(update)
        if update.message.text=="mockingjay":
            update.message.reply_text("I'm mockingjay")
            star_bot.advance(update)
        elif update.message.text=="image":
            star_bot.advance(update)
        elif update.message.text=="predict":
            star_bot.advance(update)

    elif star_bot.state=="q1":
        star_bot.q1_loop(update)
        if update.message.text=="go to init":
            star_bot.back(update)

    elif star_bot.state=="q2":
        star_bot.q2_loop(update)
        if update.message.text=="go to init":
            star_bot.back(update)

    elif star_bot.state=="q3":
        star_bot.q3_loop(update)
        if update.message.text=="go to init":
            star_bot.back(update)

    return 'ok'


@app.route('/')
def message():
    return 'the deadline of final project is on 1/3.'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io=BytesIO()
    star_bot.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == '__main__':
    _set_webhook()
    app.run(port=5000)


