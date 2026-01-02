from typing import Protocol, List, Tuple
from datetime import datetime

class EpisodeInfo:
    # Minimal interface for what we use from PodMeEpisode
    id: int
    title: str
    description: str
    date_added: datetime
    author_full_name: str
    length: str | datetime.time # PodMeEpisode has time, but we might want flexibility

class PodcastClient(Protocol):
    async def get_episode_list(self, slug: str) -> List[any]:
        ...

    async def get_latest_episodes(self, slug: str, limit: int) -> List[any]:
        ...

    async def get_episode_ids(self, slug: str) -> List[int]:
        ...

    async def get_episode_download_url_bulk(self, episode_ids: List[int]) -> List[Tuple[int, str]]:
        ...

    async def download_files(self, download_infos: List[Tuple[str, str]], on_progress=None, on_finished=None):
        ...

    async def get_episodes_info(self, episode_ids: List[int]) -> List[any]:
        ...

    async def get_podcast_info(self, slug: str) -> any:
        ...
