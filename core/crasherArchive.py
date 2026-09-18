
from io import BytesIO
import os, time, zipfile, logging
from core.EventEmitter import events
_logger = logging.getLogger(__name__)

class CrashArchive():
        
    @staticmethod
    def buildZip(_files : dict[str, bytes], crash_dir_path : str = "crashes") -> bool:
        
        if (_files.__len__() == 0) : 
            return False
        
        zip_buffer = BytesIO()
        timestamp  = time.strftime('%Y-%m-%d_%H-%M-%S')
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for name, payload in _files.items():
                zf.writestr(name, payload)
                _logger.info("Extracted %s (%s bytes)", name, len(payload))
        
        zip_bytes = zip_buffer.getvalue()
        zip_path  = os.path.join(crash_dir_path, f"Crash_{timestamp}.zip")
        with open(zip_path, 'wb') as f:
            f.write(zip_bytes)
        _logger.info("Crash archive written to %s (%s bytes)", zip_path, len(zip_bytes))
        
        events.emit("crash_zipped", _files,zip_path)
        return True
        