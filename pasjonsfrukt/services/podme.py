import contextlib
from datetime import datetime, timedelta, timezone

from podme_api import (
    PodMeDefaultAuthClient,
    PodMeUserCredentials,
    PodMeClient,
)
from podme_api.auth.models import SchibstedCredentials

from ..config import Auth
from .interfaces import PodcastClient

@contextlib.asynccontextmanager
async def get_podme_client(auth: Auth) -> PodcastClient:
    user_creds = None
    if auth.email and auth.password:
        user_creds = PodMeUserCredentials(email=auth.email, password=auth.password)

    # Disable credentials storage if using env vars to avoid overwriting manually set credentials
    # or to prevent saving/loading invalid credentials from disk.
    client = PodMeClient(
        auth_client=PodMeDefaultAuthClient(
            user_credentials=user_creds
        ),
        request_timeout=30,
        disable_credentials_storage=True,
    )

    if auth.access_token:
        # Manually set credentials from config
        # We assume the token is valid for at least 1 hour if not specified
        # If refresh_token is provided, the client will attempt to refresh when expired
        creds = SchibstedCredentials(
            access_token=auth.access_token,
            refresh_token=auth.refresh_token or "",
            id_token="dummy",
            token_type="Bearer",
            expires_in=3600,
            scope="openid offline_access",
            expiration_time=datetime.now(tz=timezone.utc) + timedelta(hours=1)
        )
        client.auth_client.set_credentials(creds)

    try:
        await client.__aenter__()
        yield client
    finally:
        await client.__aexit__(None, None, None)
