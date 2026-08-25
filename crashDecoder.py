from io import BytesIO
import struct
import subprocess
import xml.etree.ElementTree as Et

class CrashDecoder:
    
    @staticmethod
    def decodeUnrealCrash(self, data: bytes) -> dict[str, bytes]:
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

        # Header
        _buffer.read(4)    # magic CR1\x04
        _buffer.read(3)    # unk
        _buffer.read(256)  # nom rapport

        # Entrée archive
        _buffer.read(4)    # sep
        _buffer.read(4)    # unk
        _buffer.read(256)  # nom archive
        _buffer.read(4)    # padding
        _buffer.read(4)    # taille totale (ignorée)
        nb_files = struct.unpack('<I', _buffer.read(4))[0]
        print(f"  Fichiers dans l'archive : {nb_files}")

        # Lire chaque fichier
        for _ in range(nb_files):
            _buffer.read(4)   # sep
            _buffer.read(4)   # unk
            name = _buffer.read(256).rstrip(b'\x00').decode('utf-8', errors='replace')
            if name.endswith('-xml'):
                name = name[:-4] + '.xml' 
            _buffer.read(4)   # padding
            _size = struct.unpack('<I', _buffer.read(4))[0]
            payload = _buffer.read(_size)
            if(name.endswith('.dmp')):
                payload = CrashDecoder.resolve_callstack(payload, "symbols")
            _files[name] = payload

        return _files
    
    @staticmethod
    def GetXMLData(self, data: bytes) -> dict[str, str]:
        """
        Récupère le contenu XML du crash report.
        """
        _files = CrashDecoder.decodeUnrealCrash(self, data)
        for name, payload in _files.items():
            if name.endswith('.xml'):
                Et.fromstring(payload)  # Vérifie que le XML est valide
                for child in Et.fromstring(payload):
                    return {elem.tag: elem.text for elem in child}
                return payload.decode('utf-8', errors='replace')
        return ""
    
    def resolve_callstack(dmp_path: str, symbols_dir: str) -> str:
        result = subprocess.run(
            ['minidump_stackwalk', dmp_path, symbols_dir],
            capture_output=True, text=True
        )
        return result.stdout