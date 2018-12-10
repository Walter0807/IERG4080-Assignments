import os
import numpy as np
from PIL import Image
from queue import Queue
import threading
import socket
import json
import base64
from io import BytesIO
import keras    
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np


def predict(q):
	model = ResNet50(weights='imagenet')
	while True:
		client_socket = q.get()
		if client_socket is None:
			break
		msg = ''
		while msg[-7:]!='##END##':
			ss = client_socket.recvfrom(10000)
			msg += ss[0].decode('utf-8')
		print(len(msg))
		dic = json.loads(msg[:-7])
		chat_id = dic['chat_id']
		image_data = base64.b64decode(dic['image'])
		img_path = 'predict.png'
		with open(img_path, 'wb') as outfile:
			outfile.write(image_data)
		img = image.load_img(img_path, target_size=(224, 224))
		x = image.img_to_array(img)
		x = np.expand_dims(x, axis=0)
		x = preprocess_input(x)
		preds = decode_predictions(model.predict(x), top=5)[0]
		pred_list = []
		for entry in preds:
		    dic = {'label': entry[1], 'proba': str(entry[2])}
		    pred_list.append(dic)
		result = {'predictions':pred_list, 'chat_id': chat_id}
		print(result)
		client_socket.sendall((json.dumps(result)+'##END##').encode('utf-8'))
		client_socket.close()
		



def main():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("localhost", 3303))
	server_socket.listen(10)
	q = Queue()
	threading.Thread(target=predict, args=(q,)).start()
	while True:
		(client_socket, address) = server_socket.accept()
		q.put(client_socket)
		

main()
