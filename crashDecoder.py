from io import BytesIO
import os
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as Et

class CrashDecoder:
    
    @staticmethod
    def decodeUnrealCrash(data: bytes) -> dict[str, bytes]:
        """
        Patterne trouver par Claude (IA) pour parser les fichiers .uecrash envoyés par le jeu.
        
        Note : faire un hex dump et reconnaitre les paterne, permet de faire ceci.
        Format CR1 (après décompression zlib globale) :
          [4]    Magic "CR1\x04"
          [3]    unk
          [256]  Nom du rapport (null-padded)
          -- Entrée archive .uecrash --
          [4]    séparateur (0x00000000)
          [4]    unk
          [256]  Nom archive
          [4]    padding (0x00000000)
          [4]    taille totale (ignorée)
          [4]    nombre de fichiers
          -- Pour chaque fichier --
          [4]    séparateur
          [4]    unk
          [256]  Nom du fichier (null-padded)
          [4]    padding (0x00000000)
          [4]    taille des données (uint32 LE)
          [N]    données brutes (non compressées)
        """
        
        _buffer = BytesIO(data)
        _files = {}

        def _readBuffer(size: int) -> bytes:
            value = _buffer.read(size)
            if len(value) != size:
                raise ValueError("Invalid or truncated Unreal crash archive")
            return value

        # Header
        if _readBuffer(4) != b"CR1\x04":
            raise ValueError("Unsupported Unreal crash archive format")
        _readBuffer(3)    # unk
        _readBuffer(256)  # nom rapport

        # Entrée archive
        _readBuffer(4)    # sep
        _readBuffer(4)    # unk
        _readBuffer(256)  # nom archive
        _readBuffer(4)    # padding
        _readBuffer(4)    # taille totale (ignorée)
        nb_files = struct.unpack('<I', _readBuffer(4))[0]
        print(f"  Fichiers dans l'archive : {nb_files}")

        # Lire chaque fichier
        for _ in range(nb_files):
            _readBuffer(4)   # sep
            _readBuffer(4)   # unk
            name = _readBuffer(256).rstrip(b'\x00').decode('utf-8', errors='replace')
            if name.endswith('-xml'):
                name = name[:-4] + '.xml' 
            _readBuffer(4)   # padding
            _size = struct.unpack('<I', _readBuffer(4))[0]
            payload = _readBuffer(_size)
            if name.endswith('.dmp'):
                callstack = CrashDecoder.resolve_callstack(payload, "symbols")
                if callstack != payload:
                    _files[f'{name}.stacktrace'] = callstack
            _files[name] = payload

        return _files
    
    @staticmethod
    def GetXMLData(data: bytes) -> dict[str, str]:
        """
        Récupère le contenu XML du crash report.
        """
        _files = CrashDecoder.decodeUnrealCrash(data)
        for name, payload in _files.items():
            if name.endswith('.xml'):
                root = Et.fromstring(payload)
                elements = next(iter(root), root)
                if not list(elements):
                    elements = root
                return {elem.tag: elem.text or "" for elem in elements}
        return {}
    
    @staticmethod
    def resolve_callstack(dmp_data: bytes, symbols_dir: str) -> bytes:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".dmp") as dump_file:
                dump_file.write(dmp_data)
                dump_path = dump_file.name
            # result = subprocess.run(
            #     ['minidump_stackwalk', dump_path, symbols_dir],
            #     capture_output=True, text=True, check=False
            # )
            # if result.returncode == 0 and result.stdout:
            #     return result.stdout.encode('utf-8')
        except (OSError, subprocess.SubprocessError):
            pass
        finally:
            if 'dump_path' in locals():
                os.unlink(dump_path)
        return dmp_data