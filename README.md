# Unreal Crash Reporter

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Discord Webhook](https://img.shields.io/badge/Discord-Webhook-5865F2?logo=discord&logoColor=white)](https://discord.com/)
[![Docker Build](https://img.shields.io/badge/Docker%20Build-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/DockerImage.yml)
[![GHCR](https://img.shields.io/badge/Image-GHCR-2496ED?logo=docker&logoColor=white)](https://ghcr.io/)

A lightweight HTTP crash-reporting service for Unreal Engine applications. The service accepts compressed Unreal crash reports, extracts their contents, stores them as ZIP archives, and sends a summary and the archive to a Discord channel through a webhook.

## Features

- Accepts Unreal Engine crash reports over HTTP.
- Extracts crash files and packages them as ZIP archives.
- Extracts basic crash information from the XML report.
- Sends crash summaries and ZIP files to Discord.
- Uses a small `python:3.13-slim` Docker image.

## Requirements

- Docker Desktop or Docker Engine
- A Discord webhook URL

## Build the image

Run this command from the project directory:

```powershell
docker build -t py-crasher-unreal .
```

## Configure the Discord webhook

1. Open the Discord server and channel where reports should be sent.
2. Open **Edit Channel** > **Integrations** > **Webhooks**.
3. Create or select a webhook and copy its URL.
4. Pass the URL to the container through the `DISCORD_WEBHOOK` environment variable.

Keep the webhook URL private. Anyone who has it can send messages to the configured Discord channel.

## Run the container

The following command starts the service on port `8000` and configures Discord notifications:

```powershell
docker run --name py-crasher-unreal `
 -p 8000:8000 `
 -e "DISCORD_WEBHOOK=https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN" `
 -v "${PWD}/crashes:/app/crashes" `
 -v "${PWD}/logs:/app/logs" `
 py-crasher-unreal
```

The `crashes` volume keeps crash archives on the host, while the `logs` volume keeps the application log file when the container is stopped or removed. Both local directories are created automatically if they do not already exist.

## Logging

The application writes logs to both:

- Docker standard output, available with `docker logs py-crasher-unreal`.
- `logs/crash_reporter.log` inside the container.

To change the log level, set `LOG_LEVEL` when starting the container. Supported values include `DEBUG`, `INFO`, `WARNING`, and `ERROR`:

```powershell
docker run --name py-crasher-unreal `
 -p 8000:8000 `
 -e "LOG_LEVEL=DEBUG" `
 -v "${PWD}/crashes:/app/crashes" `
 -v "${PWD}/logs:/app/logs" `
 py-crasher-unreal
```

To run without Discord notifications, omit the `-e` option:

```powershell
docker run --name py-crasher-unreal -p 8000:8000 -v "${PWD}/logs:/app/logs" py-crasher-unreal
```

## Configuration

| Variable          | Required | Description                                      | Default |
| ----------------- | -------- | ------------------------------------------------ | ------- |
| `DISCORD_WEBHOOK` | No       | Discord webhook URL used for crash notifications | Empty   |
| `LOG_LEVEL`       | No       | Application logging level                        | `INFO`  |

The HTTP server listens on `0.0.0.0:8000` inside the container. Port `8000` is exposed by the image and must be published with `-p` when the service needs to receive requests from outside Docker.

## Sending crash reports

Send the Unreal crash report body to the service using an HTTP `POST` request on port `8000`. For example:

```text
POST http://localhost:8000/
Content-Type: application/octet-stream
```

The request body should contain the Unreal crash archive, either compressed with zlib or uncompressed.

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
```

## Stop and remove the container

```powershell
docker stop py-crasher-unreal
docker rm py-crasher-unreal
```

## Troubleshooting

- **No Discord message:** verify that `DISCORD_WEBHOOK` is set and that the webhook URL is valid.
- **Port already in use:** publish another host port, for example `-p 8080:8000`.
- **Crash archives disappear:** make sure the `-v "${PWD}/crashes:/app/crashes"` volume option is present.
- **Need to inspect logs:** run `docker logs py-crasher-unreal` or inspect `logs/crash_reporter.log` on the host.
- **Missing symbols:** place the required symbol files in the project `symbols/` directory before building the image.

## License

No license has been specified for this project yet.
