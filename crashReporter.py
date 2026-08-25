import http.server
from discordWs import DiscordWebhook
import zlib, os, time, zipfile
import logging
from io import BytesIO
from crashDecoder import CrashDecoder

_logger = logging.getLogger(__name__)

class CrashReportHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        raw_body       = self.rfile.read(content_length)
        timestamp      = time.strftime('%Y-%m-%d_%H-%M-%S')

        _logger.info("Received crash report: %s bytes", len(raw_body))

        # Le body entier est zlib compressé
        try:
            _data = zlib.decompress(raw_body)
        except zlib.error:
            _data = raw_body  # déjà décompressé

        _files = CrashDecoder.decodeUnrealCrash(_data)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for name, payload in _files.items():
                zf.writestr(name, payload)
                _logger.info("Extracted %s (%s bytes)", name, len(payload))

        zip_bytes = zip_buffer.getvalue()
        from app import App
        zip_path  = os.path.join(App().output_dir, f"Crash_{timestamp}.zip")
        with open(zip_path, 'wb') as f:
            f.write(zip_bytes)
        _logger.info("Crash archive written to %s (%s bytes)", zip_path, len(zip_bytes))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
        
        crash_data = CrashDecoder.GetXMLData(_data)
        crash_data["isLogPresent"] = "Yes" if any(name.endswith('.log') for name in _files) else "No"
        DiscordWebhook.sendCrashReportToServ(crash_data, zip_path)

    # ------------------------------------------------------------------ #
