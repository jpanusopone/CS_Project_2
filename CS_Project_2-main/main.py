"""Main file for Resonate"""

from __future__ import annotations
import spotipy
from pyvis.network import Network
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Any
import networkx as nx
import webbrowser
import math


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
        - info: The artist information from the api,

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    info: dict[str, Any]
    neighbours: set[_Vertex]
    name: str

    def __init__(self, name: str, neighbours: set[_Vertex], info: dict[str, Any]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.name = name
        self.neighbours = neighbours
        self.info = info

    def degree(self) -> int:
        """Calculate the degree of this vertex."""
        return len(self.neighbours)

class Graph:
    """A graph.

    Representation Invariants:
        - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[str, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def get_vertices(self) -> set:
        """
        Return the vertex set of this graph.
        """
        return {self._vertices[vertex] for vertex in self._vertices}

    def get_vertex(self, item) -> _Vertex:
        """
        Return the vertex representation of item.
        """
        return self._vertices[item]

    def get_vertex_items(self) -> set:
        """
        Return a set containing the items of the vertices in this graph.
        """
        return {item for item in self._vertices}

    def add_vertex(self, name: Any, info: dict[str, Any]) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        if name not in self._vertices:
            self._vertices[name] = _Vertex(name, set(), info)

    def add_edge(self, name1: Any, name2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if name1 or name2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if name1 in self._vertices and name2 in self._vertices:
            v1 = self._vertices[name1]
            v2 = self._vertices[name2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError


client_id = "fde1c486c2c94a68bec1203ae8f8e622"
client_secret = "28d7df9c67064ee4bfe24ae0083a97cc"

auth_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


def get_artist(name: str):
    """Filler
    """
    results = sp.search(q=name, limit=1, type="artist")
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
    """Calculate an artist's influence score based on popularity and follower count."""

    popularity = artist_info['popularity']
    followers = artist_info['followers']

    # Avoid log(0) by adding 1
    influence_score = popularity * math.log10(followers + 1)

    return int(influence_score)

def get_collaborations(name: str):
    """Filler
    """
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

def build_collaboration_graph(graph: Graph, artist_name: str, depth: int, visited: set[str] = None) -> None:
    """
    Recursively build a graph of artist collaborations starting from the given artist."""
    if visited is None:
        visited = set()

    if artist_name in visited or depth < 0:
        return

    visited.add(artist_name)

    artist_info = get_artist(artist_name)
    if artist_info is None:
        return

    graph.add_vertex(artist_name, artist_info)

    if depth > 0:
        collaborators = get_collaborations(artist_name)
        for collaborator in collaborators:
            if collaborator not in visited:
                collaborator_info = get_artist(collaborator)
                if collaborator_info:
                    graph.add_vertex(collaborator, collaborator_info)
                    graph.add_edge(artist_name, collaborator)
                    build_collaboration_graph(graph, collaborator, depth - 1, visited)


def build_networkx(graph: Graph) -> nx.Graph:
    """Filler
    """
    nx_graph = nx.Graph()
    for artist in graph.get_vertex_items():
        nx_graph.add_node(artist)
    for artist in graph.get_vertex_items():
        vertex = graph.get_vertex(artist)
        for neighbour in vertex.neighbours:
            nx_graph.add_edge(artist, neighbour.name)
    return nx_graph

def top_influential(graph: Graph, n:int) -> list:
    """Print the top n most influential artists."""
    vertices = graph.get_vertices()
    influences = [(vertex.name, vertex.info["influence"]) for vertex in vertices]

    sorted_influences = sorted(influences, key=lambda x: x[1], reverse=True)
    top_n = [f"{artist[0]}" + "," + f"{artist[1]}" for artist in sorted_influences[:n]]

    return top_n

def top_degree(graph: Graph, n:int) -> list:
    """Print the top n most degree artists."""
    vertices = graph.get_vertices()
    degrees = [(vertex.name, vertex.degree()) for vertex in vertices]

    sorted_influences = sorted(degrees, key=lambda x: (x[1],x[0]), reverse=True)
    top_d = [f"{artist[0]}" + "," + f"{artist[1]}" for artist in sorted_influences[:n]]

    return top_d

def analyse_graph(graph: Graph, depth) -> None:
    inf = top_influential(graph, depth)
    deg =  top_degree(graph, depth)
    print("Top Influential Artists:")
    for artist in inf:
        print(artist)

    print("Most Connected Artists:")
    for artist in deg:
        print(artist)

def display_graph(graph: Graph) -> None:
    """Display the artist collaboration graph using NetworkX and PyVis"""

    nt = Network("100vh", "100vw")

    for artist in graph.get_vertex_items():
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

    for artist in graph.get_vertex_items():
        vertex = graph.get_vertex(artist)
        for neighbor in vertex.neighbours:
            nt.add_edge(artist, neighbor.name)

    nt.generate_html(name='index.html', local=True, notebook=False)
    nt.save_graph("graph.html")
    webbrowser.open_new_tab('graph.html')

main_graph = Graph()
prompt_artist = input("What artist would you like to analyse? ")
prompt_depth = int(input("How many graph levels do you want? 2 or 3 recommended. The more levels, the longer it takes. "))
print("Please wait.......")

build_collaboration_graph(main_graph, prompt_artist, prompt_depth)
display_graph(main_graph)
analyse_graph(main_graph, 15)
