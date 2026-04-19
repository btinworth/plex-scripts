"""
This script refreshes posters for all movies and shows in the Plex library.
For shows, it refreshes the poster for each season as well.
"""

import helpers


def set_poster(item):
    posters = item.posters()
    if posters and len(posters) > 0:
        item.setPoster(posters[0])
        item.unlockPoster()

    print(f"Refreshed poster for '{item.title}'")


def refresh_movie_poster(movie):
    set_poster(movie)


def refresh_show_poster(show):
    for season in show.seasons():
        set_poster(season)

    set_poster(show)


def main():
    plex_server = helpers.get_plex_server()

    for item in helpers.get_media(plex_server):
        if item.type == "movie":
            refresh_movie_poster(item)
        elif item.type == "show":
            refresh_show_poster(item)
        else:
            print(f"Media type '{item.type}' for '{item.title}' is not supported.")

if __name__ == "__main__":
    main()
