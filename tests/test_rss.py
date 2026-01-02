from unittest.mock import MagicMock
from datetime import datetime, time
from pasjonsfrukt.config import Config
from pasjonsfrukt.services.rss import build_feed, get_secret_query_parameter
from podme_api import PodMeEpisode

def test_get_secret_query_parameter_none():
    config = Config(host="http://localhost", auth=None, podcasts={}, secret=None)
    assert get_secret_query_parameter(config) == ""

def test_get_secret_query_parameter_exists():
    config = Config(host="http://localhost", auth=None, podcasts={}, secret="shh")
    assert get_secret_query_parameter(config) == "?secret=shh"

def test_build_feed_structure():
    config = Config(host="http://example.com", auth=None, podcasts={}, secret="123")
    episodes = [
        PodMeEpisode(
            id=1,
            podcast_id=10,
            title="Ep 1",
            podcast_title="Title",
            description="Desc 1",
            length=time(0, 10, 0),
            date_added=datetime(2023, 1, 1),
            author_full_name="Author",
            small_image_url="img",
            medium_image_url="img",
            # large_image_url="img", # Removed invalid argument
            image_url="img",
            stream_url="url",
            is_premium=True,
            only_as_package_subscription=False
        )
    ]

    # Mock file size check since it touches filesystem

    from unittest.mock import patch
    with patch("pasjonsfrukt.services.rss.build_podcast_episode_file_path") as mock_path_builder:
        mock_path = MagicMock()
        mock_path.stat.return_value.st_size = 5000
        mock_path_builder.return_value = mock_path

        rss_xml = build_feed(config, episodes, "slug", "Title", "Desc", "img.jpg")

        assert "Ep 1" in rss_xml
        assert "http://example.com/slug/1?secret=123" in rss_xml
        assert 'length="5000"' in rss_xml
