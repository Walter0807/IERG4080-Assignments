import os
from flask import Flask, request, jsonify
import json
import csv
import numpy as np
import pandas as pd
import random
import time
from scipy.stats import pearsonr

app = Flask(__name__)
app.host_addr = "localhost" # Default

def load_data(datapath):
    ratings = {}
    new_mid = {}
    cnt = 0
    links = {}
    titles = {}
    with open(datapath+'ratings_small.csv') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for row in f_csv:
            userId = row[0]
            movieId = row[1]
            rate = row[2]
            if not (movieId in new_mid):
                new_mid[movieId] = cnt
                cnt += 1
            movieId = new_mid[movieId]
            if not (userId in ratings):
                ratings[userId] = np.zeros(app.num_movies)
            ratings[userId][movieId] = float(rate)

    with open(datapath+'links.csv') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for row in f_csv:
            movieId = row[0]
            imdbId = row[1]
            if not (movieId in new_mid):
                continue
            movieId = new_mid[movieId]
            links[movieId] = imdbId

    with open(datapath+'movies.csv') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for row in f_csv:
            movieId = row[0]
            title = row[1]
            if not (movieId in new_mid):
                continue
            movieId = new_mid[movieId]
            titles[movieId] = title
    return ratings, titles, links, new_mid

temp = pd.read_csv("ratings_small.csv");
set_movies = set(temp['movieId'])
app.num_movies = len(set_movies)
app.ratings, app.titles, app.links, app.new_mid = load_data('data/')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()    
    chat_id = data["chat_id"]
    chat_id = data["chat_id"]
    if chat_id in app.ratings:
        exists = 1
    else:
        exists = 0
    return jsonify(exists=exists)   


@app.route('/get_unrated_movie', methods=['POST'])
def get_unrated_movie():
    data = request.get_json()    
    chat_id = data["chat_id"]
    if chat_id in app.ratings:
        unrated = np.where(app.ratings[chat_id]==0)[0]
    else:
        unrated = range(app.num_movies)
    to_rate = int(random.choice(unrated))
    title = app.titles[to_rate]
    url = 'https://www.imdb.com/title/tt%s/' % app.links[to_rate]
    print(to_rate, title, url)
    return jsonify(id=to_rate, title=title, url=url) 

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    data = request.get_json()    
    chat_id = data["chat_id"]
    movieId = data["movie_id"]
    rate = data["rating"]
    print(movieId, rate)
    try:
        if not (chat_id in app.ratings):
            app.ratings[chat_id] = np.zeros(app.num_movies)
        app.ratings[chat_id][movieId] = float(rate)
    except Exception as e:
        print(e)
        return jsonify(status='fail') 
    else:
        return jsonify(status='success') 

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()    
    chat_id = data["chat_id"]
    top_n = data["top_n"]
    if chat_id in app.ratings:
        rated_num = sum(app.ratings[chat_id]>0)
    else:
        rated_num = 0
    to_recommend = []
    if rated_num>=10:
        to_recommend = []
        rec_id = get_recommendation(chat_id, top_n) 
        for item in rec_id:
            title = app.titles[item]
            url = 'https://www.imdb.com/title/tt%s/' % app.links[item]
            to_recommend.append({"title":title, 'url':url})
    return jsonify(movies=to_recommend)     

def get_recommendation(uid, topn):
    mean_x = get_mean(uid)
    x = 0
    y = 0
    for user in app.ratings:
        if user==uid:
            continue
        sim = similarity(uid,user)
        mean_u = get_mean(user)
        sx = np.zeros(app.num_movies)
        sy = np.zeros(app.num_movies)
        for (idx,r) in enumerate(app.ratings[user]):
            if r>0:
                sx[idx] = sim*(r-mean_u)
                sy[idx] = sim
        x = x + sx
        y = y + sy
    score = x/y + mean_x
    return np.argsort(score)[::-1][:topn]

# similarity between users
def similarity(u1, u2):
    r, _ = pearsonr(app.ratings[u1], app.ratings[u2])
    return r

def get_mean(uid):
    return np.mean([r for r in app.ratings[uid] if r > 0])


if __name__ == '__main__':
    app.run(host=app.host_addr, port=5000, debug=False)



