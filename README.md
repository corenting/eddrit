# eddrit

![Build](https://img.shields.io/github/checks-status/corenting/eddrit/master?label=build) ![License](https://img.shields.io/github/license/corenting/eddrit) ![Codecov](https://img.shields.io/codecov/c/github/corenting/eddrit)

An alternative frontend for Reddit, written with Python + [Starlette](https://www.starlette.io/). Inspired by [Nitter](https://github.com/zedeus/nitter), an alternative frontend for Twitter

- Lightweight
- No ads
- Compact design (closer to [old.reddit.com](https://old.reddit.com) than to the redesign)
- Mobile support (responsive design)
- Use the old `.json` APIs, no need to register for an OAuth2 identifier

## Screenshots

![Subreddit view](https://raw.githubusercontent.com/corenting/eddrit/master/doc/screenshots/subreddit.png)

![Thread view](https://raw.githubusercontent.com/corenting/eddrit/master/doc/screenshots/thread.png)


## Installation

### Docker

A Docker image is available on [Docker Hub](https://hub.docker.com/r/corentingarcia/eddrit).
There are multiple tags:
- `latest` for the latest stable tagged release
- `master` for the latest commit on the master branch
- Version tags (like `0.1.1`, `0.1.2`) for specific versions

### Without Docker

You can run the app with gunicorn directly :
1. Make sure Python >= 3.11 is installed on your system.
2. Install [Poetry](https://python-poetry.org/) which is used to manage dependencies of the project.
3. Download the repository and run "make init" to install the dependencies.
4. You can then run the app through gunicorn, for example with the following command: `poetry run gunicorn eddrit.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080]`

## Credits

- [Bootstrap Icons](https://icons.getbootstrap.com/) for the icons used
- [dash.js](https://github.com/Dash-Industry-Forum/dash.js) for playing videos
- [Pico.css](https://picocss.com/) for the CSS framework used
- [Video.js](https://videojs.com/) for playing videos
