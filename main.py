from __future__ import annotations
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Any

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
