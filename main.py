from config import ServerConfig, VideoConfig, ConfigManager
from server import make_http_server, make_websocket_server
from threading import Thread
from broadcast import WebsocketBroadcaster, FfmpegConverter
from photoman import PhotoManager
from time import sleep

config_manager = ConfigManager("config.json")
config_dict = config_manager.get_dict()

photo_man = PhotoManager("./photo")
server_config = ServerConfig(
    config_dict["server_host"],
    config_dict["server_http_port"],
    config_dict["server_ws_port"]
)
video_config = VideoConfig(
    config_dict["camera_video_resolution_x"],
    config_dict["camera_video_resolution_y"],
    config_dict["camera_video_iso"],
    config_dict["camera_video_frame_rate"],
    config_dict["camera_video_exposure_mode"],
    config_dict["camera_video_shutter_speed_sec"],
    config_dict["camera_video_mode"]
)

# PiCamera нельзя установить на десктоп, поэтому на десктопе импортируем заглушку
try:
    from camera_pi import fabric
except ImportError:
    from camera_fake import fabric

ffmpeg_converter = FfmpegConverter(video_config)
camera = fabric(video_config, ffmpeg_converter)

print('Initializing HTTP server')
http_server = make_http_server(config_manager, server_config, video_config, camera, photo_man)
http_thread = Thread(target=http_server.serve_forever)

websocket_server = make_websocket_server(server_config, video_config)
websocket_thread = Thread(target=websocket_server.serve_forever)

websocket_broadcaster = WebsocketBroadcaster(ffmpeg_converter, websocket_server)

try:
    camera.start_stream()
    print('Starting websockets thread')
    websocket_thread.start()
    print('Starting HTTP server')
    http_thread.start()
    print('Starting broadcast thread')
    websocket_broadcaster.start()
    while True:
        camera.wait_recording()
except KeyboardInterrupt:
    pass
finally:
    print('Stopping recording')
    camera.stop_stream()
    camera.destroy()
    print('Stopping ffmpeg conversion')
    ffmpeg_converter.stop()
    print('Waiting for broadcast thread to finish')
    websocket_broadcaster.stop_broadcast()
    websocket_broadcaster.join()
    print('Shutting down HTTP server')
    http_server.shutdown()
    print('Waiting for HTTP server thread to finish')
    http_thread.join()
    print('Shutting down websockets server')
    websocket_server.manager.close_all()
    websocket_server.manager.stop()
    websocket_server.shutdown()
    print('Waiting for websockets thread to finish')
    websocket_thread.join()
