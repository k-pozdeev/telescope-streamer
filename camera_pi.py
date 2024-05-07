from picamera import PiCamera
from camera_base import CameraBase
from broadcast import VideoStreamConsumerInterface
from config import CameraConfig, PhotoConfig
from time import sleep
from fractions import Fraction
from threading import Thread, Lock


class Camera(CameraBase):
    def __init__(self, camera_config: CameraConfig, consumer: VideoStreamConsumerInterface):
        super().__init__(camera_config, consumer)
        self._camera_config = camera_config
        self._camera = self._init_camera()
        self._consumer = consumer
        self._lock = Lock()
        # warm-up
        sleep(1)

    def _init_camera(self) -> PiCamera:
        camera: PiCamera = PiCamera(sensor_mode=0)
        camera.resolution = (self._camera_config.resolution_x, self._camera_config.resolution_y)
        camera.framerate = self._camera_config.frame_rate
        return camera

    def start_stream(self):
        self._camera.start_recording(self._consumer, 'yuv')

    def stop_stream(self):
        self._camera.stop_recording()

    def wait_recording(self):
        # lock нужен, потому что в другом потоке может быть вызван make_photo, уничтожающий камеру.
        # При этом упадет с ошибкой метод wait_recording()
        self._lock.acquire(True)
        self._camera.wait_recording(1)
        sleep(1)
        self._lock.release()

    def make_photo(self, photo_config: PhotoConfig, path: str):
        self._lock.acquire(True)
        self._camera.stop_recording()
        self._camera.close()
        tmpcamera = PiCamera(sensor_mode=3)
        tmpcamera.resolution = (photo_config.resolution_x, photo_config.resolution_y)
        framerate = 1.0 / photo_config.shutter_speed_sec
        tmpcamera.framerate = Fraction.from_float(max(framerate, 30.0))
        tmpcamera.shutter_speed = photo_config.shutter_speed_sec * 1_000_000
        tmpcamera.iso = photo_config.iso
        # warm-up
        if photo_config.shutter_speed_sec < 1.0:
            sleep(1)
        else:
            sleep(3)
        tmpcamera.capture(path, format='jpeg')
        tmpcamera.close()
        self._camera = self._init_camera()
        self._camera.start_recording(self._consumer, 'yuv')
        self._lock.release()

    def destroy(self):
        if self._camera.recording:
            self._camera.stop_recording()
        if not self._camera.closed:
            self._camera.close()
