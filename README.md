<div align="center">

<image src="static/images/logo.svg" height="80">

<hr>

A lightweight alternative frontend for Reddit.

![GitHub Tag](https://img.shields.io/github/v/tag/corenting/eddrit?label=latest)
![Build](https://img.shields.io/github/actions/workflow/status/corenting/eddrit/ci.yml?branch=master)
![License](https://img.shields.io/github/license/corenting/eddrit)

<a href="https://eddrit.com"><img src="https://raw.githubusercontent.com/corenting/eddrit/master/doc/screenshots/subreddit.png" width="80%"></a>

</div>

> **🌍 Official demo instance**: [eddrit.com](https://eddrit.com)

- Lightweight, with no ads
- Compact design inspired by [old.reddit.com](https://old.reddit.com) rather than the redesign
- Mobile-friendly
- No OAuth2 registration needed for self-hosting: mimics the official Android app by default to bypass rate-limiting
- Basic RSS support for subreddits and posts: fetches the original feed from Reddit and rewrites URLs to point to the current eddrit instance

URLs follow the same structure as Reddit, so you can simply replace `reddit.com` with `eddrit.com` to open any page in eddrit.

## Donations

If you wish to support the app, donations are possible on [Github Sponsors](https://github.com/sponsors/corenting/) or [here](https://corenting.fr/donate).

## Deployment (self-hosting)

To setup and configure your own instance, see the [deployment documentation](./doc/deployment/README.md).

## Development

For local development instructions, see the [development documentation](./doc/dev.md).

## Credits

eddrit is inspired by [Nitter](https://github.com/zedeus/nitter), an alternative frontend for Twitter.

- [Bootstrap Icons](https://icons.getbootstrap.com/) for the icons
- [dash.js](https://github.com/Dash-Industry-Forum/dash.js) for DASH video playback
- [Pico.css](https://picocss.com/) as the CSS framework
- [redlib](https://github.com/redlib-org/redlib) for the Android app spoofing code
- [Video.js](https://videojs.com/) for video playback
