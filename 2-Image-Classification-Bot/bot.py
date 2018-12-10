import time
import telepot
from telepot.loop import MessageLoop
import os
import numpy as np
from PIL import Image
from queue import Queue
import threading 
from urllib import request

def handle(msg):
    print('Hello from Thread 1')
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    content_type, chat_type, chat_id = telepot.glance(msg)
    output_queue = Queue()
    threading.Thread(target=client_thread, args=(output_queue,)).start()
    if content_type == "text":
        import wget
        content = msg["text"]
        filename = wget.download(content)
        image = Image.open(filename)
        
    if content_type == 'photo':
        bot.download_file(msg['photo'][-1]['file_id'], 'file.png')
        image = Image.open('file.png')
    output_queue.put([chat_id, image])
    
    

def client_thread(output_queue):
    import base64
    from io import BytesIO
    from PIL import Image
    import json
    import socket
    print('Hello from Thread 2')
    reply_queue = Queue()
    threading.Thread(target=send_message, args=(reply_queue,)).start()
    while True:
        item = output_queue.get()
        if item is None:
            break
        #Prepare a data string
        chat_id = item[0]
        image = item[1]
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode()
        data = {'image': encoded_image, 'chat_id':chat_id}
        paired_string = json.dumps(data)+'##END##'
        print(len(paired_string))

        # Set up a connection
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect(("localhost", 3303))
        soc.sendall(paired_string.encode('utf-8'))
        response = ''
        while response[-7:]!='##END##':
            ss = soc.recvfrom(10000)
            response += ss[0].decode('utf-8')
        res = json.loads(response[:-7])
        reply_queue.put(res)
        soc.close()

def send_message(reply_queue):
    print("Hello from Thread 3")
    while True:
        item = reply_queue.get()
        if item is None:
            break
        chat_id = item['chat_id']
        reply = ''
        for (idx,entry) in enumerate(item['predictions']):
            reply += "%d. %s (%s)\n" % (idx+1, entry['label'], entry['proba'])
        bot.sendMessage(chat_id, reply)

if __name__ == "__main__":
    
    # Load Model
    # [vectorizer,logis] = joblib.load('model.pkl')

    # Provide your bot's token
    bot = telepot.Bot("621970538:AAFZ2oIboMS3a3zlu5Yo0Vs-N_wk9nS7nBo")
    MessageLoop(bot, handle).run_as_thread()
    # t2 = Thread(target=client_thread)
    while True:
        time.sleep(10)
