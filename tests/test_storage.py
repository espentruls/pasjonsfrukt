from unittest.mock import MagicMock
from pathlib import Path
from pasjonsfrukt.config import Config, Podcast
from pasjonsfrukt.services.storage import build_podcast_dir, build_podcast_feed_path, build_podcast_episode_file_path

def test_build_podcast_dir():
    config = Config(host="http://localhost", auth=None, podcasts={}, yield_dir="/tmp/yield")
    path = build_podcast_dir(config, "my-podcast")
    assert path == Path("/tmp/yield/my-podcast")

def test_build_podcast_feed_path():
    config = Config(host="http://localhost", auth=None, podcasts={"my-podcast": Podcast(feed_name="custom-feed")}, yield_dir="/tmp/yield")
    path = build_podcast_feed_path(config, "my-podcast")
    assert path == Path("/tmp/yield/my-podcast/custom-feed.xml")

def test_build_podcast_episode_file_path():
    config = Config(host="http://localhost", auth=None, podcasts={}, yield_dir="/tmp/yield")
    path = build_podcast_episode_file_path(config, "my-podcast", 123)
    assert path == Path("/tmp/yield/my-podcast/123.mp3")
