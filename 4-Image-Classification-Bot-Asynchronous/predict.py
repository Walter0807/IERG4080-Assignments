import os
from redis import StrictRedis
import numpy as np
from PIL import Image
from queue import Queue
import threading
import socket
import json
import base64
from io import BytesIO
import numpy as np
import torch
import requests

# Initialize pretrained Inception V3 model
import torchvision.models as models

# Define the preprocessing function
model = models.inception_v3(pretrained=True)
model.transform_input = True

def predict_image(im, labels):
    from torch.autograd import Variable
    import torchvision.transforms as transforms

    normalize = transforms.Normalize(
       mean=[0.485, 0.456, 0.406],
       std=[0.229, 0.224, 0.225]
    )
    preprocess = transforms.Compose([
       transforms.Resize(256),
       transforms.CenterCrop(299),
       transforms.ToTensor(),
       normalize
    ])

    img_tensor = preprocess(im)
    img_tensor.unsqueeze_(0)
    img_variable = Variable(img_tensor)

    model.eval()
    preds = model(img_variable)

    # sm = torch.nn.Softmax()
    # probabilities = sm(preds).detach().cpu().numpy()
    # print(probabilities.shape)
    # print(preds)
    import json
    

    predictions = []
    for i, score in enumerate(preds[0].data.numpy()):
        predictions.append((score, labels[str(i)][1]))
       
    predictions.sort(reverse=True)
    result = []
    for score, label in predictions[:5]:
        # print(label, score)
        entry = {"label": label, "score": float(score)}
        result.append(entry)
    return result

r = StrictRedis(host='localhost', port=6379)
content = requests.get("https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json").text
labels = json.loads(content)

while True:
	
    item = json.loads(r.blpop('image')[1].decode('utf-8'))
    print('An item received')
    chat_id = item['chat_id']
    image_data = base64.b64decode(item['image'])
    img_path = 'predict.png'
    with open(img_path, 'wb') as outfile:
        outfile.write(image_data)
    im = Image.open(img_path)
    pred_result = predict_image(im, labels)
    data = {'predictions': pred_result, 'chat_id': chat_id}
    message = json.dumps(data)
    r.rpush('prediction', message.encode("utf-8"))
    # print(message)

