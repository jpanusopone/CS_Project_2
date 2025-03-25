from __future__ import annotations
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Any
import networkx as nx
import matplotlib.pyplot as plt


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

    def __init__(self, name: str, neighbours: set[_Vertex],info: dict[str, Any]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.name = name
        self.neighbours = neighbours
        self.info = info

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
sp = spotipy.Spotify(auth_manager = auth_manager)

def get_artist(name: str):
    results = sp.search(q = name, limit = 1, type = "artist")
    artist = results['artists']['items'][0]
    info = {
        "name" : artist["name"],
        "artist_id" : artist['id'],
        "genres" : artist['genres'],
        "popularity": artist['popularity']
    }
    return info


def get_collaborations(name: str):
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

def display_graph(graph: Graph) -> None:
    """Display the artist collaboration graph using NetworkX and Matplotlib."""
    G = nx.Graph()

    for artist in graph._vertices:
        G.add_node(artist)

    for artist, vertex in graph._vertices.items():
        for neighbor in vertex.neighbours:
            G.add_edge(artist, neighbor.name)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=8, edge_color="gray")
    plt.title("Artist Collaboration Graph")
    plt.show()