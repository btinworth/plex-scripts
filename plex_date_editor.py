"""
This script updates the "Added At" date of movies and TV shows in a Plex library to match their "Originally Available At" date.
It connects to a Plex server using the provided URL and token, then iterates through the specified titles in the library,
updating the dates accordingly.
"""

from datetime import datetime

import toml
from plexapi.server import PlexServer

CONFIG = toml.load("config.toml")
PLEX_URL = CONFIG["plex"]["url"]
PLEX_TOKEN = CONFIG["plex"]["token"]
OLDEST_DATE = datetime.fromisoformat(CONFIG["dates"]["oldest"])

TITLES = []


def update_movie(movie):
    date = max(movie.originallyAvailableAt, OLDEST_DATE)
    movie.editAddedAt(date, False)
    print(f"Updated movie '{movie.title}' with {date}")


def update_show(show):
    for episode in show.episodes():
        date = max(episode.originallyAvailableAt, OLDEST_DATE)

        if episode.index == 1 and episode.parentIndex == 1:
            # update the show to use the date of the first episode
            show.editAddedAt(date, False)
            print(f"Updated show '{show.title}' with {date}")

        if episode.index == 1:
            # update the season to use the date of the first episode in the season
            season = show.season(season=episode.parentIndex)
            season.editAddedAt(date, False)
            print(f"Updated season '{season.title}' with {date}")

        episode.editAddedAt(date, False)
        print(f"Updated episode '{episode.title}' with {date}")


def get_items(plex_server):
    items = []

    for library in plex_server.library.sections():
        for title in TITLES:
            items.extend(library.search(title))

    return items


def main():
    plex_server = PlexServer(PLEX_URL, PLEX_TOKEN)

    for item in get_items(plex_server):
        if item.type == "movie":
            update_movie(item)
        elif item.type == "show":
            update_show(item)


if __name__ == "__main__":
    main()
