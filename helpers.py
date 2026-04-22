"""
Helper functions.
"""

import toml
from plexapi.server import PlexServer


def get_config():
    config = toml.load("config.toml")
    return config


def get_plex_server():
    config = get_config()
    plex_url = config["plex"]["url"]
    plex_token = config["plex"]["token"]

    return PlexServer(plex_url, plex_token)


def get_media(plex_server):
    config = get_config()

    use_filter = config["media"]["filter_use"]
    media_filter = config["media"]["filter"]

    items = []

    for library in plex_server.library.sections():
        if use_filter:
            for title in media_filter:
                titles = [x for x in library.search(title) if x.title.casefold() == title.casefold()]
                items.extend(titles)
        else:
            items.extend(library.all())

    return items
