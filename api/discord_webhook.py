from dataclasses import dataclass
import os
import requests
import time
import logging

_logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass
class DiscordWebhookContent:
    name : str
    value : str 

@dataclass
class DiscordWebhookMessage:
    title : str
    description : str
    color : int
    contents : list[DiscordWebhookContent]
    author : str
    files : list[str]


class DiscordWebhook:
    
    WEBHOOK_URL : str = ""
    
    @staticmethod
    def sendToWebhook(_data : DiscordWebhookMessage):
        if(not DiscordWebhook.WEBHOOK_URL or not str.__contains__(DiscordWebhook.WEBHOOK_URL, "https://discord.com/api/webhooks/")):
            _logger.warning("Discord webhook URL is not configured")
            return
        
        payload = {
            "embeds": [
                {
                    "title": _data.title,
                    "description": _data.description,
                    "color": _data.color,
                    "fields": [
                        {"name": content.name, "value": content.value}
                        for content in _data.contents
                    ],
                    "author": {
                        "name": _data.author
                    }
                }
            ],
            "attachments": []
        }
        
        #send json + file to webhook
        _nbFiles = len(_data.files)
        if _nbFiles <= 0:
            response = requests.post(DiscordWebhook.WEBHOOK_URL, json=payload)
        else:
            # 1. Embed en premier
            response = requests.post(DiscordWebhook.WEBHOOK_URL, json=payload)
            
            if response.status_code in (200, 204):
                # 2. Fichier ensuite
                for _file in _data.files:
                    with open(_file, "rb") as f:
                        response = requests.post(
                            DiscordWebhook.WEBHOOK_URL,
                            files={"file": (os.path.basename(_file), f, "application/zip")}
                        )
        
        if response.status_code == 204 or response.status_code == 200:
            _logger.info("Crash report sent successfully to Discord")
        else:
            _logger.error("Failed to send crash report to Discord: HTTP %s, response: %s", response.status_code, response.text)



    