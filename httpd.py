import os
import re
import time
import socket
import logging
import argparse
import threading
from urllib.parse import unquote
from collections import namedtuple

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

    def __init__(self, host, port, con_num, path):
        self.host = host
        self.port = port
        self.con_num = con_num
        self.path = path

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(self.con_num)

    def get_mime_type(self, path):
        try:
            ext = re.compile(r'^.*[.](?P<ext>html|css|js|jpeg|jpg|png|gif|swf|txt)$').match(path).group('ext')
            if ext == 'html':
                return f'text/{ext}'
            if ext == 'css':
                return f'text/{ext}'
            if ext == 'js':
                return 'text/javascript'
            if ext in ('jpeg', 'jpg'):
                return 'image/jpeg'
            if ext in ('png', 'gif'):
                return f'image/{ext}'
            elif ext == 'swf':
                return 'application/x-shockwave-flash'
            if ext == 'txt':
                return 'text/text'
        except AttributeError:
            logger.info(f'Extension of {path} is not allowed')
            return

    def read_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return

    def generate_main_headers(self, status, version='HTTP/1.1', content_type='', content_len=0):
        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        http_header = f'{version} {status.code} {status.message}'
        date_header = 'Date: {now}'.format(now=time_now)
        server_header = 'Server: Python-WebServer'
        connection_header = 'Connection: close'
        type_header = f'Content-type: {content_type}'
        len_header = f'Content-length: {content_len}\n\n'

        return '\n'.join([http_header, date_header, server_header, connection_header, type_header, len_header])

    def handle_request(self, client_socket):
        try:
            raw_request = client_socket.recv(1024)
            request = re.split(' ', raw_request.decode())
            method = request[0] if request else None
            request_path = ''
            if len(request) > 1:
                request_path = unquote(request[1])
                version = re.compile(r'^(.*)\r\n(.*)').match(request[2]).group(1)
                if '?' in request_path:
                    request_path = request_path[:request_path.index('?')]
                if '../' in request_path:
                    request_path = request_path.replace('../', '')
                if request_path.endswith('/'):
                    request_path = os.path.join(request_path, 'index.html')
            response_mime_type = self.get_mime_type(request_path)
            if method not in ('GET', 'HEAD') or not request:
                client_socket.send(self.generate_main_headers(self.NOT_ALLOWED).encode())
                logger.info(f'{method} {request_path} {self.NOT_ALLOWED.code}')
                return
            if method == 'HEAD':
                client_socket.send(self.generate_main_headers(self.OK).encode())
                logger.info(f'{method} {request_path} {self.OK.code}')
                return

            file_path = os.path.join(self.path, request_path[1:])
            file = self.read_file(file_path)
            if not file:
                response_status = self.NOT_FOUND
                response = self.generate_main_headers(response_status)
                client_socket.send(response.encode())
                logger.info(f'{method} {request_path} {response_status.code}')
                return
            else:
                response_status = self.OK
                headers = self.generate_main_headers(response_status, version=version, content_type=response_mime_type,
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
        while True:
            try:
                client_socket, addr = self.server.accept()
                client_handler = threading.Thread(
                    target=self.handle_request,
                    args=(client_socket,)
                )
                client_handler.start()
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
