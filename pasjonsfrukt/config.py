from dataclasses import dataclass
from io import TextIOWrapper
from typing import Optional
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
            k: (v if v is not None else Podcast()) for k, v in self.podcasts.items()
        }


def config_from_stream(stream: TextIOWrapper) -> Optional[Config]:
    config = Config.from_yaml(stream)

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

    return config
