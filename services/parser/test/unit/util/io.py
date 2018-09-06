import os


def read_local_file(*path) -> str:
    """read file from data folder"""
    folder = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(folder, '..', 'data', *path)) as file:
        text = file.read()

    return text
