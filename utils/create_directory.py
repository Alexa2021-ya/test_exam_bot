import os
import json


def create_directory(dir_name: str):
    main_directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(main_directory, dir_name)
    os.makedirs(path, exist_ok=True)


def load_config(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)
