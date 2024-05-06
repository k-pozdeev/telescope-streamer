from config import ServerConfig, CameraConfig
from server import make_http_server, make_websocket_server
from threading import Thread
from broadcast import WebsocketBroadcaster, FfmpegConverter
from photoman import PhotoManager
from time import sleep


# PiCamera нельзя установить на десктоп, поэтому на десктопе импортируем заглушку
try:
    from picamera import PiCamera
    from camera_pi import Camera
except ImportError:
    from camera_fake import Camera

photo_man = PhotoManager("./photo")
server_config = ServerConfig("0.0.0.0", 8082, 8084)
camera_config = CameraConfig(640, 480, 30)
ffmpeg_converter = FfmpegConverter(camera_config)
camera = Camera(camera_config, ffmpeg_converter)

print('Initializing HTTP server')
http_server = make_http_server(server_config, camera_config, camera, photo_man)
http_thread = Thread(target=http_server.serve_forever)

websocket_server = make_websocket_server(server_config, camera_config)
websocket_server.initialize_websockets_manager()
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
        sleep(0.1)
        #camera.wait_recording()
except KeyboardInterrupt:
    pass
finally:
    print('Stopping recording')
    camera.stop_stream()
    ffmpeg_converter.stop()
    print('Shutting down websockets server')
    websocket_server.shutdown()
    print('Waiting for broadcast thread to finish')
    websocket_broadcaster.stop_broadcast()
    websocket_broadcaster.join()
    print('Shutting down HTTP server')
    http_server.shutdown()
    print('Waiting for websockets thread to finish')
    websocket_thread.join()
    print('Waiting for HTTP server thread to finish')
    http_thread.join()
