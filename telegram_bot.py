import json
import requests
import time
from mongoengine import *
import json

connect('olam-ml3')


class Olamdict(Document):
    english = StringField()
    speech = StringField()
    malayalam = StringField()


TOKEN = ""
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text,chat_id)
def getmal(text):
    olam = Olamdict.objects(english=text)
    mal = []
    if olam:
        for entry in olam:
            mal.append(entry.malayalam)
    return mal

def generateString(data):
    finalString = ''
    for item in data:
        finalString = finalString+item+'\n'
    return finalString

def send_message(text,chat_id):
    data = getmal(text)
    if data:
        res = generateString(data)
    else:
        res = "Nothing found"
    url = URL + "sendMessage?text={}&chat_id={}".format(res, chat_id)
    get_url(url)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        send_message(text, chat)

def main():
    last_textchat = (None,None)
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)
    while True:

        text,chat = get_last_chat_id_and_text(get_updates())
        if(text,chat)!= last_textchat:
            send_message(text,chat)
            last_textchat = (text,chat)
        time.sleep(0.5)

if __name__=="__main__":
    main()

