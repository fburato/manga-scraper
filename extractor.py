import requests
from requests import Response
from urllib import parse
import bs4
import logging
import functools
import os
import re
from concurrent.futures import ThreadPoolExecutor
import sys
import time
from typing import List, Tuple
from dataclasses import dataclass

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


logger = logging.getLogger("main")

chapter_resolution_workers = 25
image_downloading_workers = 50


@dataclass
class Chapter:
    chapter: str
    directory: str
    images_hrefs: List[str]


def main(index_url: str, start_from: str):
    (manga_name, chapters) = get_chapter_list(index_url)
    resolved_chapters = resolve_chapters(chapters)
    start_index = 0
    for index, chapter in enumerate(resolved_chapters):
        if chapter.chapter == start_from:
            start_index = index
    logger.info(f"Starting download from {resolved_chapters[start_index].chapter}")
    download_chapters(resolved_chapters, manga_name)


def get_chapter_list(index_url: str) -> Tuple[str, List[str]]:
    logger.info(f"Downloading manga index from {index_url}")
    parsed_url = parse.urlparse(index_url)
    components = parsed_url.path.split("/")
    manga_name = components[len(components) - 1]
    index = get_with_retries(index_url)
    logger.info("Parsing index")
    indexparsed = bs4.BeautifulSoup(index.text, features="html.parser")
    chapters = indexparsed.select(".chapter-list > ul > li > div > h4 > a")
    logger.info(f"Identified {len(chapters)} chapters")
    hrefs = functools.reduce(lambda x, y: x + y, map(lambda a: a.get_attribute_list('href'), chapters), [])
    hrefs.reverse()
    return manga_name, hrefs


def get_with_retries(url: str) -> Response:
    success = False
    while not success:
        response = requests.get(url)
        if response.status_code >= 400:
            logger.warning(f"Retrieval of {url} failed with status code {response.status_code}. Sleeping and retrying in 2 seconds")
            time.sleep(2)
        else:
            success = True
    return response


def resolve_chapters(chapter_urls: List[str]) -> List[Chapter]:
    chapter_list = []
    with ThreadPoolExecutor(max_workers=chapter_resolution_workers) as executor:
        futures = []
        logger.info("Starting parallel resolution of chapters")
        for chapter_url in chapter_urls:
            futures.append(executor.submit(process_chapter, chapter_url))
        for index, future in enumerate(futures, start=1):
            chapter: Chapter = future.result()
            logger.info(f"Resolved {len(chapter.images_hrefs)} images for {chapter.chapter}")
            chapter_list.append(Chapter(chapter=chapter.chapter, directory=str(index).rjust(3, '0') + "-" + chapter.directory, images_hrefs=chapter.images_hrefs))
    return chapter_list


def process_chapter(chapter_url: str) -> Chapter:
    parsed_url = parse.urlparse(chapter_url)
    chapter_name = parsed_url.path.replace("/", "")
    logger.info(f"Downloading {chapter_name} from {chapter_url}")
    page = get_with_retries(chapter_url)
    parsed_page = bs4.BeautifulSoup(page.text, features="html.parser")
    elements = parsed_page.select("#arraydata")
    if len(elements) > 0:
        images = list(map(lambda s: s.strip(), elements[0].getText().split(",")))
    else:
        images = []
    return Chapter(chapter=chapter_name, images_hrefs=images, directory=chapter_name)


def download_chapters(chapter_hrefs: List[Chapter], base_directory: str):
    processing_list = []
    for chapter in chapter_hrefs:
        target = os.path.join(base_directory, chapter.directory)
        logger.info(f"Making directory {target}")
        os.makedirs(target, exist_ok=True)
        for index, image in enumerate(chapter.images_hrefs, start=1):
            logger.debug(f"Processing {image}")
            parsed = parse.urlparse(image)
            safe_url = parse.ParseResult(scheme=parsed.scheme if parsed.scheme else "http", netloc=parsed.netloc,
                                         path=parsed.path, params=parsed.params, query=parsed.query,
                                         fragment=parsed.fragment)
            match = re.search("^.*(?P<extension>\\.[a-zA-Z]+)$", parsed.path.strip())
            extension = match.group("extension") if match else ""
            filepath = os.path.join(base_directory, chapter.directory, str(index).rjust(3, '0') + extension)
            processing_list.append((filepath, safe_url.geturl(), index))
    with ThreadPoolExecutor(max_workers=image_downloading_workers) as executor:
        futures = []
        for (filepath, url, index) in processing_list:
            futures.append(executor.submit(download_image, filepath, url, index))
        for future in futures:
            future.result()


def download_image(filepath: str, url: str, index: int):
    if not os.path.exists(filepath):
        with open(filepath, 'wb') as file:
            logger.info(f"Downloading image {index}")
            image_content = get_with_retries(url)
            file.write(image_content.content)
    else:
        logger.info("Skipping already existing file")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Provide index url")
    index_url = sys.argv[1]
    start_chapter = sys.argv[2] if len(sys.argv) >= 3 else ""
    logger.info(f"Index provided={index_url}, start_chapter={start_chapter}")
    main(index_url, start_chapter)
