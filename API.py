import os
import requests
import openai
from openai import OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
client = OpenAI(api_key=OPENAI_API_KEY)
AUTH_URL = 'https://accounts.spotify.com/api/token'
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': SPOTIFY_CLIENT_ID,
    'client_secret': SPOTIFY_CLIENT_SECRET,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}
BASE_URL = 'https://api.spotify.com/v1/'
def get_track_features(track_id):
    response = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
    return response.json()
def get_playlist_tracks(playlist_id):
    playlist_endpoint = f"{BASE_URL}playlists/{playlist_id}/tracks"
    response = requests.get(playlist_endpoint, headers=headers)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    data = response.json()
    tracks = []
    for item in data['items']:
        track = item['track']
        track_info = {
            'name': track['name'],
            'id': track['id'],
            'artists': [artist['name'] for artist in track['artists']],
            'album': track['album']['name']
        }
        tracks.append(track_info)
    return tracks
# def get_user_profile(access_token):
#     headers = {'Authorization': f'Bearer {access_token}'}
#     response = requests.get('https://api.spotify.com/v1/me', headers=headers)
#     return response.json()
# playlist_id = '2lxMJeFfTQK1gmAktAiYTE'
# playlist_tracks = get_playlist_tracks(playlist_id)
# for track in playlist_tracks:
#     print(f"Name: {track['name']}")
#     print(f"Artists: {', '.join(track['artists'])}")
#     print(f"Album: {track['album']}")
#     print(f"ID: {track['id']}")
#     print("---")
def get_user_public_playlists(user_id, limit=50):
    # access_token = get_access_token()
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    params = {
        'limit': min(limit, 50)
    }
    response = requests.get(f"{BASE_URL}users/{user_id}/playlists", headers=headers, params=params)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    data = response.json()
    playlists = []
    for item in data['items']:
        playlist_info = {
            'name': item['name'],
            'id': item['id'],
            'tracks_total': item['tracks']['total'],
            'public': item['public'],
            'collaborative': item['collaborative'],
            'owner': item['owner']['display_name']
        }
        playlists.append(playlist_info)
    return playlists
user_id = "6niwco3w1t5vjo511n09z5pbz"
playlists = print(get_user_public_playlists(user_id))


#new code
# mood = input("How are you feeling? (e.g. happy, sad, relaxing) ")
# response = client.create_prompt(
#     prompt=f"Generate a playlist based on the mood '{mood}'",
#     engine="text-davinci-002",
#     temperature=0.5,
#     max_tokens=100
# )

# playlist_id = response.choices[0].text

# playlists = get_user_public_playlists(user_id)
# for playlist in playlists:
#     if playlist['id'] == playlist_id:
#         tracks = get_playlist_tracks(playlist_id)
#         print("Playlist:")
#         for track in tracks:
#             print(f"Name: {track['name']}")
#             print(f"Artists: {', '.join(track['artists'])}")
#             print(f"Album: {track['album']}")
#             print(f"ID: {track['id']}")
#             print("---")