"""
This script updates the "Added At" date of movies and TV shows in a Plex library to match their "Originally Available At" date.
It connects to a Plex server using the provided URL and token, then iterates through the specified titles in the library,
updating the dates accordingly.
"""

from datetime import datetime

import helpers


def get_oldest_date():
    config = helpers.get_config()
    oldest_date_str = config["dates"]["oldest"]
    return datetime.fromisoformat(oldest_date_str)


def update_date(item, date, name=""):
    date = max(date, get_oldest_date())
    item.editField("addedAt", date, locked=False)
    item.editField("updatedAt", date, locked=False)
    print(f"Updated '{name if name else item.title}' with {date}")


def update_movie(movie):
    update_date(movie, movie.originallyAvailableAt)


def update_show(show):
    for episode in show.episodes():
        if episode.index == 1 and episode.parentIndex == 1:
            # update the show to use the date of the first episode
            update_date(show, episode.originallyAvailableAt, f"{show.title}")

        if episode.index == 1:
            # update the season to use the date of the first episode in the season
            season = show.season(season=episode.parentIndex)
            update_date(season, episode.originallyAvailableAt, f"{show.title} (Season {episode.parentIndex})")

        update_date(episode, episode.originallyAvailableAt, f"{show.title} (S{episode.parentIndex:02}E{episode.index:02}) - {episode.title}")


def main():
    plex_server = helpers.get_plex_server()

    for item in helpers.get_media(plex_server):
        if item.type == "movie":
            update_movie(item)
        elif item.type == "show":
            update_show(item)


if __name__ == "__main__":
    main()
