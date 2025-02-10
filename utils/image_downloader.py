import os
import aiohttp
import asyncio
import logging
import re
from utils.create_directory import create_directory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_image_name_for_task_image(image_id: int):
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

async def save_image(url: str, image_id: int, path: str) -> str:
    create_directory(path)

    image_url = generate_url_for_download(url)
    file_name = generate_image_name_for_task_image(image_id)
    file_path = os.path.join(path, file_name)

    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                with open(file_path, "wb") as f:
                    f.write(await response.read())
            else:
                logging.error(f"Failed to download image: {response.status}")

    return file_path