# Installation

## Components

eddrit needs two components to work:
- the app itself
- a [valkey](https://github.com/valkey-io/valkey) instance (used to store OAuth tokens)

## Installation

You can run the app through Docker, or directly if you know how to deploy a Python ASGI application.

### Option 1: Docker (recommended)

You can get the image from either:
- [Docker Hub](https://hub.docker.com/r/corentingarcia/eddrit) as `corentingarcia/eddrit`
- [ghcr.io](https://github.com/corenting/eddrit/pkgs/container/eddrit) as `ghcr.io/corenting/eddrit`

There are multiple tags:
- `latest` for the latest stable tagged release (**recommended**)
- `dev` for the latest development version (the latest commit on the master branch)
- Version tags (like `0.1.1`, `0.1.2`) for specific versions

ℹ️ *Note*: you can find an example Docker Compose `docker-compose.yml` file [here](./docker-compose.yml).

The following architectures are supported by the Docker image:
- `linux/amd64`
- `linux/i386`
- `linux/arm64`
- `linux/arm/v7`
- `linux/ppc64le`

### Option 2: without Docker

If you know how to deploy a Python ASGI application, you can also deploy it directly without Docker.

For example, with [uvicorn](https://uvicorn.org/):
1. Make sure Python >=3.13 is installed on your system as it's the minimum version supported by eddrit.
2. Install [Poetry](https://python-poetry.org/) which is used to manage dependencies of the project.
3. Download/clone the repository and run `poetry install --only main` to install the application.
4. You can then run the app through uvicorn, for example with the following command: `poetry run uvicorn eddrit.app:app`

## Configuration

The application can be configured through environment variables (if a `.env` file is present, it will also be read).

Mandatory configuration:
- `VALKEY_URL`: the URL to your [valkey](https://github.com/valkey-io/valkey) instance. Example: `valkeys://my_user:my_password@example.com:15345/1`
- `FORWARDED_ALLOW_IPS` (if using a proxy such as nginx, traefik etc. in front of the app): a comma-separated list of the IP addresses used by the proxy, to trust for setting up the correct public URL for the instance. For example `127.0.0.1,::1` for a proxy running locally. Set to * to disable checking of IPs. This is useful for setups where you don’t know in advance the IP address of front-end, but instead have ensured via other means that only your authorized front-ends can access the app.
Also make sure that the proxy sets the correct `X-Forwarded-For`, `X-Forwarded-Proto` etc. headers.


Optional configuration:
- `DEBUG` (default is `false`): enable [starlette](https://www.starlette.io/) debug mode. Should not be needed outside of development.
- `LOG_LEVEL` (default is `WARNING`): only log if the message level is superior or equal to this level.
- `PROXY` (default is null): if set, requests to Reddit will be sent through the specified proxy. This can be used to bypass
IP-based blocks, for example if proxying the instance through Cloudflare WARP.
