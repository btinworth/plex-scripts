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


def update_date(item, date):
    date = max(date, OLDEST_DATE)
    item.editField("addedAt", date, locked=False)
    item.editField("updatedAt", date, locked=False)
    print(f"Updated '{item.title}' with {date}")


def update_movie(movie):
    update_date(movie, movie.originallyAvailableAt)


def update_show(show):
    for episode in show.episodes():
        if episode.index == 1 and episode.parentIndex == 1:
            # update the show to use the date of the first episode
            update_date(show, episode.originallyAvailableAt)

        if episode.index == 1:
            # update the season to use the date of the first episode in the season
            season = show.season(season=episode.parentIndex)
            update_date(season, episode.originallyAvailableAt)

        update_date(episode, episode.originallyAvailableAt)


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
