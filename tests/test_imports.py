import pytest
from pasjonsfrukt.services.interfaces import EpisodeInfo, PodcastClient
from pasjonsfrukt.harvester import harvest_podcast

def test_imports():
    """Verify that modules can be imported without TypeErrors."""
    assert EpisodeInfo
    assert PodcastClient
    assert harvest_podcast
