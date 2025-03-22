import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_id = "fde1c486c2c94a68bec1203ae8f8e622"
client_secret = "28d7df9c67064ee4bfe24ae0083a97cc"

auth_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(auth_manager = auth_manager)

def get_artist(name):
    results = sp.search(q = name, limit = 1, type = "artist")
    artist = results['artists']['items'][0]
    info = {
        "name" : artist["name"],
        "artist_id" : artist['id'],
        "genres" : artist['genres'],
        "popularity": artist['popularity']
    }
    return info


def get_collaborations(name):
    artist_id = get_artist(name)["artist_id"]
    albums = sp.artist_albums(artist_id, album_type='album', limit=5)
    collaborators = []
    for album in albums['items']:
        tracks = sp.album_tracks(album['id'])
        for track in tracks['items']:
            if track['artists']:
                for artist in track['artists']:
                    if artist['id'] != artist_id:
                        collaborators.append(artist['name'])

    return set(collaborators)

