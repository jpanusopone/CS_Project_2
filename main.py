"""Main file for collabgraph by James Li Fan, Jason Panusopone, Rui Weng, and Loago Zambe."""

from __future__ import annotations

import webbrowser
import math
import spotipy
from pyvis.network import Network
from spotipy.oauth2 import SpotifyClientCredentials

from collab_graph import CollabGraph

CLIENT_ID = "fde1c486c2c94a68bec1203ae8f8e622"
CLIENT_SECRET = "28d7df9c67064ee4bfe24ae0083a97cc"

AUTH_MANAGER = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
SP = spotipy.Spotify(auth_manager=AUTH_MANAGER)


def get_artist(name: str) -> dict:
    """
    Retrieve the information for this artist from the Spotify API and
    return a dictionary containing the artist's name, ID, genres, popularity,
    and follower count. Also calculates includes the artist's influence score.

    Preconditions:
        - name is a valid artist name that exists on Spotify
    """
    results = SP.search(q=name, limit=1, type="artist")
    if not results['artists']['items']:
        return {}

    artist = results['artists']['items'][0]

    info = {
        "name": artist["name"],
        "artist_id": artist['id'],
        "genres": artist['genres'],
        "popularity": artist['popularity'],
        "followers": artist["followers"]["total"],
    }
    info['influence'] = calculate_influence(info)

    return info


def calculate_influence(artist_info: dict) -> int:
    """
    Calculate an artist's influence score based on their popularity and follower count.
    """
    popularity = artist_info['popularity']
    followers = artist_info['followers']

    # Avoid log(0) by adding 1
    influence_score = popularity * math.log10(followers + 1)

    return int(influence_score)


def get_collaborators(name: str) -> set:
    """
    Return the set of artists who have collaborated with the given artist searching through
    (up to) 5 of the artist's albums using the Spotify API.

    Preconditions:
        - name is a valid artist name that exists on Spotify
    """
    artist_info = get_artist(name)
    if not artist_info:
        return set()

    artist_id = artist_info["artist_id"]
    albums = SP.artist_albums(artist_id, album_type='album', limit=5)
    collaborators = []

    for album in albums['items']:
        tracks = SP.album_tracks(album['id'])
        for track in tracks['items']:
            collaborators.extend(get_song_collabs(track, artist_id))

    return set(collaborators)


def get_song_collabs(song: dict, _id: str) -> list:
    """
    Return a new list named collabs with the collaborators in this song track.
    """
    collabs = []

    for artist in song.get('artists', []):
        if artist['id'] != _id:
            collabs.append(artist['name'])

    return collabs


def build_collaboration_graph(graph: CollabGraph, artist_name: str, depth: int,
                              visited: set[str] = None) -> None:
    """
    Recursively build a collaboration graph for the artist with the given artist_name.
    """
    if visited is None:
        visited = set()

    if artist_name in visited or depth < 0:
        return

    visited.add(artist_name)

    artist_info = get_artist(artist_name)
    if artist_info is None:
        return

    graph.add_artist(artist_name, artist_info)

    if depth > 0:
        collaborators = get_collaborators(artist_name)
        for collaborator in collaborators:
            if collaborator in visited:
                collaborator_info = get_artist(collaborator)
                if collaborator_info:
                    graph.add_artist(collaborator, collaborator_info)
                    graph.add_edge(artist_name, collaborator)
                    build_collaboration_graph(graph, collaborator, depth - 1, visited)

    # if depth <= 0:
    #     return
    #
    # collaborators = get_collaborators(artist_name)
    # for collaborator in collaborators:
    #     if collaborator in visited:
    #         collaborator_info = get_artist(collaborator)
    #         if collaborator_info:
    #             graph.add_artist(collaborator, collaborator_info)
    #             graph.add_edge(artist_name, collaborator)
    #             build_collaboration_graph(graph, collaborator, depth - 1, visited)


def top_influential(graph: CollabGraph, n: int) -> list:
    """
    Print the top n most influential artists.
    """
    vertices = graph.get_artists()
    influences = [(vertex.name, vertex.info["influence"]) for vertex in vertices]

    sorted_influences = sorted(influences, key=lambda x: x[1], reverse=True)
    top_n = [f"{artist[0]}" + ", " + f"{artist[1]}" for artist in sorted_influences[:n]]

    return top_n


def top_degree(graph: CollabGraph, n: int) -> list:
    """
    Print the top n most degree artists.
    """
    vertices = graph.get_artists()
    degrees = [(vertex.name, vertex.degree()) for vertex in vertices]

    sorted_influences = sorted(degrees, key=lambda x: (x[1], x[0]), reverse=True)
    top_d = [f"{artist[0]}" + ", " + f"{artist[1]}" for artist in sorted_influences[:n]]

    return top_d


def analyze_graph(graph: CollabGraph, num_top: int) -> None:
    """
    Print an analysis of the graph (artists with the most influence and high degrees) to the
    console.
    """
    inf = top_influential(graph, num_top)
    deg = top_degree(graph, num_top)
    print("Top Influential Artists:")
    for artist in inf:
        print(artist)

    print("\nMost Connected Artists:")
    for artist in deg:
        print(artist)


def display_graph(graph: CollabGraph) -> None:
    """
    Display the artist collaboration graph using NetworkX and PyVis.
    """
    nt = Network("100vh", "100vw")

    for artist in graph.get_artist_names():
        vertex = graph.get_vertex(artist)
        popularity = vertex.info['popularity']
        genres = vertex.info['genres']
        genre_str = ", ".join(genres) if genres else ""
        followers = vertex.info['followers']
        influence = vertex.info['influence']
        spotify_link = f"https://open.spotify.com/artist/{vertex.info['artist_id']}"

        if popularity >= 70:
            color = "red"
        elif popularity >= 50:
            color = "orange"
        else:
            color = "yellow"

        title = f"""
                <b>{artist}</b><br>
                Genres: {genre_str}<br>
                Popularity: {popularity}<br>
                Followers: {followers}<br>
                Influence: {influence}
                <a href='{spotify_link}' target='_blank'>Open in Spotify</a>
                """

        nt.add_node(artist, label=artist, title=title, color=color)

    for artist in graph.get_artist_names():
        vertex = graph.get_vertex(artist)
        for neighbor in vertex.neighbours:
            nt.add_edge(artist, neighbor.name)

    nt.generate_html(name='index.html', local=True, notebook=False)
    nt.save_graph("graph.html")
    webbrowser.open_new_tab('graph.html')


if __name__ == '__main__':
    MAIN_GRAPH = CollabGraph()
    print("-=-=- Welcome to collabgraph! -=-=-")
    PROMPT_ARTIST = input("Which artist would you like to analyze? ")

    PROMPT_DEPTH = int(input("How many levels of collaboration would you like? "
                             "We recommend 2 or 3; the more levels, the longer it will take. "))

    print("Please wait as we generate your collabgraph. This may take a few seconds...")

    build_collaboration_graph(MAIN_GRAPH, PROMPT_ARTIST, PROMPT_DEPTH)
    display_graph(MAIN_GRAPH)
    analyze_graph(MAIN_GRAPH, 15)

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["spotipy", "webbrowser", "math", "pyvis.network", "spotipy.oauth2"],
        'allowed-io': ["analyze_graph"],
        'max-line-length': 100
    })
