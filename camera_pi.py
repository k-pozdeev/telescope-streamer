from picamera import PiCamera
from camera_base import CameraBase
from broadcast import VideoStreamConsumerInterface
from config import VideoConfig, PhotoConfig
from time import sleep, time
from fractions import Fraction
from threading import Thread, Lock
from typing import Dict, Any


def fabric(video_config: VideoConfig, consumer: VideoStreamConsumerInterface) -> CameraBase:
    if video_config.mode == 'video_stream':
        return Camera(video_config, consumer)
    elif video_config.mode == 'photo_stream':
        return PhotoStreamCamera(video_config, consumer)


class Camera(CameraBase):
    def __init__(self, video_config: VideoConfig, consumer: VideoStreamConsumerInterface):
        super().__init__(video_config, consumer)
        self._video_config = video_config
        self._camera = self._init_camera()
        self._consumer = consumer
        self._lock = Lock()
        # warm-up
        sleep(1)

    def _init_camera(self) -> PiCamera:
        camera: PiCamera = PiCamera(sensor_mode=0)
        camera.resolution = (self._video_config.resolution_x, self._video_config.resolution_y)
        camera.framerate = self._video_config.frame_rate
        camera.exposure_mode = self._video_config.exposure_mode
        camera.iso = self._video_config.iso
        camera.shutter_speed = int(self._video_config.shutter_speed_sec * 1_000_000)
        camera.image_denoise = False
        return camera

    def start_stream(self):
        self._camera.start_recording(self._consumer, 'h264')

    def stop_stream(self):
        self._camera.stop_recording()

    def wait_recording(self):
        # lock нужен, потому что в другом потоке может быть вызван make_photo, уничтожающий камеру.
        # При этом упадет с ошибкой метод wait_recording()
        # self._lock.acquire(True)
        # self._camera.wait_recording(1)
        sleep(1)
        # self._lock.release()

    def change_video_settings(self, settings: Dict[str, Any]):
        self._lock.acquire(True)
        self._camera.iso = settings["iso"]
        self._camera.exposure_mode = settings["exposure_mode"]
        self._lock.release()

    def make_photo(self, photo_config: PhotoConfig, path: str):
        self._lock.acquire(True)
        self._camera.stop_recording()
        self._camera.close()
        tmpcamera = PiCamera(sensor_mode=3)
        tmpcamera.resolution = (photo_config.resolution_x, photo_config.resolution_y)
        tmpcamera.framerate = Fraction.from_float(min(1.0 / photo_config.shutter_speed_sec, 30.0))
        tmpcamera.shutter_speed = int(photo_config.shutter_speed_sec * 1_000_000)
        tmpcamera.iso = photo_config.iso
        tmpcamera.exposure_mode = photo_config.exposure_mode
        # warm-up
        # if photo_config.shutter_speed_sec < 1.0:
        #     sleep(1)
        # else:
        #     sleep(3)
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


class PhotoStreamCamera(CameraBase):
    def __init__(self, video_config: VideoConfig, consumer: VideoStreamConsumerInterface):
        super().__init__(video_config, consumer)
        self._video_config = video_config
        self._camera = None
        self._init_camera()
        self._consumer = consumer
        self._lock = Lock()
        self._streaming_thread = None
        self._need_stop_streaming = False
        # warm-up
        sleep(1)

    def _init_camera(self):
        camera: PiCamera = PiCamera(sensor_mode=0)
        camera.resolution = (self._video_config.resolution_x, self._video_config.resolution_y)
        camera.framerate = self._video_config.frame_rate
        camera.exposure_mode = self._video_config.exposure_mode
        camera.iso = self._video_config.iso
        camera.shutter_speed = int(self._video_config.shutter_speed_sec * 1_000_000)
        camera.image_denoise = False
        self._camera = camera

    def start_stream(self):
        self._streaming_thread = Thread(target=self._run_streaming_thread)
        self._streaming_thread.start()

    def stop_stream(self):
        self._need_stop_streaming = True
        self._streaming_thread.join()

    def wait_recording(self):
        sleep(0.1)

    def change_video_settings(self, settings: Dict[str, Any]):
        self._lock.acquire(True)
        self._camera.iso = settings["iso"]
        self._camera.exposure_mode = settings["exposure_mode"]
        self._lock.release()

    def make_photo(self, photo_config: PhotoConfig, path: str):
        self._lock.acquire(True)
        self.stop_stream()
        self._camera.close()
        tmpcamera = PiCamera(sensor_mode=3)
        tmpcamera.resolution = (photo_config.resolution_x, photo_config.resolution_y)
        tmpcamera.framerate = Fraction.from_float(min(1.0 / photo_config.shutter_speed_sec, 30.0))
        tmpcamera.shutter_speed = int(photo_config.shutter_speed_sec * 1_000_000)
        tmpcamera.iso = photo_config.iso
        tmpcamera.exposure_mode = photo_config.exposure_mode
        # warm-up
        if photo_config.shutter_speed_sec < 1.0:
            sleep(1)
        else:
            sleep(3)
        tmpcamera.capture(path, format='jpeg')
        tmpcamera.close()
        self._init_camera()
        self.start_stream()
        self._lock.release()

    def destroy(self):
        if not self._camera.closed:
            self._camera.close()

    def _run_streaming_thread(self):
        frame_duration_sec = float(1.0 / self._video_config.frame_rate)
        while True:
            before_time = time()
            self._camera.capture(self._consumer, format='rgba', use_video_port=False)
            after_time = time()
            actual_frame_duration_sec = after_time - before_time
            if actual_frame_duration_sec < frame_duration_sec:
                sleep(actual_frame_duration_sec - frame_duration_sec)
            if self._need_stop_streaming:
                break
