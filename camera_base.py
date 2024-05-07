from config import CameraConfig, PhotoConfig
from broadcast import VideoStreamConsumerInterface


class CameraBase(object):
    """Интерфейс обертки камеры Raspberry PI"""
    def __init__(self, camera_config: CameraConfig, consumer: VideoStreamConsumerInterface):
        pass

    def start_stream(self):
        pass

    def stop_stream(self):
        pass

    def wait_recording(self):
        pass

    def make_photo(self, photo_config: PhotoConfig, path: str):
        pass

    def destroy(self):
        pass
