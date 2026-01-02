from podme_api import PodMeClient
from podme_api.models import PodMeDownloadProgressTask
from .services.interfaces import PodcastClient
from .config import Config
from .services.storage import (
    build_podcast_dir,
    build_podcast_feed_path,
    harvested_episode_ids,
)
from .services.rss import build_feed

async def harvest_podcast(client: PodcastClient, config: Config, slug: str):
    if slug not in config.podcasts:
        print(f"[FAIL] The slug '{slug}' did not match any podcasts in the config file")
        return
    most_recent_episodes_limit = config.podcasts[slug].most_recent_episodes_limit
    if most_recent_episodes_limit is None:
        episodes = await client.get_episode_list(slug)
    else:
        episodes = await client.get_latest_episodes(slug, most_recent_episodes_limit)

    if len(episodes) == 0:
        print(f"[WARN] Could not find any published episodes for '{slug}'")
        return

    published_ids = [e.id for e in episodes]
    harvested_ids = await harvested_episode_ids(client, config, slug)
    to_harvest = [e for e in published_ids if e not in harvested_ids]
    if len(to_harvest) == 0:
        print(
            f"[INFO] Nothing new from '{slug}', all available episodes already harvested"
            f"{f' (only looking at {most_recent_episodes_limit} most recent)' if most_recent_episodes_limit is not None else ''}"
        )
        return
    print(
        f"[INFO] Found {len(to_harvest)} new episode{'s' if len(to_harvest) > 1 else ''} of '{slug}' ready to harvest"
        f"{f' (only looking at {most_recent_episodes_limit} most recent)' if most_recent_episodes_limit is not None else ''}"
    )
    podcast_dir = build_podcast_dir(config, slug)
    podcast_dir.mkdir(parents=True, exist_ok=True)

    # harvest each missing episode
    download_urls = await client.get_episode_download_url_bulk(to_harvest)
    download_infos = [
        (url, podcast_dir / f"{episode_id}.mp3") for episode_id, url in download_urls
    ]

    def log_progress(_: PodMeDownloadProgressTask, url: str, progress: int, total: int):
        print(f"[INFO] Downloading from {url}: {progress}/{total}.")

    def log_finished(url: str, path: str):
        print(f"[INFO] Finished downloading {url} to {path}.")

    await client.download_files(
        download_infos, on_progress=log_progress, on_finished=log_finished
    )

    await sync_slug_feed(client, config, slug)


async def sync_slug_feed(client: PodcastClient, config: Config, slug: str):
    if slug not in config.podcasts:
        print(f"[FAIL] The slug '{slug}' did not match any podcasts in the config file")
        return
    print(f"[INFO] Syncing '{slug}' feed...")
    episode_ids = await harvested_episode_ids(client, config, slug)
    episodes = await client.get_episodes_info(episode_ids)
    podcast_info = await client.get_podcast_info(slug)
    feed = build_feed(
        config,
        episodes,
        slug,
        podcast_info.title,
        podcast_info.description,
        podcast_info.image_url,
    )
    build_podcast_dir(config, slug).mkdir(parents=True, exist_ok=True)
    with build_podcast_feed_path(config, slug).open("w", encoding="utf-8") as feed_file:
        feed_file.write(feed)
    print(
        f"[INFO] '{slug}' feed now serving {len(episodes)} episode{'s' if len(episodes) != 1 else ''}"
    )
