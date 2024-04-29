from flask import Flask, render_template, request, redirect, url_for
from RecommendSongs import fetch_lyrics, calculate_cosine_similarity, fetch_lyrics_and_calculate_similarity

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from PIL import Image

app = Flask(__name__)

client_id = 'your_id'
client_secret = 'your_secret'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_album_cover(song_name, artist_name):
    # Search for the track
    results = sp.search(q=f'track:{song_name} artist:{artist_name}', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        # Get the album ID
        album_id = track['album']['id']
        # Get the album details
        album = sp.album(album_id)
        # Get the URL of the album cover
        image_url = album['images'][0]['url']
        return image_url  # Return the album cover URL
    else:
        return None  # Return None if track is not found

@app.route('/', methods=['GET', 'POST'])
def input():
    return render_template('input.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    '''book_name = request.form['bookName']
    author_name = request.form['authorName']'''
    book_name = request.args.get('book')
    author_name = request.args.get('author')

    print(f"Book Name: {book_name}, Author Name: {author_name}")
    songs = fetch_lyrics_and_calculate_similarity(book_name)
    print(songs)
    '''
    if songs == 'Book not found in the dataset.':
        # Book not found in the dataset, render error template
        error_message = f"We don't have '{book_name}' in our dataset. Please try again with another book."
        return render_template('error.html', error_message=error_message)'''
    
    for index, song in songs.iterrows():
        track_name = song['track_name']
        track_artist = song['track_artist']
        
        # Get album cover URL for the song
        album_cover_url = get_album_cover(track_name, track_artist)
        
        # Update the 'album_cover_url' column in the DataFrame
        songs.at[index, 'album_cover_url'] = album_cover_url

    return render_template('result.html', songs=songs.to_dict('records'))
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=8886, debug=True)