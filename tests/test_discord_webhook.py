from api import DiscordWebhook,DiscordWebhookMessage, DiscordWebhookContent
from app import App

def test_send_webhook_without_file(monkeypatch):
    DiscordWebhook.WEBHOOK_URL = "https://discord.com/api/webhooks/test/test"
    calls = []

    class FakeResponse:
        status_code = 204
        text = ""

    def fake_post(url, **kwargs):
        calls.append({
            "url": url,
            "kwargs": kwargs,
        })

        return FakeResponse()

    monkeypatch.setattr(
        "api.discord_webhook.requests.post",
        fake_post
    )

    message = DiscordWebhookMessage(
        title="Test crash",
        description="Test description",
        color=5814783,
        contents=[
            DiscordWebhookContent(
                name="Platform",
                value="Windows"
            )
        ],
        author="MyGame",
        files=[]
    )

    DiscordWebhook.sendToWebhook(message)

    assert len(calls) == 1
    assert calls[0]["url"] == DiscordWebhook.WEBHOOK_URL

    payload = calls[0]["kwargs"]["json"]

    assert payload["embeds"][0]["title"] == "Test crash"
    assert payload["embeds"][0]["description"] == "Test description"

def test_webhook_not_configured(monkeypatch):
    DiscordWebhook.WEBHOOK_URL = ""

    called = False

    def fake_post(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(
        "api.discord_webhook.requests.post",
        fake_post
    )

    message = DiscordWebhookMessage(
        title="Test",
        description="Test",
        color=0,
        contents=[],
        author="Test",
        files=[]
    )

    DiscordWebhook.sendToWebhook(message)

    assert called is False
    
    
def test_build_discord_message():
    crash_data = {
        "ErrorMessage": "NullReferenceException",
        "PlatformFullName": "Windows 11",
        "BuildConfiguration": "Development",
        "EngineMode": "Game",
        "CrashVersion": "1.2.3",
        "CrashGUID": "ABC-123",
        "CrashType": "Crash",
        "isLogPresent": "Yes",
        "GameName": "MyGame",
    }

    zip_path = "crash.zip"
    app = App("")
    message = app.buildDiscordMessage(
        crash_data,
        zip_path
    )

    assert message.title.startswith("CrashReport")
    assert "NullReferenceException" in message.description
    assert message.author == "MyGame"
    assert message.files == [zip_path]

    assert len(message.contents) == 3