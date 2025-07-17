<div align="center">

<image src="static/images/logo.svg" height="80">

<hr>

A lightweight alternative frontend for Reddit.

![GitHub Tag](https://img.shields.io/github/v/tag/corenting/eddrit?label=latest)
![Build](https://img.shields.io/github/actions/workflow/status/corenting/eddrit/ci.yml?branch=master)
![License](https://img.shields.io/github/license/corenting/eddrit)

<a href="https://eddrit.com"><img src="https://raw.githubusercontent.com/corenting/eddrit/master/doc/screenshots/subreddit.png" width="80%"></a>

</div>

**Official instance**: [eddrit.com](https://eddrit.com)

- Lightweight
- No ads
- Compact design (closer to [old.reddit.com](https://old.reddit.com) than to the redesign)
- Better mobile support
- No need to register for an OAuth2 identifier for self-hosting: mimic the official Android app by default to bypass rate-limiting.
- Basic RSS support (for subreddits and posts): fetch the original RSS feed from Reddit, and rewrite the URLs to point to the current eddrit instance.

Inspired by [Nitter](https://github.com/zedeus/nitter), an alternative frontend for Twitter.

Written with Python & [Starlette](https://www.starlette.io/).

## Usage

You can use the official instance at [eddrit.com](https://eddrit.com).

Like Nitter, the URLs are identical to reddit, so if you can just replace `reddit.com` by `eddrit.com` to open a Reddit page in eddrit.

## Deployment (for self-hosting)

You can also deploy eddrit for yourself if you don't want to use the public instance.

### Docker (recommended)

You can get the image from either:
- [Docker Hub](https://hub.docker.com/r/corentingarcia/eddrit) as `corentingarcia/eddrit`
- [ghcr.io](https://github.com/corenting/eddrit/pkgs/container/eddrit) as `ghcr.io/corenting/eddrit`

There are multiple tags:
- `latest` for the latest stable tagged release (**recommended**)
- `dev` for the latest development version (the latest commit on the master branch)
- Version tags (like `0.1.1`, `0.1.2`) for specific versions

The following architectures are supported by the Docker image:
- `linux/amd64`
- `linux/i386`
- `linux/arm64`
- `linux/arm/v7`
- `linux/ppc64le`

### Without Docker

If you know how to deploy a Python ASGI application, you can also deploy it directly without Docker.

For example, with [uvicorn](https://uvicorn.org/):
1. Make sure Python >=3.13 is installed on your system as it's the minimum version supported by eddrit.
2. Install [Poetry](https://python-poetry.org/) which is used to manage dependencies of the project.
3. Download/clone the repository and run `poetry install --only main` to install the application.
4. You can then run the app through uvicorn, for example with the following command: `poetry run uvicorn eddrit.app:app`

### Configuration

The application can be configured through environment variables (if a `.env` file is present, it will also be read).

eddrit needs a [valkey](https://github.com/valkey-io/valkey) instance to work. You need specify the connection url with
the `VALKEY_URL` environment variable (or in your env file).

The following configuration parameters are also available:
- `DEBUG` (default is `false`): enable [starlette](https://www.starlette.io/) debug mode. Should not be needed outside of development.
- `LOG_LEVEL` (default is `WARNING`): only log if the message level is superior or equal to this level.
- `PROXY` (default is null): if set, requests to Reddit will be sent through the specified proxy. This can be used to bypass
IP-based blocks, for example if proxying the instance through Cloudflare WARP.

## Donations

If you wish to support the app, donations are possible on [Github Sponsors](https://github.com/sponsors/corenting/) or [here](https://corenting.fr/donate).

## Credits

- [Bootstrap Icons](https://icons.getbootstrap.com/) for the icons used in the frontend
- [dash.js](https://github.com/Dash-Industry-Forum/dash.js): library used for DASH videos in the frontend
- [Pico.css](https://picocss.com/): CSS framework used for the frontend
- [redlib](https://github.com/redlib-org/redlib): for the backend Android app spoofing code
- [Video.js](https://videojs.com/): the library used for the videos in the frontend
