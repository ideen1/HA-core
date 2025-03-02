"""API for YouTube bound to Home Assistant OAuth."""
from aiohttp import ClientSession
from google.oauth2.credentials import Credentials
from google.oauth2.utils import OAuthClientAuthHandler
from googleapiclient.discovery import Resource, build

from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow


class AsyncConfigEntryAuth(OAuthClientAuthHandler):
    """Provide Google authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        hass: HomeAssistant,
        websession: ClientSession,
        oauth2_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize YouTube Auth."""
        self.oauth_session = oauth2_session
        self.hass = hass
        super().__init__(websession)

    @property
    def access_token(self) -> str:
        """Return the access token."""
        return self.oauth_session.token[CONF_ACCESS_TOKEN]

    async def check_and_refresh_token(self) -> str:
        """Check the token."""
        await self.oauth_session.async_ensure_token_valid()
        return self.access_token

    async def get_resource(self) -> Resource:
        """Create executor job to get current resource."""
        credentials = Credentials(await self.check_and_refresh_token())
        return await self.hass.async_add_executor_job(self._get_resource, credentials)

    def _get_resource(self, credentials: Credentials) -> Resource:
        """Get current resource."""
        return build(
            "youtube",
            "v3",
            credentials=credentials,
        )
