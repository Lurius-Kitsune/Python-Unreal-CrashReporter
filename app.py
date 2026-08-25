import os
import socket
import http.server
import logging
from crashReporter import CrashReportHandler

_logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class App(metaclass=Singleton):
    output_dir : str
    port : int
    httpd : http.server.HTTPServer
    
    def __init__(self, _output_dir : str = "crashes", _port : int = 8000) -> None :
        self.output_dir = _output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        if not self._checkPort(_port):
            raise Exception(f"Port {_port} is already in use. Please choose a different port.")
        else :
            self.port = _port
        
        self.name = "Crash Reporter"
        self.version = "1.0.0"
        self.author = "LuriusFox"
        
    def _checkPort (self, port : int) -> bool :
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
        
    def _initHttpServer (self) -> None :
        self.httpd = http.server.HTTPServer(('', self.port), CrashReportHandler)
        _logger.info("Serving on port %s", self.port)
        self.httpd.serve_forever()
        
    def run (self) -> None :
        try :
            self._initHttpServer()
        except KeyboardInterrupt :
            _logger.info("Shutting down server...")
            self.httpd.server_close()
            _logger.info("Server stopped.")