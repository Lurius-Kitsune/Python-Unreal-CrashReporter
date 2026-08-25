import os
import requests
import time

class DiscordWebhook:
    
    WEBHOOK_URL : str = ""
    
    @staticmethod
    def sendCrashReportToServ(crashReportData : dict[str, str], _filePath : str|None) -> None:
        """
        Send the crash report data to the Discord webhook.
        """
        
        WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
        print(f"Discord webhook URL: {WEBHOOK_URL}")
        if(not WEBHOOK_URL or not str.__contains__(WEBHOOK_URL, "https://discord.com/api/webhooks/")):
            print("Discord webhook URL is not set. Please set the DISCORD_WEBHOOK environment variable.")
            return
        
        
        _currentTime : str = time.strftime('%Y-%m-%d_%H_%M_%S');
        
        payload = {
            "embeds": [
                {
                    "title": f"CrashReport {_currentTime}",
                    "description": f"**__Error message__**\n{crashReportData.get('ErrorMessage', '?')}",
                    "color": 5814783,
                    "fields": [
                        {
                            "name": "__Play Info__",
                            "value": (
                                f"Platform : {crashReportData.get('PlatformFullName', '?')}\n"
                                f"Build : {crashReportData.get('BuildConfiguration', '?')}\n"
                                f"Engine Mode : {crashReportData.get('EngineMode', '?')}"
                            )
                        },
                        {
                            "name": "__Crash Data__",
                            "value": (
                                f"Crash Version : {crashReportData.get('CrashVersion', '?')}\n"
                                f"Crash GUID : {crashReportData.get('CrashGUID', '?')}\n"
                                f"Crash Type : {crashReportData.get('CrashType', '?')}"
                            )
                        },
                        {
                            "name": "__Is log present ?__",
                            "value": str(crashReportData.get('isLogPresent', '?'))
                        }
                    ],
                    "author": {
                        "name": crashReportData.get('GameName', '?')
                    }
                }
            ],
            "attachments": []
        }
        headers = {'Content-Type': 'application/json'}
        #send json + file to webhook
        
        
        if _filePath is None:
            response = requests.post(WEBHOOK_URL, json=payload)
        else:
            # 1. Embed en premier
            response = requests.post(WEBHOOK_URL, json=payload)
            
            if response.status_code in (200, 204):
                # 2. Fichier ensuite
                with open(_filePath, "rb") as f:
                    response = requests.post(
                        WEBHOOK_URL,
                        files={"file": (f"CrashDump_{_currentTime}.zip", f, "application/zip")}
                    )
        
        if response.status_code == 204 or response.status_code == 200:
            print("Crash report sent successfully to Discord.")
        else:
            print(f"Failed to send crash report to Discord. Status code: {response.status_code}, Response: {response.text}")
            
        
    
    
    