import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from write_art import apply_to_dir


def debug_log(log: str):
    print(f"[DEBUG] {log}", file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(description="Get album art via spotify")
    parser.add_argument("dirs", nargs="+", help="Album directories")
    parser.add_argument("--separator", "-s", default=" - ", help="Field separtor")
    parser.add_argument(
        "--dry_run",
        "-d",
        action="store_true",
        help="Run without write image data in music file",
    )
    parser.add_argument("--limits", default=20, help="Limits at one fecth")
    parser.add_argument("--debug", action="store_true", help="Run with debug info")
    return parser.parse_args()


@dataclass
class SpotifyToken:
    id: str
    secret: str

    def __init__(self):
        self.id = os.environ["CLIENT_ID"]
        self.secret = os.environ["CLIENT_SECRET"]


def fetch(album_name: str, spotify: spotipy.Spotify, limit=20):
    return spotify.search(
        q=album_name,
        limit=limit,
        type="album",
        market="JP",
    )


def get_album_art(album_name: str, spotify: spotipy.Spotify, limit=20, debug=False):
    if debug:
        debug_log(f"Albun: {album_name}")

    album_infos = fetch(album_name, spotify, limit)
    n_albums = len(album_infos["albums"]["items"])
    if n_albums == 0:
        print(f"{album_name} matchs any one.")
        return None
    print(f"{album_name} matchs {n_albums}.")

    selected = select(album_infos["albums"]["items"])
    if selected is None:
        return None

    url = selected["images"][0]["url"]
    image = requests.get(url).content
    return image


# T[] => T
def select(items: list):
    n_items = len(items)
    if n_items == 1:
        return items[0]
    inputed = "s"
    while all(map(lambda i: inputed != str(i + 1), range(0, n_items))):
        if inputed == "N":
            return None
        if inputed == "s":
            for i, name in enumerate([item["name"] for item in items], start=1):
                print(f"{i}: {name}")
        inputed = input("Which one? [show list again: s, Cancel: N] > ")
    return items[int(inputed) - 1]


if __name__ == "__main__":
    args = parse_args()

    token = SpotifyToken()
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=token.id, client_secret=token.secret
        )
    )

    for d in args.dirs:
        dir = Path(d)
        album_name = dir.name.split(args.separator, maxsplit=1)[1]
        image = get_album_art(album_name, sp, args.limits, args.debug)

        if image is not None:
            with open(dir / "cover.jpg", "wb") as f:
                f.write(image)
        if not args.dry_run:
            apply_to_dir(dir)
        os.system("clear")
