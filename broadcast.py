import io
from subprocess import Popen, PIPE
from config import CameraConfig
from typing import Union
from threading import Thread, Event
from time import sleep
from ws4py.server.wsgirefserver import WSGIServer


class VideoStreamConsumerInterface:
    def write(self, b: Union[bytes, None]):
        pass


class VideoStreamSourceInterface:
    def read(self) -> Union[bytes, None]:
        pass


class StoppableInterface:
    def stop(self):
        pass


class FfmpegConverter(VideoStreamConsumerInterface, VideoStreamSourceInterface, StoppableInterface):
    def __init__(self, camera_config: CameraConfig):
        print('Spawning background conversion process')
        self.converter = Popen([
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % (camera_config.resolution_x, camera_config.resolution_y),
            '-r', str(camera_config.frame_rate),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b:v', '800k',
            '-r', str(camera_config.frame_rate),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open('ffmpeg.err.log', 'wb'),
            shell=False, close_fds=True)
        # warm-up
        sleep(1)

    def write(self, b: Union[bytes, None]):
        if b is not None:
            self.converter.stdin.write(b)

    def read(self) -> Union[bytes, None]:
        buf = self.converter.stdout.read1(32768)
        if buf:
            return buf
        elif self.converter.poll() is not None:
            return None
        else:
            return None

    def stop(self):
        print('Waiting for background conversion process to exit')
        self.converter.stdin.close()
        self.converter.wait()


class WebsocketBroadcaster(Thread):
    def __init__(self, video_stream_source: VideoStreamSourceInterface, websocket_server: WSGIServer):
        super(WebsocketBroadcaster, self).__init__()
        self.video_stream_source = video_stream_source
        self.websocket_server = websocket_server
        self._stop_broadcast = False

    def run(self):
        while not self._stop_broadcast:
            buf = self.video_stream_source.read()
            if buf is not None:
                self.websocket_server.manager.broadcast(buf, binary=True)
            else:
                sleep(0.1)

    def stop_broadcast(self):
        self._stop_broadcast = True
