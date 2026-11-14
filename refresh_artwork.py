"""
Refreshes artwork for movies, shows and seasons
This includes posters, backgrounds, logos, and square art
"""

import helpers


def set_artwork(item):
    resources = (
        ("poster", item.posters, item.setPoster, item.unlockPoster),
        ("background", item.arts, item.setArt, item.unlockArt),
        ("logo", item.logos, item.setLogo, item.unlockLogo),
        ("square art", item.squareArts, item.setSquareArt, item.unlockSquareArt),
    )
    for name, get_resources, set_resource, unlock_resource in resources:
        available = get_resources()
        if available:
            if not available[0].selected:
                set_resource(available[0])
                print(f"Refreshed {name} for '{item.title}'")
            unlock_resource()


def main():
    plex_server = helpers.get_plex_server()

    for item in helpers.get_media(plex_server):
        if item.type == "movie":
            set_artwork(item)
        elif item.type == "show":
            for season in item.seasons():
                set_artwork(season)

            set_artwork(item)
        else:
            print(f"Media type '{item.type}' for '{item.title}' is not supported.")


if __name__ == "__main__":
    main()
