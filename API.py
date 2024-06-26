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
# user_id = "6niwco3w1t5vjo511n09z5pbz"
# playlists = print(get_user_public_playlists(user_id))


def mood_recommendations(mood,tracks):
    track_descriptions = [f"{track['name']} by {', '.join(track['artists'])}" for track in tracks[:10]]
    prompt = f"Given the following tracks from a user's playlist: {', '.join(track_descriptions)}, " \
             f"and user's current mood is {mood}, " \
             f"recommend song that matches the user's manual recommendations."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Generate a playlist based on the mood '{mood}'"}
        ])
    return response.choices[0].message.content
def get_lyrics ():
    song_name = input("Enter any song name: ")
    prompt = f"Given the song {song_name}, provide lyrics for the song."\
            f"if you can't find the lyrics, provide a summary of the song."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Provide lyrics for the song {song_name}"}
        ])
    return response.choices[0].message.content







def get_manual_recommendations():
    print("Manual recommendations:")
    recommendations = []
    for i in range(2):
        track_name = input("Enter track name: ")
        artist_name = input("Enter artist name: ")
        recommendations.append({
            'name': track_name,
            'artists': [artist_name]
        })
    return recommendations
def main():
    print("Welcome to the Moodify App!")
    print("Type 1 to get mood recommendations")
    print("Type 2 to get lyrics of a song")
    response = input("Enter your choice: ")
    if response == "1":
        user_spotify  = input("Do you want to use Spotify? (y/n) ")
        if user_spotify == "y":
            user_id = "6niwco3w1t5vjo511n09z5pbz"
            playlists = get_user_public_playlists(user_id)
            all_tracks = []
            for playlist in playlists:
                print(f"Getting tracks from playlist: {playlist['name']}")
                playlist_tracks = get_playlist_tracks(playlist['id'])
                all_tracks.extend(playlist_tracks)
        else:
            all_tracks = get_manual_recommendations()
        mood = input("How are you feeling? (e.g. happy, sad, relaxing) ")
        print(mood_recommendations(mood, all_tracks))
    elif response == "2":
        print(get_lyrics())
    else:
        print("Invalid choice. Please try again.")

    # user_spotify  = input("Do you want to use Spotify? (y/n) ")
    # if user_spotify == "y":
    #     user_id = "6niwco3w1t5vjo511n09z5pbz"
    #     playlists = get_user_public_playlists(user_id)
    #     all_tracks = []
    #     for playlist in playlists:
    #         print(f"Getting tracks from playlist: {playlist['name']}")
    #         playlist_tracks = get_playlist_tracks(playlist['id'])
    #         all_tracks.extend(playlist_tracks)
    # else:
    #     all_tracks = get_manual_recommendations()
   

    # #tracks = get_playlist_tracks(playlist_id)
    # mood = input("How are you feeling? (e.g. happy, sad, relaxing) ")
   
    # print(mood_recommendations(mood, all_tracks))


if __name__ == "__main__":
        main()




# mood = input("How are you feeling? (e.g. happy, sad, relaxing) ")
# response = (
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

