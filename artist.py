"""File containing the artist class."""

from __future__ import annotations
from typing import Any


class _Artist:
    """An artist vertex in the collaboration graph.

    Instance Attributes:
        - name: The name of this artist.
        - neighbours: The artist vertices that are adjacent to this artist.
        - info: Information about the artist provided by the Spotify API.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    info: dict[str, Any]
    neighbours: set[_Artist]
    name: str

    def __init__(self, name: str, neighbours: set[_Artist], info: dict[str, Any]) -> None:
        """
        Initialize a new artist vertex with the given item and neighbours.
        """
        self.name = name
        self.neighbours = neighbours
        self.info = info

    def degree(self) -> int:
        """
        Return the degree of this artist vertex.
        """
        return len(self.neighbours)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["spotipy", "webbrowser", "math", "pyvis.network", "spotipy.oauth2"],
        'allowed-io': ["analyze_graph"],
        'max-line-length': 100
    })
