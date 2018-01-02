###################################
# * Title: starbot.py
# * Author: Chen Yijia
# * Updating date: 2018.1.3
###################################
from flask import Flask, request
from transitions import State
from transitions.extensions import GraphMachine as Machine
import telegram
import sys
from io import BytesIO


API_TOKEN='462585096:AAGZJmZBt-WXhh1AhJN6OrFzLALip7SKpz0'
WEBHOOK_URL='https://05d88f63.ngrok.io'

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
     'unless': 'go_back'}
]

#create a state machine
class Game(object):
    def print_state(self, update):
        print("current state=", self.state)
    def on_enter_init(self, update):
        update.message.reply_text("initial state")
        update.message.reply_text("Hi, I'm Starbot, you can type in \nthe following command:\n1.mockingjay\n2.go to q2\n3.go to q3\n\nIf you want to find me again, \njust type in <go to init>.")
    def on_enter_q1(self, update):
        re_text=update.message.text
        update.message.reply_text(re_text)
    def on_enter_q2(self, update):
        update.message.reply_text("I'm q2")
    def on_enter_q3(self, update):
        update.message.reply_text("I'm q3")

    def if_enter_q1(self, update):
        text=update.message.text
        return text.lower()=='mockingjay'
    def if_enter_q2(self, update):
        text=update.message.text
        return text.lower()=='go to q2'
    def if_enter_q3(self, update):
        text=update.message.text
        return text.lower()=='go to q3'
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

#diagram
#machine=Machine(model=life_bot,
#                states=states,
#                transitions=transitions,
#                initial='baby',
#                title='figure record')
#record.get_graph().draw('state_diagram.png', prog='dot')




#tell telegram where to send the message it received
def _set_webhook():
    status=bot.set_webhook('https://05d88f63.ngrok.io/hook')
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

#how to handle the message when bot receive
@app.route('/hook', methods=['POST'])
def webhook_handler():
    update=telegram.Update.de_json(request.get_json(force=True), bot)
    print("receive update.message.text=", update.message.text, "~~~")

    if star_bot.state=="init":
        if update.message.text=="mockingjay":
            update.message.reply_text("I'm mocking jay")
            star_bot.advance(update)
        elif update.message.text=="go to q2":
            star_bot.advance(update)
        elif update.message.text=="go to q3":
            star_bot.advance(update)

    elif star_bot.state=="q1":
        star_bot.q1_loop(update)
        if update.message.text=="go to init":
            star_bot.back(update)

    elif star_bot.state=="q2":
        if update.message.text=="go to init":
            star_bot.back(update)

    elif star_bot.state=="q3":
        if update.message.text=="go to init":
            star_bot.back(update)

    return 'ok'


@app.route('/')
def message():
    return 'the deadline of final project is on 1/3.'


if __name__ == '__main__':
    _set_webhook()
    app.run(port=5000)


