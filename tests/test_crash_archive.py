import zipfile

from core import CrashArchive


def test_build_zip_with_empty_files(tmp_path):
    result = CrashArchive.buildZip(
        {},
        str(tmp_path)
    )

    assert result is False

    # Aucun fichier ne doit avoir été créé
    assert list(tmp_path.iterdir()) == []


def test_build_zip(tmp_path, monkeypatch):
    files = {
        "crash.log": b"Hello crash",
        "game.log": b"Game log content",
        "data.txt": b"Some data",
    }

    emitted_events = []

    def fake_emit(event_name, *args, **kwargs):
        emitted_events.append(
            (event_name, args, kwargs)
        )

    monkeypatch.setattr(
        "core.crash_archive.events.emit",
        fake_emit
    )

    result = CrashArchive.buildZip(
        files,
        str(tmp_path)
    )

    assert result is True

    # Un seul ZIP doit avoir été créé
    zip_files = list(tmp_path.glob("Crash_*.zip"))

    assert len(zip_files) == 1

    zip_path = zip_files[0]

    # Vérifie que c'est bien un ZIP valide
    assert zipfile.is_zipfile(zip_path)

    # Vérifie le contenu du ZIP
    with zipfile.ZipFile(zip_path, "r") as archive:
        assert set(archive.namelist()) == {
            "crash.log",
            "game.log",
            "data.txt",
        }

        assert archive.read("crash.log") == b"Hello crash"
        assert archive.read("game.log") == b"Game log content"
        assert archive.read("data.txt") == b"Some data"

    # Vérifie l'event
    assert len(emitted_events) == 1

    event_name, args, kwargs = emitted_events[0]

    assert event_name == "crash_zipped"
    assert args[0] == files
    assert args[1] == str(zip_path)
    assert kwargs == {}
    
def test_build_zip_with_empty_file(tmp_path, monkeypatch):
    files = {
        "empty.log": b"",
    }

    monkeypatch.setattr(
        "core.crash_archive.events.emit",
        lambda *args, **kwargs: None
    )

    result = CrashArchive.buildZip(
        files,
        str(tmp_path)
    )

    assert result is True

    zip_files = list(tmp_path.glob("Crash_*.zip"))

    assert len(zip_files) == 1

    with zipfile.ZipFile(zip_files[0], "r") as archive:
        assert archive.namelist() == ["empty.log"]
        assert archive.read("empty.log") == b""