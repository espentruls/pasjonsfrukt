import re
from pathlib import Path
from podme_api import PodMeClient
from ..config import Config

def build_podcast_dir(config: Config, slug: str):
    return Path(config.yield_dir) / slug


def build_podcast_feed_path(config: Config, slug: str):
    return (
        build_podcast_dir(config, slug) / f"{config.podcasts.get(slug).feed_name}.xml"
    )


def build_podcast_episode_file_path(config: Config, podcast_slug: str, episode_id: int):
    return build_podcast_dir(config, podcast_slug) / f"{episode_id}.mp3"

async def harvested_episode_ids(client: PodMeClient, config: Config, slug: str):
    podcast_dir = build_podcast_dir(config, slug)
    if not podcast_dir.is_dir():
        # no directory, so clearly no harvested episodes
        return []
    episode_ids = await client.get_episode_ids(slug)
    harvested = []
    for f in podcast_dir.iterdir():
        if not f.is_file():
            continue
        m = re.match(r"(.*)\.mp3$", f.name)
        if m is not None:
            episode_id = int(m.group(1))
            if episode_id in episode_ids:
                harvested.append(episode_id)
    return harvested
