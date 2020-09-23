import requests
from requests import Response
from urllib import parse
import bs4
from typing import List
from dataclasses import dataclass
import logging
import time
import os
import re
from concurrent.futures import ThreadPoolExecutor


image_downloading_workers = 50


logger = logging.getLogger("main")


@dataclass
class Chapter:
    chapter: str
    directory: str
    images_hrefs: List[str]


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
