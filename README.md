# 🍹 pasjonsfrukt

[![PyPI](https://img.shields.io/pypi/v/pasjonsfrukt)](https://pypi.org/project/pasjonsfrukt/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pasjonsfrukt)
[![PyPI - License](https://img.shields.io/pypi/l/pasjonsfrukt)](https://github.com/mathiazom/pasjonsfrukt/blob/main/LICENSE)

Scrape PodMe podcast streams to mp3 and host with RSS feed.

<i style="color:grey">Note: A valid PodMe subscription is required to access premium content</i>

### Setup

1. Install `pasjonsfrukt`

```
pip install pasjonsfrukt
```

2. Install [`ffmpeg`](https://ffmpeg.org/)

3. Define harvest and feed configurations by copying [`config.template.yaml`](config.template.yaml) to your own `config.yaml`.  
   Most importantly, you need to provide:

   - a `host` path (for links in the RSS feeds)
   - login credentials (`auth`) for your PodMe account
   - the `podcasts` you wish to harvest and serve

### Usage

##### Harvest episodes

Harvest episodes of all podcasts defined in config

```sh
pasjonsfrukt harvest
```

Harvest episodes of specific podcast(s)

```sh
pasjonsfrukt harvest [PODCAST_SLUG]...
```

##### Update feeds

Update all RSS feeds defined in config

```sh
pasjonsfrukt sync
```

Update RSS feed of specific podcast

```sh
pasjonsfrukt sync [PODCAST_SLUG]...
```

> The feeds are always updated after harvest, so manual feed syncing is only required if files are changed externally

##### Serve RSS feeds with episodes

Run web server

```sh
pasjonsfrukt serve
```

RSS feeds will be served at `<host>/<podcast_slug>`, while episode files are served
at `<host>/<podcast_slug>/<episode_id>`

> `host` must be defined in the config file.

##### Secret

If a `secret` has been defined in the config, a query parameter (`?secret=<secret-string>`) with matching secret string
is required to access the served podcast feeds and episode files. This is useful for making RSS feeds accessible on the
web, without making them fully public. Still, the confidentiality is provided as is, with no warranties 🙃

### Docker

You can run `pasjonsfrukt` using Docker, which is recommended for continuous harvesting and serving. The image is built automatically on GitHub.

#### Environment Variables

-   `PUID`: User ID to run as (e.g., `99` for Unraid nobody).
-   `PGID`: Group ID to run as (e.g., `100` for Unraid users).
-   `ENABLE_SERVER`: Set to `true` to enable the built-in RSS feed server. Defaults to `false` (only downloads episodes).
-   `PODME_EMAIL`: Override email from config.yaml.
-   `PODME_PASSWORD`: Override password from config.yaml.
-   `PODME_ACCESS_TOKEN`: Override access token (for bypassing login issues).
-   `PODME_REFRESH_TOKEN`: Override refresh token.

#### Unraid / Docker Run

Run the container mapping your config and download directory. Using a `/config` volume allows you to store `config.yaml` and access logs easily.

```sh
docker run -d \
  --name pasjonsfrukt \
  -e PUID=99 \
  -e PGID=100 \
  -e ENABLE_SERVER=false \
  -e PODME_EMAIL="your@email.com" \
  -e PODME_PASSWORD="yourpassword" \
  -v /mnt/user/appdata/pasjonsfrukt/yield:/app/yield \
  -v /mnt/user/appdata/pasjonsfrukt:/config \
  ghcr.io/espentruls/pasjonsfrukt:latest
```

**Configuration:**
-   Place your `config.yaml` in `/mnt/user/appdata/pasjonsfrukt/`.
-   Logs will be available at `/mnt/user/appdata/pasjonsfrukt/pasjonsfrukt.log`.
-   By default, it runs harvest every hour. If you want a custom schedule, place a file named `pasjonsfrukt-crontab` in `/mnt/user/appdata/pasjonsfrukt/` (mapped to `/etc/cron.d/pasjonsfrukt-crontab`).

**Note on Authentication:**
If standard login fails (HTTP 400), you can manually extract your session tokens from the PodMe website (via browser Developer Tools > Application > Cookies/Storage) and provide them via `PODME_ACCESS_TOKEN` and `PODME_REFRESH_TOKEN` environment variables.

### Development

#### Formatting

```commandline
poe fmt
```
> uses [Black](https://black.readthedocs.io/en/stable/) code formatter
