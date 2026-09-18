import http.server
import zlib
from api import DiscordWebhook
import logging
from core import CrashDecoder, CrashArchive, events

_logger = logging.getLogger(__name__)

class CrashHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        raw_body       = self.rfile.read(content_length)

        _logger.info("Received crash report: %s bytes", len(raw_body))

        # Le body entier est zlib compressé
        try:
            _data = zlib.decompress(raw_body)
        except zlib.error:
            _data = raw_body  # déjà décompressé
        
        events.emit("crash_received", _data)
        
        self.send_response(200 if _data.__len__() <= 0 else 500)
        self.end_headers()
        self.wfile.write(b'OK')
        
        

    # ------------------------------------------------------------------ #
