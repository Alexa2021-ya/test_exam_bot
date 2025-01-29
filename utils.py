import os
import urllib.request
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_directory(dir_name: str):
    main_directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(main_directory, dir_name)
    os.makedirs(path, exist_ok=True)
    logging.info(f'Создана директория: {path}')


def generate_image_name(image_id: int):
    return f'task_image_id_{image_id}.png'


def extract_id_from_url(url):
    pattern = r'/d/([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)

    if match:
        return match.group(1)

    return None


def generate_url_for_download(image_url: str) -> str:
    image_key = extract_id_from_url(image_url)
    image_download_url = f'https://drive.google.com/uc?id={image_key}&export=download'
    return image_download_url


def save_image(url: str, image_id: int, path: str) -> str:
    create_directory(path)

    image_url = generate_url_for_download(url)
    file_name = generate_image_name(image_id)
    file_path = os.path.join(path, file_name)

    logo = urllib.request.urlopen(image_url).read()
    f = open(file_path, "wb")
    f.write(logo)
    f.close()

    return file_path