# eddrit

![Build](https://img.shields.io/travis/com/corenting/eddrit/master) ![License](https://img.shields.io/github/license/corenting/eddrit) ![Codecov](https://img.shields.io/codecov/c/github/corenting/eddrit)

An alternative frontend for Reddit, written with Python + [Starlette](https://www.starlette.io/). Inspired by [Nitter](https://github.com/zedeus/nitter), an alternative frontend for Twitter

- Lightweight
- No ads
- Compact design (closer to [old.reddit.com](https://old.reddit.com) than to the redesign)
- Mobile support (responsive design)
- Use the old `.json` APIs, no need for OAuth2 identifier

## Screenshots

![Subreddit view](doc/screenshots/subreddit.png)

![Thread view](doc/screenshots/subreddit.png)


## Installation

### Docker
A Docker image is available on [Docker Hub](https://hub.docker.com/r/corentingarcia/eddrit).

### Without Docker

You can run the app with gunicorn directly :
1. Make sure Python >= 3.8 is installed on your system.
2. Install [Poetry](https://python-poetry.org/) which is used to manage dependencies of the project.
3. Download the repository and run "make init" to install the dependencies.
4. You can then run the app through gunicorn, for example with the following command: `poetry run gunicorn eddrit.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080]`
