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

def setup_platform(hass, config, add_entities, discovery_info=None):
    token = config.get('access_token')
    if not token:
        _LOGGER.error("Oura Ring access token is missing")
        return
    
    sensors = [
        OuraRingSensor(token, "sleep"),
        OuraRingSensor(token, "activity"),
        OuraRingSensor(token, "readiness"),
        OuraRingSensor(token, "stress"),
        OuraRingSensor(token, "sleep_time")
    ]
    
    add_entities(sensors, True)

class OuraRingSensor(Entity):
    def __init__(self, token, sensor_type):
        self._state = None
        self._token = token
        self._sensor_type = sensor_type
        self._name = f"Oura Ring {sensor_type.capitalize()}"
        self._data = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        headers = {"Authorization": f"Bearer {self._token}"}

        # Match URL based on the sensor type
        if self._sensor_type == "sleep":
            url = OURA_SLEEP_URL
        elif self._sensor_type == "activity":
            url = OURA_ACTIVITY_URL
        elif self._sensor_type == "readiness":
            url = OURA_READINESS_URL
        elif self._sensor_type == "stress":
            url = OURA_STRESS_URL
        elif self._sensor_type == "sleep_time":
            url = OURA_SLEEP_TIME_URL
        else:
            _LOGGER.error(f"Unknown sensor type: {self._sensor_type}")
            return
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            self._data = data
            self._state = self.extract_state(data)
        elif response.status_code == 404:
            _LOGGER.error(f"URL not found for {self._sensor_type}: {url}")
        else:
            _LOGGER.error(f"Failed to fetch Oura {self._sensor_type} data: {response.status_code} - {response.text}")

    def extract_state(self, data):
        if self._sensor_type == "sleep":
            sleep_data = data.get("data", [])
            if sleep_data:
                latest_sleep = sleep_data[0]  # assuming the most recent data is first
                return latest_sleep.get("score")
        elif self._sensor_type == "activity":
            activity_data = data.get("data", [])
            if activity_data:
                latest_activity = activity_data[0]
                return latest_activity.get("score")
        elif self._sensor_type == "readiness":
            readiness_data = data.get("data", [])
            if readiness_data:
                latest_readiness = readiness_data[0]
                return latest_readiness.get("score")
        elif self._sensor_type == "stress":
            stress_data = data.get("data", [])
            if stress_data:
                latest_stress = stress_data[0]
                return latest_stress.get("score")
        elif self._sensor_type == "sleep_time":
            sleep_time_data = data.get("data", [])
            if sleep_time_data:
                latest_sleep_time = sleep_time_data[0]
                return latest_sleep_time.get("total_sleep_time")  # Example field, modify based on API response
        return None
