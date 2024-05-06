from fractions import Fraction


class ServerConfig:
    def __init__(self, host: str, http_port: int, ws_port: int):
        self.host = host
        self.http_port = http_port
        self.ws_port = ws_port


class CameraConfig:
    def __init__(self, resolution_x: int, resolution_y: int, frame_rate: int):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.frame_rate = frame_rate


class PhotoConfig:
    def __init__(self, resolution_x: int, resolution_y: int, iso: int, shutter_speed_sec: float):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.iso = iso
        self.shutter_speed_sec = shutter_speed_sec
