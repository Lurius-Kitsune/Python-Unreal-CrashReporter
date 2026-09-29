# Unreal Crash Reporter

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker\&logoColor=white)](https://www.docker.com/)
[![Discord Webhook](https://img.shields.io/badge/Discord-Webhook-5865F2?logo=discord\&logoColor=white)](https://discord.com/)
[![Docker Build](https://img.shields.io/badge/Docker%20Build-GitHub%20Actions-2088FF?logo=githubactions\&logoColor=white)](.github/workflows/DockerImage.yml)
[![GHCR](https://img.shields.io/badge/Image-GHCR-2496ED?logo=docker\&logoColor=white)](https://ghcr.io/)

A lightweight HTTP crash-reporting service for Unreal Engine applications.

The service accepts Unreal Engine crash reports over HTTP, extracts their contents, stores them as ZIP archives, and optionally sends a summary and the archive to a Discord channel through a webhook.

## Features

* Accepts Unreal Engine crash reports over HTTP.
* Compatible with the Unreal Engine `CrashReportClient`.
* Extracts crash files from Unreal Engine crash reports.
* Supports zlib-compressed and uncompressed crash report payloads.
* Packages crash reports as ZIP archives.
* Extracts basic crash information from the XML report.
* Stores crash archives locally.
* Sends crash summaries and ZIP files to Discord.
* Optional Discord integration.
* Configurable logging level.
* Docker-ready.
* Uses a small `python:3.13-slim` Docker image.
* Can be configured directly from an Unreal Engine project's `DefaultEngine.ini`.

## Requirements

* Docker Desktop or Docker Engine
* An Unreal Engine project
* A Discord webhook URL if Discord notifications are required

---

## Build the image

Run this command from the project directory:

```bash
docker build -t py-crasher-unreal .
```

---

## Configure the Discord webhook

1. Open the Discord server and channel where crash reports should be sent.
2. Open **Edit Channel** > **Integrations** > **Webhooks**.
3. Create or select a webhook.
4. Copy the webhook URL.
5. Pass the URL to the container through the `DISCORD_WEBHOOK` environment variable.

Keep the webhook URL private. Anyone who has access to it can send messages to the configured Discord channel.

---

## Run the container

The following command starts the service on port `8000` and configures Discord notifications:

```bash
docker run -d --name py-crasher-unreal \
  -p 8000:8000 \
  --restart unless-stopped \
  -e "DISCORD_WEBHOOK=https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN" \
  -v "${PWD}/crashes:/app/crashes" \
  -v "${PWD}/logs:/app/logs" \
  ghcr.io/lurius-kitsune/unreal-py-crashreport:latest
```

The `crashes` volume keeps crash archives on the host, while the `logs` volume keeps the application log file when the container is stopped or removed.

Both local directories are created automatically if they do not already exist.

### Run without Discord

Discord notifications are optional.

To run the crash reporter without Discord:

```bash
docker run -d --name py-crasher-unreal \
  -p 8000:8000 \
  -v "${PWD}/crashes:/app/crashes" \
  -v "${PWD}/logs:/app/logs" \
  py-crasher-unreal
```

---

# Configure Unreal Engine

Unreal Engine's `CrashReportClient` can be configured to send crash reports to a custom server using the `DataRouterUrl` setting.

The configuration is placed in your Unreal Engine project's:

```text
Config/DefaultEngine.ini
```

Add the following section:

```ini
[CrashReportClient]
DataRouterUrl="http://127.0.0.1:8000/"
```

For a server accessible over your network or the Internet, replace the URL with the address of your crash reporter:

```ini
[CrashReportClient]
DataRouterUrl="https://crash.example.com/"
```

`DataRouterUrl` is the endpoint used by Unreal Engine's Crash Reporter Client to upload crash reports.

### Example

A complete `DefaultEngine.ini` could look like this:

```ini
[/Script/Engine.Engine]
+ActiveGameNameRedirects=(OldGameName="OldProject",NewGameName="/Script/MyProject")

[CrashReportClient]
DataRouterUrl="http://127.0.0.1:8000/"
bSendLogFile=true
```

The following options can also be configured:

```ini
[CrashReportClient]
DataRouterUrl="http://127.0.0.1:8000/"
bSendLogFile=true
bAllowToBeContacted=true
```

Where:

| Option                | Description                                                       |
| --------------------- | ----------------------------------------------------------------- |
| `DataRouterUrl`       | URL of the crash-reporting server.                                |
| `bSendLogFile`        | Enables sending the game's log file with the crash report.        |
| `bAllowToBeContacted` | Controls the default state of the "Allow to be contacted" option. |

`DataRouterUrl` is the only setting required by this service. The other options are optional Unreal Engine `CrashReportClient` settings.

---

## Local development

If the Unreal Engine game and the crash reporter are running on the same machine, use:

```ini
[CrashReportClient]
DataRouterUrl="http://127.0.0.1:8000/"
```

Then start the Docker container:

```bash
docker run -d --name py-crasher-unreal \
  -p 8000:8000 \
  -v "${PWD}/crashes:/app/crashes" \
  -v "${PWD}/logs:/app/logs" \
  py-crasher-unreal
```

Unreal Engine will send crash reports to:

```text
http://127.0.0.1:8000/
```

### Important

`127.0.0.1` refers to the machine running the Unreal Engine application.

If the game is running on another computer, `127.0.0.1` will point to that computer, not to the machine running the crash reporter.

For example, if the crash reporter is running on:

```text
192.168.1.100
```

use:

```ini
[CrashReportClient]
DataRouterUrl="http://192.168.1.100:8000/"
```

Make sure port `8000` is accessible from the machine running the game.

---

## Production configuration

For a production deployment, it is recommended to expose the crash reporter through HTTPS:

```ini
[CrashReportClient]
DataRouterUrl="https://crash.example.com/"
```

For example:

```text
Unreal Engine
      |
      | HTTP POST
      v
https://crash.example.com/
      |
      v
Unreal Crash Reporter
      |
      +----> ZIP archive
      |
      +----> Discord webhook
```

The crash reporter itself listens on:

```text
0.0.0.0:8000
```

inside the Docker container.

A reverse proxy such as Nginx, Caddy, or Traefik can be used to provide HTTPS and expose the service publicly.

---

## Packaged builds

When distributing a packaged Unreal Engine game, make sure the Crash Reporter Client is included in the build.

Unreal Engine supports including the Crash Reporter Client in packaged builds, and its configuration can be customized through `CrashReportClient`.

For a packaged game, verify that the final build contains the Crash Reporter Client and that the `DataRouterUrl` points to your crash reporter.

Example:

```ini
[CrashReportClient]
DataRouterUrl="https://crash.example.com/"
bSendLogFile=true
```

This allows crashes from distributed builds to be sent to your server instead of Unreal Engine's default crash-reporting endpoint.

---

## Automatic crash uploads

If you want Unreal Engine to automatically accept crash uploads without requiring the user to interact with the Crash Reporter UI, Unreal Engine provides additional `CrashReportClient` configuration options.

For example:

```ini
[CrashReportClient]
DataRouterUrl="https://crash.example.com/"
bAgreeToCrashUpload=true
```

Use this option according to your project's privacy and consent requirements. Unreal Engine documents `bAgreeToCrashUpload` as controlling whether crash uploads are automatically agreed to.

---

## Sending crash reports manually

The service accepts Unreal Engine crash report data using an HTTP `POST` request on port `8000`.

Example:

```text
POST http://localhost:8000/
Content-Type: application/octet-stream
```

The request body should contain the Unreal Engine crash archive.

The Unreal Engine `CrashReportClient` compresses crash report data before sending it to the configured `DataRouterUrl`.

The server accepts both:

* zlib-compressed crash reports
* uncompressed crash reports

---

## Configuration

The application can be configured using environment variables.

| Variable          | Required | Description                                      | Default |
| ----------------- | -------- | ------------------------------------------------ | ------- |
| `DISCORD_WEBHOOK` | No       | Discord webhook URL used for crash notifications | Empty   |
| `LOG_LEVEL`       | No       | Application logging level                        | `INFO`  |

### `DISCORD_WEBHOOK`

Discord webhook used to send crash notifications.

Example:

```bash
-e "DISCORD_WEBHOOK=https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
```

If this variable is not provided, crash reports are still stored locally but no Discord notification is sent.

### `LOG_LEVEL`

Controls the application logging level.

Supported values include:

```text
DEBUG
INFO
WARNING
ERROR
```

Example:

```bash
-e "LOG_LEVEL=DEBUG"
```

---

## Logging

The application writes logs to both:

* Docker standard output
* `logs/crash_reporter.log`

View Docker logs with:

```bash
docker logs py-crasher-unreal
```

To follow logs in real time:

```bash
docker logs -f py-crasher-unreal
```

To enable debug logging:

```bash
docker run -d --name py-crasher-unreal \
  -p 8000:8000 \
  --restart unless-stopped \
  -e "LOG_LEVEL=DEBUG" \
  -v "${PWD}/crashes:/app/crashes" \
  -v "${PWD}/logs:/app/logs" \
  py-crasher-unreal
```

---

## Project layout

```text
app.py            HTTP server lifecycle
crashDecoder.py   Unreal crash archive and XML parsing
crashReporter.py  HTTP POST handler and archive storage
discordWs.py      Discord webhook integration
main.py           Application entry point
dockerfile        Container image definition
symbols/          Symbol files used for crash decoding
crashes/          Locally stored crash archives
logs/             Application logs
```

---

## Crash report workflow

The complete workflow looks like this:

```text
┌──────────────────────┐
│   Unreal Engine Game │
└──────────┬───────────┘
           │
           │ Crash
           ▼
┌──────────────────────┐
│   CrashReportClient  │
└──────────┬───────────┘
           │
           │ HTTP POST
           │ DataRouterUrl
           ▼
┌──────────────────────┐
│ Unreal Crash Reporter│
│   Docker Container   │
└──────────┬───────────┘
           │
           ├───────────────► crashes/*.zip
           │
           ▼
┌──────────────────────┐
│ Discord Webhook      │
└──────────────────────┘
```

---

## Stop and remove the container

Stop the container:

```powershell
docker stop py-crasher-unreal
```

Remove it:

```powershell
docker rm py-crasher-unreal
```

The crash archives and logs remain on the host if the corresponding Docker volumes are configured.

---

## Troubleshooting

### No Discord message

Verify that:

```bash
DISCORD_WEBHOOK
```

is set and that the webhook URL is valid.

Check the application logs:

```bash
docker logs py-crasher-unreal
```

---

### Unreal Engine does not send the crash

Check your project's:

```text
Config/DefaultEngine.ini
```

and verify that it contains:

```ini
[CrashReportClient]
DataRouterUrl="http://127.0.0.1:8000/"
```

Also verify that the Docker container is running:

```bash
docker ps
```

And that port `8000` is published:

```text
0.0.0.0:8000->8000/tcp
```

---

### Port already in use

If port `8000` is already used by another application, publish another host port:

```bash
docker run -d --name py-crasher-unreal \
  -p 8080:8000 \
  py-crasher-unreal
```

Then update Unreal Engine:

```ini
[CrashReportClient]
DataRouterUrl="http://127.0.0.1:8080/"
```

The Docker container continues listening on port `8000`; only the host port changes.

---

### Crash archives disappear

Make sure the crashes volume is configured:

```bash
-v "${PWD}/crashes:/app/crashes"
```

Without this volume, crash archives are stored inside the Docker container and can be lost when the container is removed.

---

### Logs disappear

Mount the logs directory:

```bash
-v "${PWD}/logs:/app/logs"
```

The application log will then be available on the host at:

```text
logs/crash_reporter.log
```

---

### Missing symbols

Place the required symbol files in the project's:

```text
symbols/
```

directory before building the Docker image.

Then rebuild:

```bash
docker build -t py-crasher-unreal .
```

---

## Security

If the crash reporter is exposed to the Internet:

* Use HTTPS.
* Keep the Discord webhook private.
* Consider placing the service behind a reverse proxy.
* Restrict access to the crash-reporting endpoint when possible.
* Monitor the size and number of uploaded crash reports.
* Regularly clean old crash archives.
* Avoid exposing the Docker management API publicly.

Crash reports can contain sensitive information such as logs, file paths, hardware information, or application-specific data. Make sure your deployment complies with your project's privacy requirements.

---

## License

No license has been specified for this project yet.
