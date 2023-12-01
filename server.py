from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
from chatapp import ChatApp

app = Flask(__name__)

#for gpt
import os
import openai
import time
import secret_key
openai.api_key = secret_key.SECRET_KEY



#for dalle
import json
from base64 import b64decode
from pathlib import Path

genre = 'Fantasy'
gpt = ChatApp()
gpt.chat('You are a rpg dungeon master')

char_data = {
    'genre': '',
    'features': [],
    'generations': [],
    'description':''
}

@app.route('/get_avatar_img', methods=['GET', 'POST'])
def get_avatar_img():
    global char_data
    data = request.get_json()
    # print(data)
    char_data[data['id']] = {}
    char_data[data['id']]['race'] = data['race']
    char_data[data['id']]['name'] = data['name']
    char_data[data['id']]['personality'] = data['personality']
    char_data[data['id']]['ability'] = data['ability']

    msg = '''We are adding a new player,
            name: %s,
            race: %s,
            personality: %s,
            ability: %s,
            Create a short description within 40 words for %s without mentioning character name in reply
            ''' %(data['name'], data['race'], data['personality'], data['ability'], data['name'])
    prompt = gpt.chat(msg)['content']
    # print(prompt)
    time.sleep(1)
    url = get_img("RPG avatar. " +(prompt), "256")
    # print("url:", url)

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify({'url': url})

def get_char_info(data):
    pass

def get_img(prompt, size):
    response = openai.Image.create(
        prompt= prompt,
        n=1,
        size=size + "x" + size
    )
    image_url = response['data'][0]['url']
    return image_url

@app.route('/set_genre', methods=['GET', 'PUT'])
def set_genre():
    global genre
    data = request.get_json()
    genre = data["genre"]
    intro = gpt.chat('Story Genre: ' + genre + ', create an intro to the world within 40 words')['content']
    # print(intro)
    time.sleep(1)

    race = gpt.chat('Give me 5 different words for player race with no descriptions, use format 1. word1\n 2. word2\n')['content']
    gpt.messages = gpt.messages[:-2]
    # print(race)
    time.sleep(1)

    personality = gpt.chat('Give me 5 different words for player personality with no descriptions, use format 1. word1\n 2. word2\n')['content']
    gpt.messages = gpt.messages[:-2]
    # print(personality)
    time.sleep(1)

    ability = gpt.chat('Give me 5 different words for player abilities with no descriptions, use format 1. word1\n 2. word2\n')['content']
    gpt.messages = gpt.messages[:-2]
    # print(ability)
    time.sleep(1)

    race_list = parse_value(race)
    personality_list = parse_value(personality)
    ability_list = parse_value(ability)

    # print(race_list, personality_list, ability_list, sep='\n')

    return jsonify({'intro': intro, 'race': race_list, 'personality': personality_list, 'ability': ability_list})

def parse_value(response):
    split_list = response.splitlines()
    value_list = []
    for i, item in enumerate(split_list):
        item = item.strip()
        if item != "":
            item = item[item.index(".") + 1:]
            item = item.strip()
            value_list.append(item)
    return value_list

@app.route('/player_request', methods=['GET', 'POST'])
def player_request():
    data = request.get_json()
    prompt = data["prompt"]
    # print('test', prompt)
    response = gpt.chat("Reply within 30 words. " + prompt)['content']
    # print(response)

    return jsonify({'response': response})

@app.route('/get_area_img', methods=['GET', 'POST'])
def get_area_img():
    msg = 'Describe the scenery where the players are within 40 words'
    prompt = gpt.chat(msg)['content']
    gpt.messages = gpt.messages[:-2]
    # print(prompt)
    time.sleep(1)

    url = get_img("Scenery, " + prompt, "512")
    # print("url:", url)

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify({'url': url})

# --------------------------------------------------------------


@app.route('/play/')
def play():
    return render_template('home.html', data=char_data)

@app.route('/')
def home():
    return render_template('index.html', data=char_data)


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)
    app.run(debug = True)




