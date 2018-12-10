import time
import telepot
from telepot.loop import MessageLoop
import os
import numpy as np
from sklearn.externals import joblib

def handle(msg):
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == "text":
        content = msg["text"]
        x = vectorizer.transform([content])
        if logis.predict(x):
            reply = 'This is a positive review! '
        else:
            reply = 'This is a negative review! '
        # print(logis.predict_proba(x))
        reply += str(round(logis.predict_proba(x)[0][1],2))
        bot.sendMessage(chat_id, reply)

if __name__ == "__main__":
    
    # Load Model
    [vectorizer,logis] = joblib.load('model.pkl')

    # Provide your bot's token
    bot = telepot.Bot("621970538:AAFZ2oIboMS3a3zlu5Yo0Vs-N_wk9nS7nBo")
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)