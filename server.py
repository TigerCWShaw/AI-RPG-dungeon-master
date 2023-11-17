from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
from chatapp import ChatApp
app = Flask(__name__)

#for gpt
import os
import openai

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
    print(data)
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

    url = get_img("RPG avatar. " +(prompt))
    # print("url:", url)

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify({'url': url})

def get_char_info(data):
    pass

def get_img(prompt):
    response = openai.Image.create(
        prompt= prompt,
        n=1,
        size="256x256"
    )
    image_url = response['data'][0]['url']
    return image_url

@app.route('/set_genre', methods=['GET', 'PUT'])
def set_genre():
    global genre
    data = request.get_json()
    genre = data["genre"]
    intro = gpt.chat('Story Genre: ' + genre + ', create an intro to the world within 40 words')['content']
    # print(response)

    race = gpt.chat('Give me 5 choices for races each in one word, no need for description, use format 1. value \n 2. value\n')['content']
    personality = gpt.chat('Give me 5 choices for personalities each in one word, no need for description, use format 1. value \n 2. value\n')['content']
    ability = gpt.chat('Give me 5 choices for abilities each in one word, no need for description, use format 1. value \n 2. value\n')['content']

    # print(race, personality, ability)
    race_list = parse_value(race)
    personality_list = parse_value(personality)
    ability_list = parse_value(ability)

    print(race_list, personality_list, ability_list, sep='\n')

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

@app.route('/player_request', methods=['GET', 'PUT'])
def player_request():
    data = request.get_json()
    prompt = data["prompt"]
    response = gpt.chat("Reply within 30 words. " + prompt)['content']
    # print(response)

    return jsonify({'response': response})

# --------------------------------------------------------------

#### INIT with example data
# char_data = sample_char_data_1

@app.route('/get_features', methods=['GET', 'POST'])
def get_features():
    global char_data
    data = request.get_json()

    char_data["genre"] = data["genre"]

    features = get_features_for_char(char_data["genre"])
    char_data['features'] = features
    print(features)

    print(char_data["genre"])
    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(char_data)

def parse_features_from_gpt_response(gpt_response):
    feature_list = gpt_response['choices'][0]['message']['content'].splitlines()
    new_feature_list = []
    for i, item in enumerate(feature_list):
        item = item.strip()
        if item != "":
            item = item[item.index(".") + 1:]
            item = item.strip()
            new_feature_list.append(item)
    return new_feature_list


def get_features_for_char(genre):
    prompt = 'Give me 10 keywords that describe the appearance of a new league of legends champions from the ' + genre + ' genre using formats like this: \n 1. keyword1 \n 2. keyword2 \n 3. keyword3'
    print(prompt)
    # response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    ### PARSE THEM HERE!
    print(type(response))
    feature_list = []
    try:
        feature_list = parse_features_from_gpt_response(response)
    except:
        print("ERROR: gpt keyword response won't parse")
        print(response)

    return feature_list

@app.route('/get_images', methods=['GET', 'POST'])
def get_images():
    global char_data
    data = request.get_json()
    # print(data)
    prompt = ''
    if data['features']:
        prompt = 'League of Legend, ' + char_data['genre'] + ', ' +  ','.join(data['features'])
    print(prompt)
    new_images = generate_images(prompt)

    for i in new_images:
        char_data["generations"].append(i)

    #just send new images
    return jsonify(new_images)


def generate_images(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="b64_json",
    )

    #create json file for image
    DATA_DIR = Path.cwd() / "responses"
    DATA_DIR.mkdir(exist_ok=True)
    JSON_FILE = DATA_DIR / f"{prompt[:5]}-{response['created']}.json"
    with open(JSON_FILE, mode="w", encoding="utf-8") as file:
        json.dump(response, file)


    #convert json image data file to png
    IMAGE_DIR = Path.cwd() / "static/generated_images" / JSON_FILE.stem

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_FILE, mode="r", encoding="utf-8") as file:
        response = json.load(file)

    for index, image_dict in enumerate(response["data"]):
        image_data = b64decode(image_dict["b64_json"])
        image_file = IMAGE_DIR / f"{JSON_FILE.stem}-{index}.png"
        with open(image_file, mode="wb") as png:
            png.write(image_data)

    full_path_to_image = image_file.as_posix()
    url_for_flask = full_path_to_image[full_path_to_image.find('static'):]

    print(url_for_flask)

    images = [
        {
            "prompt": prompt,
            "url": url_for_flask, #image_file.as_posix(),
        }
    ]
    print(url_for_flask)
    return images

@app.route('/')
def home():
    # you can pass in an existing article or a blank one.
    return render_template('home.html', data=char_data)


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)
    app.run(debug = True)




