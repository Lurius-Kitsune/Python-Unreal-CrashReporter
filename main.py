import http.server
import zlib, os, time, zipfile
from crashDecoder import CrashDecoder
from io import BytesIO
import logging
from discordWs import DiscordWebhook

OUTPUT_DIR = "crashes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

_logger : logging.Logger

def Main():
    PORT = 8000
    httpd = http.server.HTTPServer(('', PORT), CrashReportHandler)
    print(f'Serving on port {PORT}')
    _logger = logging.getLogger('http.server')
    logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.NOTSET)
    httpd.serve_forever()

class CrashReportHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        raw_body       = self.rfile.read(content_length)
        timestamp      = time.strftime('%Y-%m-%d_%H-%M-%S')

        print(f"\n[{timestamp}] POST — {len(raw_body)} bytes")

        # Le body entier est zlib compressé
        try:
            _data = zlib.decompress(raw_body)
        except zlib.error:
            _data = raw_body  # déjà décompressé

        _files = CrashDecoder.decodeUnrealCrash(self, _data)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for name, payload in _files.items():
                zf.writestr(name, payload)
                print(f"  + {name} ({len(payload)} bytes)")

        zip_bytes = zip_buffer.getvalue()
        zip_path  = os.path.join(OUTPUT_DIR, f"Crash_{timestamp}.zip")
        with open(zip_path, 'wb') as f:
            f.write(zip_bytes)
        print(f"  → ZIP : {zip_path} ({len(zip_bytes)} bytes)")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
        
        crash_data = CrashDecoder.GetXMLData(self, _data)
        crash_data["isLogPresent"] = "Yes" if any(name.endswith('.log') for name in _files) else "No"
        DiscordWebhook.sendCrashReportToServ(crash_data, zip_path)

    # ------------------------------------------------------------------ #

Main()