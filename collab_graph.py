"""File containing the collaboration graph class."""

from typing import Any

from artist import _Artist


class CollabGraph:
    """A collaboration graph.

    Representation Invariants:
        - all(name == self._vertices[name].name for name in self._artists)
    """

    # Private Instance Attributes:
    #     - _artists:
    #         A collection of the artist vertices contained in this collaboration graph.
    #         Maps the name of an artist to its respective _Artist object.

    _artists: dict[str, _Artist]

    def __init__(self) -> None:
        """
        Initialize an empty collaboration graph (no artist vertices or edges).
        """
        self._artists = {}

    def get_vertex(self, name: Any) -> _Artist:
        """
        Return the vertex representation of the artist.
        """
        return self._artists[name]

    def get_artists(self) -> set:
        """
        Return the set of artist vertices in this collaboration graph.
        """
        return {self._artists[artist] for artist in self._artists}

    def get_artist_names(self) -> set:
        """
        Return the set of artist names in this collaboration graph.
        """
        return set(self._artists)

    def add_artist(self, name: Any, info: dict[str, Any]) -> None:
        """
        Add an artist vertex with the given name to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - name not in self._artists
        """
        if name not in self._artists:
            self._artists[name] = _Artist(name, set(), info)

    def add_edge(self, name1: Any, name2: Any) -> None:
        """Add an edge between the two artists (vertices) with the given names in this graph.

        Raise a ValueError if name1 or name2 do not appear as vertices in this graph.

        Preconditions:
            - name1 != name2
        """
        if name1 in self._artists and name2 in self._artists:
            a1 = self._artists[name1]
            a2 = self._artists[name2]

            a1.neighbours.add(a2)
            a2.neighbours.add(a1)
        else:
            raise ValueError


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["spotipy", "webbrowser", "math", "pyvis.network", "spotipy.oauth2"],
        'allowed-io': ["analyze_graph"],
        'max-line-length': 100
    })
