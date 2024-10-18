import logging
import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from typing import Any, Dict, Optional

DOMAIN = "oura_ring"
OURA_SLEEP_URL = "https://api.ouraring.com/v2/usercollection/daily_sleep"
OURA_STRESS_URL = "https://api.ouraring.com/v2/usercollection/daily_stress"
OURA_SLEEP_TIME_URL = "https://api.ouraring.com/v2/usercollection/sleep_time"
OURA_ACTIVITY_URL = "https://api.ouraring.com/v2/usercollection/daily_activity"
OURA_READINESS_URL = "https://api.ouraring.com/v2/usercollection/daily_readiness"

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Oura Ring sensors from a config entry."""
    token = config_entry.data["access_token"]
    sensors = [
        OuraRingSensor(token, "sleep", OURA_SLEEP_URL),
        OuraRingSensor(token, "activity", OURA_ACTIVITY_URL),
        OuraRingSensor(token, "readiness", OURA_READINESS_URL),
        OuraRingSensor(token, "stress", OURA_STRESS_URL),
        OuraRingSensor(token, "sleep_time", OURA_SLEEP_TIME_URL)
    ]
    async_add_entities(sensors, True)

class OuraRingSensor(Entity):
    """Representation of an Oura Ring sensor."""

    def __init__(self, token: str, sensor_type: str, url: str) -> None:
        """Initialize the sensor."""
        self._state: Optional[Any] = None
        self._token = token
        self._sensor_type = sensor_type
        self._name = f"Oura Ring {sensor_type.capitalize()}"
        self._attr_unique_id = f"oura_ring_{sensor_type}"
        self._data: Dict[str, Any] = {}
        self._url = url
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> Optional[Any]:
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self._data

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        headers = {"Authorization": f"Bearer {self._token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url, headers=headers) as response:
                    if response.status == 200:
                        self._data = await response.json()
                        self._state = await self.extract_state(self._data)
                        self._available = True
                    else:
                        LOGGER.error(
                            "Failed to fetch Oura %s data: %s",
                            self._sensor_type,
                            response.status,
                        )
                        self._available = False
        except aiohttp.ClientError as error:
            LOGGER.error(
                "Error fetching Oura Ring data: %s",
                error,
            )
            self._available = False

    async def extract_state(self, data: Dict[str, Any]) -> Optional[Any]:
        """Extract the state value from the data."""
        try:
            if self._sensor_type in ["sleep", "activity", "readiness", "stress", "sleep_time"]:
                return data.get("data", [])[0].get("score")
        except (KeyError, IndexError) as error:
            LOGGER.error(
                "Error extracting state from Oura Ring data: %s",
                error,
            )
            return None
        return None
