import argparse
import mimetypes
import sys
from pathlib import Path

import mutagen
from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(
        description="Write album art that include dir as `cover.jpg` into music file"
    )
    parser.add_argument("dirs", nargs="+", help="Album directories")
    parser.add_argument("--debug", action="store_true", help="Run with debug info")
    return parser.parse_args()


def store_to_music(music_path, image_path):
    music = mutagen.File(music_path)
    music.clear_pictures()
    p = mutagen.flac.Picture()
    image = Image.open(image_path)
    with open(image_path, "rb") as f:
        p.data = f.read()
    p.mime = mimetypes.guess_type(image_path)[0]
    p.width = image.width
    p.height = image.height
    p.depth = image.bits * image.layers
    music.add_picture(p)
    music.save()


def apply_to_dir(dir_path):
    dir = Path(dir_path)
    image = dir / "cover.jpg"
    if image.exists():
        for file in filter(lambda f: f.suffix.lstrip(".") == "flac", dir.iterdir()):
            store_to_music(file, image)


def debug_log(log):
    print(f"[debug] {log}", file=sys.stderr)


if __name__ == "__main__":
    args = parse_args()
    for dir in args.dirs:
        if args.debug:
            debug_log(dir)
        apply_to_dir(dir)
