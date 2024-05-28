# Version 0.8.6

- Sticky posts now have a green title

# Version 0.8.5

- Docker image: add more architectures
- Small bugfixes
- Update dependencies

# Version 0.8.4

- For the popular page, set the geo filter to "everywhere"
- Update dependencies

# Version 0.8.3

- Spoof the official Android app to bypass rate-limiting. Thanks to [redlib](https://github.com/redlib-org/redlib) for the Android app spoofing code.

# Version 0.8.2

- Fix settings cookies expiration as reported by [ValiumBear](https://github.com/ValiumBear) in [#143](https://github.com/corenting/eddrit/issues/143)
- Fix search page not working

# Version 0.8.1

- Fix galleries without captions

# Version 0.8.0

- Add layout settings to toggle between the existing wide layout or a more compact and centered layout. Thanks to [ValiumBear](https://github.com/ValiumBear) for the [suggestion](https://github.com/corenting/eddrit/issues/133)
- Add caption to gallery posts

# Version 0.7.0

- Fix pictures galleries buttons being enabled by mistake for first and last item
- Add /user/ pages

# Version 0.6.5

- Remove sorting option "gilded" as reddit removed awards
- Updated [Pico CSS](https://v2.picocss.com/) to v2

# Version 0.6.4

- Query old.reddit.com instead of www.reddit.com to avoid blocking

# Version 0.6.3

- Fix gallery pictures being out of order. Thanks to [jedicobra](https://github.com/jedicobra) for the [PR](https://github.com/corenting/eddrit/pull/114).

# Version 0.6.2

- Fix layout issue for embed content

# Version 0.6.1

- Remove special code for gfycat as it is shutting down soon
- Update httpx usage to enable http2 and connection pooling

# Version 0.6.0

- Add error message when the instance is rate-limited by Reddit
