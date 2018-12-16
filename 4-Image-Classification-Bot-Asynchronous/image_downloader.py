from redis import StrictRedis
from PIL import Image
import json
import wget
from io import BytesIO
import base64
import telepot

r = StrictRedis(host='localhost', port=6379)
bot = telepot.Bot("735092509:AAHMWTa-ZCK8npB5r4FnvMfHW7wTsYLHwAo")

while True:
    item = json.loads(r.blpop('download')[1].decode('utf-8'))
    # print(item)
    print('An item received')
    chat_id = item['chat_id']
    if 'file_id' in item:
        bot.download_file(item['file_id'], 'file.png')
        image = Image.open('file.png')
    elif 'url' in item:
	    filename = wget.download(item['url'])
	    image = Image.open(filename)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode()
    data = {'chat_id':chat_id, 'image': encoded_image}
    message = json.dumps(data)
    r.rpush('image', message.encode("utf-8"))