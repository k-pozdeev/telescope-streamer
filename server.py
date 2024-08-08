from config import ServerConfig, CameraConfig, PhotoConfig
from photoman import PhotoManager
from camera_base import CameraBase
from http.server import HTTPServer, BaseHTTPRequestHandler
from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import (
    WSGIServer,
    WebSocketWSGIHandler,
    WebSocketWSGIRequestHandler,
)
from ws4py.server.wsgiutils import WebSocketWSGIApplication
import io
import os
from struct import Struct
from string import Template
from time import sleep, time
import datetime
import json
import re

###########################################
# CONFIGURATION
COLOR = u'#444'
BGCOLOR = u'#333'


###########################################


def read_resource(name: str) -> str:
    with open("./res/" + name) as f:
        return f.read()


class StreamingHttpHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        server_config: ServerConfig = self.server.server_config
        camera_config: CameraConfig = self.server.camera_config
        camera: CameraBase = self.server.camera
        photo_man: PhotoManager = self.server.photo_man
        content: bytes = b''

        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        elif m := re.match(r'^/([a-z0-9]+\.(html|css|js))$', self.path):
            file_name = m.group(1)
            file_ext = m.group(2)
            content_type = {
                "html": "text/html",
                "css": "text/css",
                "js": "application/javascript"
            }[file_ext] + "; charset=utf-8"
            content = read_resource(file_name).encode('UTF-8')
        elif self.path == '/photos':
            content_type = 'application/json; charset=utf-8'
            content = json.dumps(photo_man.list_photos()).encode('UTF-8')
        elif self.path.startswith('/photo/'):
            photo_name = self.path.replace('/photo/', '')
            content = photo_man.get_photo_as_bytes(photo_name)
            content_type = "image/jpeg"
        else:
            self.send_error(404, 'File not found')
            return
        if isinstance(content, str):
            raise Exception('Content must be bytes')
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Last-Modified', self.date_time_string(int(time())))
        self.end_headers()
        if self.command == 'GET':
            self.wfile.write(content)

    def do_POST(self):
        camera: CameraBase = self.server.camera
        photo_man: PhotoManager = self.server.photo_man
        content: bytes = b''
        content_type = 'application/json; charset=utf-8'

        if self.path == '/make_photo':
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body)
            photo_config = PhotoConfig(data['width'], data['height'], data['iso'], data['shutter_speed_sec'])
            photo_name = f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S.jpg}"
            camera.make_photo(photo_config, photo_man.full_path(photo_name))
            content = json.dumps({"name": photo_name}).encode('UTF-8')
        elif self.path == '/video_settings':
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body)
            iso = data["iso"]
            camera.change_video_settings({"iso": iso})
            content = json.dumps({"status": "ok"}).encode('UTF-8')

        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        if self.command == 'POST':
            self.wfile.write(content)


class StreamingWebSocket(WebSocket):
    jsmpeg_magic = b'jsmp'
    jsmpeg_header = Struct('>4sHH')
    width = None
    height = None

    def opened(self):
        self.send(self.jsmpeg_header.pack(self.jsmpeg_magic, self.width, self.height), binary=True)


def make_http_server(server_config: ServerConfig, camera_config: CameraConfig, camera, photo_man) -> HTTPServer:
    server = HTTPServer((server_config.host, server_config.http_port), StreamingHttpHandler)
    # for handler
    server.server_config = server_config
    server.camera_config = camera_config
    server.camera = camera
    server.photo_man = photo_man
    return server


def make_websocket_server(server_config: ServerConfig, camera_config: CameraConfig) -> WSGIServer:
    print('Initializing websockets server on port %d' % server_config.ws_port)
    StreamingWebSocket.width = camera_config.resolution_x
    StreamingWebSocket.height = camera_config.resolution_y
    WebSocketWSGIHandler.http_version = '1.1'
    websocket_server = make_server(
        '', server_config.ws_port,
        server_class=WSGIServer,
        handler_class=WebSocketWSGIRequestHandler,
        app=WebSocketWSGIApplication(handler_cls=StreamingWebSocket)
    )
    websocket_server.initialize_websockets_manager()
    return websocket_server
