# Version 0.10.0

- Add support for galleries with GIFs
- Better links previews when sharing links for posts with GIFs or videos
- Various fixes:
    - Fix Firefox loading the pictures from all the posts in a subreddit or user posts list view, even if they were hidden.
    - Fix comments sometimes overflowing on mobile, which resulted in an horizontal scroll appearing
    - Fix some Twitch links displayed as pictures instead of using the embedded player
    - On posts with a pictures gallery, only load the image from the current tab, and not all of them and fix the previous button being enabled on the first picture
    - On a user page, fix links to comments on "Full comments" links

# Version 0.9.6

- Better display of comments on a post page
- Add RSS feeds for frontpage

# Version 0.9.5

- Add basic RSS support (for subreddits and posts): fetch the original RSS feed from Reddit, and rewrite the URLs to point to the current eddrit instance.
- Add support for posts on users profiles

# Version 0.9.4

- Fix issue with sorting parameters not working

# Version 0.9.3

- Fix issue with settings not saving
- Fix displayed post title being too long
- Add opengraph tags for better links previews when sharing eddrit links

# Version 0.9.2

- Use cookies for theme so that it works without Javascript + avoid flash of theme change on reloads
- Rename "popular" sorting mode to "hot" like on Reddit
- Fix display of settings link button
- Add wiki link to subreddit if available
- Fix r/<subreddit>/wiki links not working

# Version 0.9.1

- Fix frontpage geo filter not being set, resulting in the instance country being used. It now uses the "global" geofilter

# Version 0.9.0

- Added basic wiki support (fix #215)

# Version 0.8.9

- Update User-Agent used for Reddit requests

# Version 0.8.8

- Avoid Reddit rate-limiting by refreshing the credentials used if needed

# Version 0.8.7

- Fix multireddits not loading

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
