import time
import telepot
from telepot.loop import MessageLoop
import os
import numpy as np
from PIL import Image
from queue import Queue
import threading 
from urllib import request
from redis import StrictRedis
import json

def find_url(text):
    import re
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls

def handle(msg):
    # print('Hello from Thread 1')
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    content_type, chat_type, chat_id = telepot.glance(msg)
    # output_queue = Queue()
    r = StrictRedis(host='localhost', port=6379)
    threading.Thread(target=reply_thread, args=(r, bot)).start()
    if content_type == "text":

        # import wget
        content = msg["text"]
        # filename = wget.download(content)
        # image = Image.open(filename)
        
        url_list = find_url(content)
        if url_list!=[]:
            url = find_url(content)[0]
            data = {'chat_id': chat_id, 'url':url}
            message = json.dumps(data)
            r.rpush('download', message.encode("utf-8"))
    if content_type == 'photo':
        file_id = msg['photo'][-1]['file_id']
        data = {'chat_id': chat_id, 'file_id': file_id}
        message = json.dumps(data)
        r.rpush('download', message.encode("utf-8"))

    # output_queue.put([chat_id, image])
    
    

def reply_thread(r, bot):
    while True:
        item = json.loads(r.blpop('prediction')[1].decode('utf-8'))
        # print(item)
        preds = item['predictions']
        chat_id = item['chat_id']
        response = ""
        for p in preds:
            response += '%s %.4f\n' % (p['label'], p['score'])
        bot.sendMessage(chat_id, response)
    

def send_message(reply_queue):

    while True:
        item = reply_queue.get()
        if item is None:
            break
        chat_id = item['chat_id']
        reply = ''
        for (idx,entry) in enumerate(item['predictions']):
            reply += "%d. %s (%s)\n" % (idx+1, entry['label'], entry['proba'])
        

if __name__ == "__main__":
    
    # Load Model
    # [vectorizer,logis] = joblib.load('model.pkl')

    # Provide your bot's token
    bot = telepot.Bot("735092509:AAHMWTa-ZCK8npB5r4FnvMfHW7wTsYLHwAo")
    MessageLoop(bot, handle).run_as_thread()
    # t2 = Thread(target=client_thread)
    while True:
        time.sleep(10)
