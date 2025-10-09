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

If you wish to setup and configure your instance, please check [this](./doc/deployment/README.md) documentation.

## Donations

If you wish to support the app, donations are possible on [Github Sponsors](https://github.com/sponsors/corenting/) or [here](https://corenting.fr/donate).

## Credits

- [Bootstrap Icons](https://icons.getbootstrap.com/) for the icons used in the frontend
- [dash.js](https://github.com/Dash-Industry-Forum/dash.js): library used for DASH videos in the frontend
- [Pico.css](https://picocss.com/): CSS framework used for the frontend
- [redlib](https://github.com/redlib-org/redlib): for the backend Android app spoofing code
- [Video.js](https://videojs.com/): the library used for the videos in the frontend
