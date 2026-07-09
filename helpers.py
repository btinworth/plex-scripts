"""
Helper functions.
"""

import time

import toml
from plexapi.server import PlexServer
from requests.exceptions import RequestException

SERVER_RETRIES = 5
SERVER_RETRY_DELAY = 5


def get_config():
    config = toml.load("config.toml")
    return config


def get_plex_server():
    config = get_config()
    plex_url = config["plex"]["url"]
    plex_token = config["plex"]["token"]

    for attempt in range(1, SERVER_RETRIES + 1):
        try:
            return PlexServer(plex_url, plex_token)
        except RequestException as _error:
            if attempt == SERVER_RETRIES:
                raise

            print(f"Failed to connect to server, retrying in {SERVER_RETRY_DELAY}s...")
            time.sleep(SERVER_RETRY_DELAY)


def get_libraries(plex_server):
    config = get_config()

    use_library_filter = config["media"]["use_library_filter"]
    library_filter = config["media"]["library_filter"]

    libraries = []

    for library in plex_server.library.sections():
        if use_library_filter:
            if library.title in library_filter:
                libraries.append(library)
        else:
            libraries.append(library)

    return libraries


def get_media(plex_server):
    config = get_config()

    use_media_filter = config["media"]["use_media_filter"]
    media_filter = config["media"]["media_filter"]

    items = []

    for library in get_libraries(plex_server):
        if use_media_filter:
            for title in media_filter:
                titles = [x for x in library.search(title) if x.title.casefold() == title.casefold()]
                items.extend(titles)
        else:
            items.extend(library.all())

    return items
