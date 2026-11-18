"""
This script exports all watched movies and episodes from the configured Plex libraries
to a history.json file in Trakt's watched history export format.
"""

import json
from datetime import timezone

import helpers

HISTORY_FILE = "history.json"


def get_ids(guids, guid, slug=None):
    ids = {"imdb": None}

    for entry in guids:
        scheme, _, value = entry.id.partition("://")
        if scheme == "imdb":
            ids["imdb"] = value
        elif scheme in ("tmdb", "tvdb"):
            ids[scheme] = int(value) if value.isdigit() else value

    plex_guid = guid.rsplit("/", 1)[-1] if guid and guid.startswith("plex://") else guid
    plex_ids = {"guid": plex_guid}
    if slug:
        plex_ids["slug"] = slug
    ids["plex"] = plex_ids

    return ids


def format_watched_at(viewed_at):
    return viewed_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get_movie_entry(movie, watched_at):
    return {
        "watched_at": format_watched_at(watched_at),
        "action": "watch",
        "type": "movie",
        "movie": {
            "ids": get_ids(movie.guids, movie.guid, movie.slug),
            "year": movie.year,
            "title": movie.title,
        },
    }


def get_episode_entry(episode, show, watched_at):
    return {
        "watched_at": format_watched_at(watched_at),
        "action": "watch",
        "type": "episode",
        "episode": {
            "ids": get_ids(episode.guids, episode.guid),
            "title": episode.title,
            "number": episode.index,
            "season": episode.parentIndex,
        },
        "show": {
            "ids": get_ids(show.guids, show.guid, show.slug),
            "year": show.year,
            "title": show.title,
            "aired_episodes": show.leafCount,
        },
    }


def get_movie_history(movie):
    if not movie.viewCount:
        return []

    return [get_movie_entry(movie, entry.viewedAt) for entry in movie.history() if entry.viewedAt]


def get_episode_history(episode, show):
    if not episode.viewCount:
        return []

    return [get_episode_entry(episode, show, entry.viewedAt) for entry in episode.history() if entry.viewedAt]


def main():
    plex_server = helpers.get_plex_server()

    history = []
    for library in helpers.get_libraries(plex_server):
        if library.type == "movie":
            for movie in library.all():
                history.extend(get_movie_history(movie))
                print(f"Processed movie '{movie.title}'")
        elif library.type == "show":
            for show in library.all():
                for episode in show.episodes():
                    history.extend(get_episode_history(episode, show))
                print(f"Processed show '{show.title}'")

    # assign ids in watched order (oldest first), like Trakt's own history ids
    history.sort(key=lambda entry: entry["watched_at"])
    history = [{"id": index, **entry} for index, entry in enumerate(history, start=1)]

    # most recently watched first, matching Trakt's export order
    history.sort(key=lambda entry: entry["watched_at"], reverse=True)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)

    print(f"Exported {len(history)} watched item(s) to {HISTORY_FILE}")


if __name__ == "__main__":
    main()
