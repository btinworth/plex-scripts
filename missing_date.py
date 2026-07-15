"""
This script prints all Plex items without an originallyAvailableAt date
Anything that is missing this date will be skipped when running the date_added.py script
"""

import helpers


def main():
    plex_server = helpers.get_plex_server()

    items = []
    for library in helpers.get_libraries(plex_server):
        items.extend(library.all())

    missing = []
    for item in items:
        if item.type == "movie" and not item.originallyAvailableAt:
            missing.append(f"Missing originallyAvailableAt date for movie: {item.title}")

        if item.type == "show":
            show = item
            for episode in show.episodes():
                if not episode.originallyAvailableAt:
                    missing.append(f"Missing originallyAvailableAt date for episode: {show.title} (S{episode.parentIndex:02}E{episode.index:02}) - {episode.title}")

    if missing:
        print(f"Found {len(missing)} items missing originallyAvailableAt date:")
        for entry in missing:
            print(entry)
    else:
        print("No items missing originallyAvailableAt date found.")

if __name__ == "__main__":
    main()
