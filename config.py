from typing import Dict, Any
import json


class ServerConfig:
    def __init__(self, host: str, http_port: int, ws_port: int):
        self.host = host
        self.http_port = http_port
        self.ws_port = ws_port


class VideoConfig:
    def __init__(self, resolution_x: int, resolution_y: int, iso: int, frame_rate: int, exposure_mode: str):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.iso = iso
        self.frame_rate = frame_rate
        self.exposure_mode = exposure_mode


class PhotoConfig:
    def __init__(self, resolution_x: int, resolution_y: int, iso: int, shutter_speed_sec: float, exposure_mode: str):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.iso = iso
        self.shutter_speed_sec = shutter_speed_sec
        self.exposure_mode = exposure_mode


class ConfigManager:
    def __init__(self, path: str):
        self.path = path
        with open(path, "r") as f:
            self.config = json.load(f)

    def get_dict(self) -> Dict:
        return self.config

    def get_val(self, key: str):
        return self.config[key]

    def set_val(self, key: str, val: Any):
        self.config[key] = val
        with open(self.path, "w") as f:
            config_str = json.dumps(self.config, indent=4)
            f.write(config_str)

    def set_vals(self, vals: Dict):
        for key, val in vals.items():
            self.config[key] = val
        with open(self.path, "w") as f:
            config_str = json.dumps(self.config, indent=4)
            f.write(config_str)
