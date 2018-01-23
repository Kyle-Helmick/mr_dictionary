import re
import time
import requests
import json
import socket
from slackclient import SlackClient

FILE = open("secret.json", "r")
STRING_SECRETS = FILE.read()
SECRETS = json.loads(STRING_SECRETS)
FILE.close()

LANGUAGE = 'en'

slack_client = SlackClient(SECRETS['slack_key'])

user_list = slack_client.api_call("users.list")

for user in user_list.get('members'):
    if user.get('name') == "dictionary_bot":
        slack_user_id = user.get('id')
        break

if slack_client.rtm_connect():
    print("Connected!")
    while True:
        for message in slack_client.rtm_read():

            if 'text' in message and (re.search(r"Define: .+", message['text']) or re.search(r"define: .+", message['text'])):

                #print("Message received: %s" % json.dumps(message, indent=2))

                message_text = message['text']

                word = message_text[8:]

                print("message_text:", word)
                
                error = 1

                while error:
                    random_word_url = "http://api.wordnik.com:80/v4/words.json/randomWord?hasDictionaryDef=true&includePartOfSpeech=noun&minCorpusCount=0&maxCorpusCount=0&minDictionaryCount=10&maxDictionaryCount=-1&minLength=5&maxLength=-1&api_key="+SECRETS['wordnik_key']
                    
                    response = requests.get(random_word_url)
                    random_word = response.json()['word']

                    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + LANGUAGE + '/' + random_word.lower()

                    response = requests.get(url, headers={'app_id': SECRETS['oxford_id'], 'app_key': SECRETS['oxford_key']})

                    #print(response.json())

                    response = json.loads(json.dumps(response.json()))
                    try:
                        definition = response['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
                        error = 0
                    except:
                        print("need to get a new word")
                        error = 1

                    formatted_response = "The definition of {0} is: {1}".format(word, definition)

                slack_client.api_call(
                    "chat.postMessage",
                    channel=message['channel'],
                    text=formatted_response,
                    as_user=True)

        time.sleep(1)
