from dataclasses import dataclass
from io import TextIOWrapper
from typing import Optional
from pathlib import Path
import os

from dataclass_wizard import YAMLWizard


@dataclass
class Auth:
    email: Optional[str] = None
    password: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


@dataclass
class Podcast:
    feed_name: str = "feed"
    most_recent_episodes_limit: Optional[int] = None


@dataclass
class Config(YAMLWizard):
    host: str
    auth: Auth
    podcasts: dict[
        str, Optional[Podcast]
    ]  # Podcast is not actually optional, see __post_init__
    yield_dir: str = "yield"
    secret: Optional[str] = None

    def __post_init__(self):
        # All Podcast properties are currently optional, but default values need to be initialized
        # This allows the YAML config to specify a podcast without an otherwise required empty object ("{}")
        self.podcasts = {
            k: (v if v is not None else Podcast(feed_name=k)) for k, v in self.podcasts.items()
        }


def config_from_stream(stream: Optional[TextIOWrapper]) -> Config:
    config = None
    if stream:
        try:
            config = Config.from_yaml(stream)
        except (TypeError, ValueError):
            # TypeError occurs if file is empty (NoneType is not iterable)
            # Proceed to use defaults/env vars
            pass

    if config is None:
        # Defaults if no file or empty file
        config = Config(
            host="http://localhost",
            auth=Auth(),
            podcasts={},
            yield_dir="yield"
        )

    # Override from Env Vars
    if os.environ.get("PODME_EMAIL"):
        config.auth.email = os.environ.get("PODME_EMAIL")
    if os.environ.get("PODME_PASSWORD"):
        config.auth.password = os.environ.get("PODME_PASSWORD")
    if os.environ.get("PODME_ACCESS_TOKEN"):
        config.auth.access_token = os.environ.get("PODME_ACCESS_TOKEN")
    if os.environ.get("PODME_REFRESH_TOKEN"):
        config.auth.refresh_token = os.environ.get("PODME_REFRESH_TOKEN")
    if os.environ.get("PODME_YIELD_DIR"):
        config.yield_dir = os.environ.get("PODME_YIELD_DIR")
    if os.environ.get("PODME_HOST"):
        config.host = os.environ.get("PODME_HOST")

    # Podcasts from Env Var (comma separated slugs)
    if os.environ.get("PODME_PODCASTS"):
        slugs = os.environ.get("PODME_PODCASTS").split(",")
        for slug in slugs:
            slug = slug.strip()
            if slug and slug not in config.podcasts:
                config.podcasts[slug] = Podcast(feed_name=slug)

    # Podcasts from File (PODME_PODCASTS_FILE)
    podcasts_file_path = os.environ.get("PODME_PODCASTS_FILE")
    if podcasts_file_path and os.path.isfile(podcasts_file_path):
        with open(podcasts_file_path, "r") as f:
            for line in f:
                slug = line.strip()
                if slug and not slug.startswith("#") and slug not in config.podcasts:
                    config.podcasts[slug] = Podcast(feed_name=slug)

    return config
