import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_directory(path: str):
    os.makedirs(path, exist_ok=True)
    logging.info(f'Создана директория: {path}')


def generate_image_name(image_id: int):
    return f'task_image_id_{image_id}.png'


def save_image(image_key: str, image_id: int, path: str) -> str:
    create_directory(path)


    image_url = f'https://drive.google.com/uc?id={image_key}&export=download'
    file_name = generate_image_name(image_id)
    file_path = os.path.join(path, file_name)

    logo = urllib.request.urlopen(image_url).read()
    f = open(file_path, "wb")
    f.write(logo)
    f.close()

    return file_path