import os
from typing import List


class PhotoManager:
    """
    Абстракция над папкой для сохранения фотографий:
    - выдает список фотографий
    - выдает контент фотографии по имени
    - сохраняет новую фотографию в папку
    """
    def __init__(self, photo_folder: str):
        self._photo_folder = os.path.abspath(photo_folder)
        if not os.path.exists(photo_folder):
            os.mkdir(photo_folder)

    def list_photos(self) -> List[str]:
        for (root, dirs, files) in os.walk(self._photo_folder, topdown=True):
            files = [file for file in files if file != ".gitkeep"]
            return sorted(files, reverse=True)

    def full_path(self, name: str) -> str:
        return os.path.join(self._photo_folder, name)

    def save_photo(self, body, name):
        abs_path = os.path.join(self._photo_folder, name)
        with open(abs_path, "wb") as f:
            f.write(body)

    def get_photo_as_bytes(self, name) -> bytes:
        abs_path = os.path.join(self._photo_folder, name)
        with open(abs_path, "rb") as f:
            return f.read()

    def get_photo_as_resource(self, name):
        abs_path = os.path.join(self._photo_folder, name)
        return open(abs_path, "rb")
