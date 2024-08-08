from config import VideoConfig, PhotoConfig
from broadcast import VideoStreamConsumerInterface
from typing import Dict, Any


class CameraBase(object):
    """Интерфейс обертки камеры Raspberry PI"""
    def __init__(self, video_config: VideoConfig, consumer: VideoStreamConsumerInterface):
        pass

    def start_stream(self):
        pass

    def stop_stream(self):
        pass

    def wait_recording(self):
        pass

    def change_video_settings(self, settings: Dict[str, Any]):
        pass

    def make_photo(self, photo_config: PhotoConfig, path: str):
        pass

    def destroy(self):
        pass
