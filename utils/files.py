import json


def load_json(filepath):
    with open(filepath, "r") as file:
        return json.load(file)


def read_txt(file_path):
    with open(file_path, 'r') as file:
        return [row.strip() for row in file]
