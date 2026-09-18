import time, os, socket, logging
from api import *
from crashHandler import CrashHandler
from http.server import ThreadingHTTPServer
from core import events, CrashDecoder, CrashArchive

_logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class App(metaclass=Singleton):
    
    crash_dir : str
    port : int
    httpd : ThreadingHTTPServer
    data : bytes
    
    __version__ = "1.1.0"                
    __author__ = "Lurius-Kitsune"
    __name__ = "Crash Reporter"
    
    def __init__(self, _webhook_url : str, _crash_dir : str = "crashes", _port : int = 8000, ) -> None :
        self.crash_dir = _crash_dir
        DiscordWebhook.WEBHOOK_URL = _webhook_url
        os.makedirs(self.crash_dir, exist_ok=True)
        if not self._checkPort(_port):
            raise Exception(f"Port {_port} is already in use. Please choose a different port.")
        else :
            self.port = _port
        
        events.on("crash_received")(self.decodeAndArchiveFiles)
        events.on("crash_zipped")(self.onCrashZipped)
    
    def _checkPort (self, _port : int) -> bool :
        """_checkPort check if the port is opened

        Args:
            _port (int): port to check

        Returns:
            bool: True if port is not used
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', _port)) != 0
        
    def _initHttpServer (self) -> None :
        self.httpd = ThreadingHTTPServer(('0.0.0.0', self.port), CrashHandler)
        _logger.info("Serving on port %s", self.port)
        self.httpd.serve_forever()
        
    def run (self) -> None :
        try :
            self._initHttpServer()
        except KeyboardInterrupt :
            _logger.info("Shutting down server...")
            self.httpd.server_close()
            _logger.info("Server stopped.")
            
    """@events.on("crash_received")"""
    def decodeAndArchiveFiles(self, _data : bytes):
        self.data = _data
        _files = CrashDecoder.decodeUnrealCrash(_data)   
        CrashArchive.buildZip(_files)
    
    """@events.on("crash_zipped")"""
    def onCrashZipped(self, _files : dict[str, bytes], _zip_path : str):
        crash_data = CrashDecoder.GetXMLData(self.data)
        crash_data["isLogPresent"] = "Yes" if any(name.endswith('.log') for name in _files) else "No"
        
        DiscordWebhook.sendToWebhook(self.buildDiscordMessage(crash_data, _zip_path))
    
    def buildDiscordMessage(self, crash_data : dict[str, str], _zip_path : str) -> DiscordWebhookMessage:
        _message : DiscordWebhookMessage = DiscordWebhookMessage (
            title = f"CrashReport {time.strftime('%Y-%m-%d_%H_%M_%S')}",
            description =  f"**__Error message__**\n{crash_data.get('ErrorMessage', '?')}",
            color = 5814783,
            contents = [
                DiscordWebhookContent(
                    "__Play Info__",
                    (
                        f"Platform : {crash_data.get('PlatformFullName', '?')}\n"
                        f"Build : {crash_data.get('BuildConfiguration', '?')}\n"
                        f"Engine Mode : {crash_data.get('EngineMode', '?')}"
                    )
                ),
                DiscordWebhookContent(
                    "__Crash Data__",
                    (
                        f"Crash Version : {crash_data.get('CrashVersion', '?')}\n"
                        f"Crash GUID : {crash_data.get('CrashGUID', '?')}\n"
                        f"Crash Type : {crash_data.get('CrashType', '?')}"
                    )
                ),
                DiscordWebhookContent(
                    "__Is log present ?__",
                    str(crash_data.get('isLogPresent', '?'))
                ),
            ],
            author = crash_data.get('GameName', '?'),
            files = [ _zip_path ]
        )
        return _message
        