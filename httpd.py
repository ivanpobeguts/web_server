import os
import re
import time
import socket
import logging
import argparse
import mimetypes
from pathlib import Path
from urllib.parse import unquote
from collections import namedtuple
from multiprocessing.pool import ThreadPool

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname).1s %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)

Status = namedtuple('Status', 'code, message')


class WebServer:
    OK = Status(200, 'OK')
    FORBIDDEN = Status(403, 'Forbidden')
    NOT_FOUND = Status(404, 'Not Found')
    NOT_ALLOWED = Status(405, 'Method Not Allowed')

    def __init__(self, host, port, workers_num, path):
        self.host = host
        self.port = port
        self.workers_num = workers_num
        self.path = path

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    def get_mime_type(self, path):
        try:
            ext = re.compile(r'^.*(?P<ext>\.(html|css|js|jpeg|jpg|png|gif|swf|txt))$').match(path).group('ext')
            return mimetypes.types_map[ext]
        except AttributeError:
            logger.info(f'Extension of {path} is not allowed')
            return

    def read_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return

    def generate_main_headers(self, status, content_type='', content_len=0):
        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        http_header = f'HTTP/1.1 {status.code} {status.message}'
        date_header = 'Date: {now}'.format(now=time_now)
        server_header = 'Server: Python-WebServer'
        connection_header = 'Connection: close'
        type_header = f'Content-Type: {content_type}'
        len_header = f'Content-Length: {content_len}\r\n\r\n'

        return '\r\n'.join([http_header, date_header, server_header, connection_header, type_header, len_header])

    def handle_request(self, client_socket):
        buf_size = 1024
        raw_request = b''
        try:
            while True:
                chunk = client_socket.recv(buf_size)
                if chunk:
                    raw_request += chunk
                    if raw_request.endswith(b'\r\n\r\n') or raw_request.endswith(b'\n\n'):
                        raw_request = raw_request.strip()
                        break
                else:
                    break
            request = re.split(' ', raw_request.decode())
            method = request[0] if request else None
            request_path = ''
            if len(request) > 1:
                request_path = unquote(request[1])
                if '?' in request_path:
                    request_path = request_path[:request_path.index('?')]
                if request_path.endswith('/'):
                    request_path = os.path.join(request_path, 'index.html')

            response_mime_type = self.get_mime_type(request_path)
            file_path = os.path.join(self.path, request_path[1:])
            if not Path(file_path).exists():
                response_status = self.NOT_FOUND
                response = self.generate_main_headers(response_status)
                client_socket.send(response.encode())
                logger.info(f'{method} {request_path} {response_status.code}')
                return
            if not response_mime_type:
                response_status = self.FORBIDDEN
                client_socket.send(self.generate_main_headers(response_status).encode())
                logger.info(f'{method} {request_path} {response_status.code}')
                return

            if method not in ('GET', 'HEAD') or not request:
                response_status = self.NOT_ALLOWED
                client_socket.send(self.generate_main_headers(response_status).encode())
                logger.info(f'{method} {request_path} {response_status.code}')
                return
            if method == 'HEAD':
                response_status = self.OK
                client_socket.send(
                    self.generate_main_headers(response_status, content_len=Path(file_path).stat().st_size).encode())
                logger.info(f'{method} {request_path} {response_status.code}')
                return

            file = self.read_file(file_path)
            if method == 'GET':
                response_status = self.OK
                headers = self.generate_main_headers(response_status, content_type=response_mime_type,
                                                     content_len=len(file)).encode()
                response = b''.join([headers, file])
                client_socket.send(response)
                logger.info(f'{method} {request_path} {response_status.code}')
        except Exception as e:
            logger.exception(e)
        finally:
            client_socket.close()

    def close(self):
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        logger.info('Server has stopped')

    def serve_forever(self):
        pool = ThreadPool(self.workers_num)
        while True:
            try:
                client_socket, addr = self.server.accept()
                pool.map(self.handle_request, (client_socket,))
            except KeyboardInterrupt:
                logger.error("[!] Keyboard Interrupted!")
                self.close()
                break


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        '-s',
        type=str,
        default='0.0.0.0',
        help='Server host',
    )
    parser.add_argument(
        '--port',
        '-p',
        type=int,
        default=9898,
        help='Server port',
    )
    parser.add_argument(
        '--workers',
        '-w',
        type=int,
        default=5,
        help='Number of workers',
    )
    parser.add_argument(
        '--doc_root',
        '-r',
        type=str,
        default='',
        help='Files path',
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    logger.info(f'Starting server on {args.host}:{args.port}..')
    server = WebServer(args.host, args.port, args.workers, args.doc_root)
    server.start()
    logger.info(f'Server has started')
    server.serve_forever()
