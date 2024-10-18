from __future__ import annotations

import logging
import aiohttp
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from typing import Any, Dict, Optional

_LOGGER = logging.getLogger(__name__)

DOMAIN = "oura_ring"
OURA_SLEEP_URL = "https://api.ouraring.com/v2/usercollection/daily_sleep"
OURA_STRESS_URL = "https://api.ouraring.com/v2/usercollection/daily_stress"
OURA_SLEEP_TIME_URL = "https://api.ouraring.com/v2/usercollection/sleep_time"
OURA_ACTIVITY_URL = "https://api.ouraring.com/v2/usercollection/daily_activity"
OURA_READINESS_URL = "https://api.ouraring.com/v2/usercollection/daily_readiness"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Oura Ring sensors from a config entry."""
    token = entry.data["access_token"]

    sensors = [
        OuraRingSensor(token, "sleep", OURA_SLEEP_URL),
        OuraRingSensor(token, "activity", OURA_ACTIVITY_URL),
        OuraRingSensor(token, "readiness", OURA_READINESS_URL),
        OuraRingSensor(token, "stress", OURA_STRESS_URL),
        OuraRingSensor(token, "sleep_time", OURA_SLEEP_TIME_URL)
    ]

    async_add_entities(sensors, True)

class OuraRingSensor(SensorEntity):
    """Representation of an Oura Ring sensor."""

    def __init__(self, token: str, sensor_type: str, url: str) -> None:
        """Initialize the sensor."""
        self._attr_native_value: StateType = None
        self._token = token
        self._sensor_type = sensor_type
        self._attr_name = f"Oura Ring {sensor_type.capitalize()}"
        self._attr_unique_id = f"oura_ring_{sensor_type}"
        self._attr_extra_state_attributes: Dict[str, Any] = {}
        self._url = url
        self._attr_available = True

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        headers = {"Authorization": f"Bearer {self._token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._attr_extra_state_attributes = data
                        await self._extract_state(data)
                        self._attr_available = True
                    else:
                        _LOGGER.error(
                            "Failed to fetch Oura %s data: %s",
                            self._sensor_type,
                            response.status,
                        )
                        self._attr_available = False
        except aiohttp.ClientError as error:
            _LOGGER.error(
                "Error fetching Oura Ring data: %s",
                error,
            )
            self._attr_available = False

    async def _extract_state(self, data: Dict[str, Any]) -> None:
        """Extract the state value from the data."""
        try:
            if self._sensor_type in ["sleep", "activity", "readiness", "stress", "sleep_time"]:
                self._attr_native_value = data.get("data", [])[0].get("score")
        except (KeyError, IndexError) as error:
            _LOGGER.error(
                "Error extracting state from Oura Ring data: %s",
                error,
            )
            self._attr_native_value = None
