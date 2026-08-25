import requests
import time

class DiscordWebhook:
    
    WEBHOOK_URL : str = "https://discord.com/api/webhooks/1517445305459671100/DZwvoYx5IZ2uaOKd0D5HDEfyjmJt5zsJbOG5ffHYYt6Ng5NiU1s7bcxHb9sXSP94BWKu"
    
    @staticmethod
    def sendCrashReportToServ(crashReportData : dict[str, str], _filePath : str|None) -> None:
        """
        Send the crash report data to the Discord webhook.
        """
        
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
            response = requests.post(DiscordWebhook.WEBHOOK_URL, json=payload)
        else:
            # 1. Embed en premier
            response = requests.post(DiscordWebhook.WEBHOOK_URL, json=payload)
            
            if response.status_code in (200, 204):
                # 2. Fichier ensuite
                with open(_filePath, "rb") as f:
                    response = requests.post(
                        DiscordWebhook.WEBHOOK_URL,
                        files={"file": (f"CrashDump_{_currentTime}.zip", f, "application/zip")}
                    )
        
        if response.status_code == 204 or response.status_code == 200:
            print("Crash report sent successfully to Discord.")
        else:
            print(f"Failed to send crash report to Discord. Status code: {response.status_code}, Response: {response.text}")
            
        
    
    
    