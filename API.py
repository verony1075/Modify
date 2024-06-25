import os
import requests
import openai
from openai import OpenAI


# Set environment variables
my_api_key = os.getenv('OPENAI_KEY')


openai.api_key = my_api_key




# WRITE YOUR CODE HERE
from openai import OpenAI


# Create an OpenAPI client using the key from our environment variable
client = OpenAI(
    api_key=my_api_key,
)


# Specify the model to use and the messages to send
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a university instructor and can explain programming concepts clearly in a few words."},
        {"role": "user", "content": "What are the advantages of pair programming?"}
    ]
)
print(completion.choices[0].message.content)





CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')


AUTH_URL = 'https://accounts.spotify.com/api/token'


auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})


auth_response_data = auth_response.json()


access_token = auth_response_data['access_token']


headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}


BASE_URL = 'https://api.spotify.com/v1/'
track_id = input('Enter track id: ')
r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)


print(r.json())

