import argparse
from pathlib import Path

import mutagen


def parse_args():
    parser = argparse.ArgumentParser(description="Restore music info by path")
    parser.add_argument("files", nargs="+", help="Music files")
    parser.add_argument("--separator", "-s", default=" - ", help="Field separtor")
    parser.add_argument(
        "--dry_run", "-d", action="store_true", help="Run without write file"
    )
    parser.add_argument("--debug", action="store_true", help="Run with debug info")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    for f in args.files:
        filename = Path(f)
        if not filename.is_file():
            continue
        track, artist, title, *etc = filename.stem.split(args.separator)
        album_artist, album_name = filename.parent.name.split(args.separator)
        if args.debug:
            fields = {
                "track": track,
                "artist": artist,
                "title": title,
                "etc": etc,
                "album_artist": album_artist,
                "album_name": album_name,
            }
            print(f"[DEBUG] Fields: {fields}")
        if etc:
            title = title + args.separator + args.separator.join(etc)
            if args.debug:
                print(f"[DEBUG] music title include {args.separtor} ? : {title}")

        album = mutagen.File(filename)
        album["album"] = [album_name]
        album["albumartist"] = [album_artist]
        album["artist"] = [artist]
        album["title"] = [title]
        if args.dry_run:
            print(f"[DRY RUN] === {filename.name} ===")
            print(f"[DRY RUN] Write {album}")
        else:
            album.save()
