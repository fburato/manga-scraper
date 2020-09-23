from common import *
import sys


def main(chapter_url: str, directory: str):
    chapter = process_chapter(chapter_url)
    download_chapters([chapter], directory)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Provide chapter url and destination directory")
    chapter_url = sys.argv[1]
    destination = sys.argv[2]
    logger.info(f"Chapter url provided={chapter_url}, destination={destination}")
    main(chapter_url, destination)