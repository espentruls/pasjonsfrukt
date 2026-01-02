from rfeed import Item, Guid, Enclosure, Feed, Image, iTunesItem, iTunes
from podme_api import PodMeEpisode
from ..config import Config
from .storage import build_podcast_episode_file_path

def get_secret_query_parameter(config: Config):
    if config.secret is None:
        return ""  # no secret required, so don't append query parameter
    return f"?secret={config.secret}"

def build_feed(
    config: Config,
    episodes: list[PodMeEpisode],
    slug: str,
    title: str,
    description: str,
    image_url: str,
):
    secret_query_param = get_secret_query_parameter(config)
    items = []
    for e in episodes:
        episode_id = e.id
        episode_path = f"{slug}/{episode_id}"
        items.append(
            Item(
                title=e.title,
                description=e.description,
                guid=Guid(episode_id, isPermaLink=False),
                enclosure=Enclosure(
                    url=f"{config.host}/{episode_path}{secret_query_param}",
                    type="audio/mpeg",
                    length=build_podcast_episode_file_path(config, slug, episode_id)
                    .stat()
                    .st_size,
                ),
                pubDate=e.date_added,
                extensions=[
                    iTunesItem(
                        author=e.author_full_name,
                        duration=e.length,
                    )
                ],
            )
        )
    feed_link = f"{config.host}/{slug}{secret_query_param}"
    feed = Feed(
        title=title,
        link=feed_link,
        description=description,
        language="no",
        image=Image(url=image_url, title=title, link=feed_link),
        items=sorted(items, key=lambda i: i.pubDate, reverse=True),
        extensions=[iTunes(block="Yes")],
    )
    return feed.rss()
