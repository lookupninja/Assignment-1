import slack
import os
from flask import Flask, request, Response
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
import requests
import json

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

BOT_ID =  client.api_call('auth.test')['user_id']

@slack_event_adapter.on('message')
def message(payload):
    #print(payload)
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text2 = event.get('text')

    if BOT_ID != user_id:
        url = 'http://api.openweathermap.org/data/2.5/weather?q=' + text2 + '&units=metric&appid=' + os.environ['WEATHER_KEY']
        response = requests.get(url)   

        if response.status_code == requests.codes.ok:
            weather_response = response.text
            weather_data = json.loads(weather_response)["main"]
            
            #print (weather_data)
            
            output = text2.capitalize() + " current weather: \n"
            output += "\tTemp: " + str(weather_data['temp']) + " C\n"
            output += "\tFeels Like: " + str(weather_data['feels_like']) + " C"
 
            #print( output )    
            
            client.chat_postMessage(channel=channel_id, text=output)
        else:
            client.chat_postMessage(channel=channel_id, text=text2)

if __name__ == '__main__':
    app.run()