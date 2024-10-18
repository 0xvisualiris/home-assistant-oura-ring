import requests
import logging
from homeassistant.helpers.entity import Entity

DOMAIN = "oura_ring"
OURA_SLEEP_URL = "https://api.ouraring.com/v2/usercollection/daily_sleep"
OURA_STRESS_URL = "https://api.ouraring.com/v2/usercollection/daily_stress"
OURA_SLEEP_TIME_URL = "https://api.ouraring.com/v2/usercollection/sleep_time"
OURA_ACTIVITY_URL = "https://api.ouraring.com/v2/usercollection/daily_activity"
OURA_READINESS_URL = "https://api.ouraring.com/v2/usercollection/daily_readiness"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
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
    def __init__(self, token, sensor_type, url):
        self._state = None
        self._token = token
        self._sensor_type = sensor_type
        self._name = f"Oura Ring {sensor_type.capitalize()}"
        self._data = {}
        self._url = url

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        headers = {"Authorization": f"Bearer {self._token}"}
        response = requests.get(self._url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            self._data = data
            self._state = self.extract_state(data)
        else:
            _LOGGER.error(f"Failed to fetch Oura {self._sensor_type} data: {response.status_code}")

    def extract_state(self, data):
        if self._sensor_type in ["sleep", "activity", "readiness", "stress", "sleep_time"]:
            return data.get("data", [])[0].get("score")  # Adjust if needed based on API response fields
        return None
