import os
import sqlite3
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

def setup_database():
    conn = sqlite3.connect('moodify.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, mood TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS recommendations (user_id TEXT, track_id TEXT, mood TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS favorite_songs (user_id Text, name TEXT, artist TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS playlists (playlist_id TEXT PRIMARY KEY, name TEXT, owner TEXT, public BOOLEAN, collaborative BOOLEAN, tracks_total INTEGER)')
    conn.commit()
    return conn

def get_track_features(track_id):
    response = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
    return response.json()

def get_playlist_tracks(playlist_id, conn):
    conn = sqlite3.connect('moodify.db')
    c = conn.cursor()
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

        c.execute('INSERT OR REPLACE INTO songs (track_id, name, artist, album) VALUES (?, ?, ?, ?)',
                    (track_info['id'], track_info['name'], ', '.join(track_info['artists']), track_info['album']))

        tracks.append(track_info)
    conn.commit()
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

def mood_recommendations(mood,tracks, genre):
    track_descriptions = [f"{track['name']} by {', '.join(track['artists'])}" for track in tracks[:10]]
    prompt = f"Given the following tracks from a user's playlist: {', '.join(track_descriptions)}, " \
             f"and user's current mood is {mood}, " \
             f"recommend song that matches the user's mood and genre {genre}."
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



def get_create_username(conn):
    c = conn.cursor()
    while True:
        username = input("Enter your username (new or existing): ")
        c.execute("SELECT * FROM users WHERE user_id = ?", (username,))
        if c.fetchone() is None:
            c.execute("INSERT INTO users (user_id, mood) VALUES (?, ?)", (username, "neutral"))
            conn.commit()
            print(f"Welcome, {username}! New user created.")
        else:
            print(f"Welcome back, {username}!")
        return username
def favorite_song(user_id, conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS favorite_songs (user_id TEXT, name TEXT, artist TEXT)')
    conn.commit()
    song_name = input("Enter the name of the song you want to favorite: ")
    artist_name = input("Enter the name of the artist: ")
    c.execute('INSERT OR REPLACE INTO favorite_songs (user_id, name, artist) VALUES (?, ?, ?)', (user_id, song_name, artist_name))
    conn.commit()
    print(f"Song {song_name} by {artist_name} has been added to your favorites.")

def print_db(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM songs')
    rows = c.fetchall()
    for row in rows:
        print(row)
def setup_database():
    conn = sqlite3.connect('moodify.db')  
    return conn

def main():
    while True:

        conn = setup_database()
        get_create_username(conn)
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
                    playlist_tracks = get_playlist_tracks(playlist['id'], conn)
                    all_tracks.extend(playlist_tracks)
            else:
                all_tracks = get_manual_recommendations()
                genre = input("Enter the genre you want to listen to: ")
            mood = input("How are you feeling? (\n  options are: sad, happy, relaxing, workout) ")
            if mood == "workout":
                print(mood_recommendations("workout", all_tracks, genre))
            elif mood == "sad":
                print (mood_recommendations("sad", all_tracks, genre))
            elif mood == "happy":
                print(mood_recommendations("happy", all_tracks, genre))
            elif mood == "relaxing":
                print(mood_recommendations("relaxing", all_tracks, genre))
            else:
                print("Invalid mood. Please try again.")
            if input(" would you like to add any of these songs to your favorite playlist? (y/n): ") == "y":
                favorite_song(user_id,conn)
        
        elif response == "2":
            print(get_lyrics())
        else:
            print("Invalid choice. Please try again.")
    #print_db(conn) 
        conn.close()

if __name__ == "__main__":
    main()