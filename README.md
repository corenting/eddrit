# eddrit

![Build](https://img.shields.io/github/actions/workflow/status/corenting/eddrit/ci.yml?branch=master) ![License](https://img.shields.io/github/license/corenting/eddrit) ![Codecov](https://img.shields.io/codecov/c/github/corenting/eddrit)

An alternative frontend for Reddit. Inspired by [Nitter](https://github.com/zedeus/nitter), an alternative frontend for Twitter.

Written with Python + [Starlette](https://www.starlette.io/).

- Lightweight
- No ads
- Compact design (closer to [old.reddit.com](https://old.reddit.com) than to the redesign)
- Better mobile support
- No need to register for an OAuth2 identifier for self-hosting: mimic the official Android app by default

Official instance: [eddrit.com](https://eddrit.com)

## ⚠️ Rate-limiting

By default, eddrit will mimic the official Android app to bypass the rate-limiting (huge thanks to [redlib](https://github.com/redlib-org/redlib) for the implementation).

If you want to use the .json endpoints directly (**you may encounter rate-limiting or be blocked from Reddit**), you can set the environment variable `SPOOFED_CLIENT` (directly or through an environment variable) to `none`.

## Screenshots

![Subreddit view](https://raw.githubusercontent.com/corenting/eddrit/master/doc/screenshots/subreddit.png)

![Thread view](https://raw.githubusercontent.com/corenting/eddrit/master/doc/screenshots/thread.png)

## Installation

### Docker

A Docker image is available on [Docker Hub](https://hub.docker.com/r/corentingarcia/eddrit) and on [ghcr.io](https://github.com/corenting/eddrit/pkgs/container/eddrit).

There are multiple tags:
- `latest` for the latest stable tagged release
- `dev` for the latest commit on the master branch
- Version tags (like `0.1.1`, `0.1.2`) for specific versions

The image supports linux/amd64 or linux/arm64 architectures.

### Without Docker

You can run the app with gunicorn directly :
1. Make sure Python >= 3.12 is installed on your system.
2. Install [Poetry](https://python-poetry.org/) which is used to manage dependencies of the project.
3. Download the repository and run "make init" to install the dependencies.
4. You can then run the app through gunicorn, for example with the following command: `poetry run gunicorn eddrit.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080`

## Donations

If you wish to support the app, donations are possible [here](https://corenting.fr/donate).

## Credits

- [Bootstrap Icons](https://icons.getbootstrap.com/) for the icons used
- [dash.js](https://github.com/Dash-Industry-Forum/dash.js) for playing videos
- [Pico.css](https://picocss.com/) for the CSS framework used
- [redlib](https://github.com/redlib-org/redlib) for the Android app spoofing code
- [Video.js](https://videojs.com/) for playing videos
