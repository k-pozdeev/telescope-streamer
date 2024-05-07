import io
import numpy as np
import yuvio
from broadcast import VideoStreamConsumerInterface
from config import CameraConfig, PhotoConfig
from fractions import Fraction
from threading import Thread, Lock, Event
from PIL import Image
from random import randrange
from camera_base import CameraBase
from time import sleep


class Camera(CameraBase):
    def __init__(self, camera_config: CameraConfig, consumer: VideoStreamConsumerInterface):
        super().__init__(camera_config, consumer)
        self._camera_config = camera_config
        self._consumer = consumer
        self._fake_camera_thread = self._init_fake_camera()
        self._fake_camera_interrupt_flag = False
        self._lock = Lock()

    def _init_fake_camera(self) -> Thread:
        fake_camera = Thread(target=self._generate_yuv_stream)
        return fake_camera

    def start_stream(self):
        self._fake_camera_interrupt_flag = False
        self._fake_camera_thread.start()

    def stop_stream(self):
        self._fake_camera_interrupt_flag = True
        self._fake_camera_thread.join()

    def wait_recording(self):
        self._lock.acquire(True)
        sleep(1)
        self._lock.release()

    def make_photo(self, photo_config: PhotoConfig, path: str):
        self._lock.acquire(True)
        self.stop_stream()
        self._fake_camera_thread = None

        image = Image.new("RGB", (photo_config.resolution_x, photo_config.resolution_y), (125, 128, 99))
        image.save(path, "jpeg")

        self._fake_camera_thread = self._init_fake_camera()
        self.start_stream()
        self._lock.release()

    def destroy(self):
        if self._fake_camera_thread is not None:
            if self._fake_camera_thread.is_alive():
                self._fake_camera_interrupt_flag = True
                self._fake_camera_thread.join()
                self._fake_camera_thread = None
        if self._lock.locked():
            self._lock.release()

    def _generate_yuv_stream(self):
        width = self._camera_config.resolution_x
        height = self._camera_config.resolution_y
        while True:
            y = randrange(255) * np.ones((width, height), dtype=np.uint8)
            u = randrange(255) * np.ones((width // 2, height // 2), dtype=np.uint8)
            v = randrange(255) * np.ones((width // 2, height // 2), dtype=np.uint8)
            frame_420 = yuvio.frame((y, u, v), "yuv420p")
            buff = io.BytesIO()
            yuvio.imwrite(buff, frame_420)
            buff.seek(0)

            self._consumer.write(buff.read1())
            Event().wait(3.0)  # sleep 3 sec
            if self._fake_camera_interrupt_flag:
                break
