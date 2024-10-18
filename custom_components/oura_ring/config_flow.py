import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from . import DOMAIN

class OuraRingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oura Ring."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            token = user_input["access_token"]
            # You could validate the token here if needed
            return self.async_create_entry(title="Oura Ring", data=user_input)
        
        # Create the form for user input
        data_schema = vol.Schema({
            vol.Required("access_token"): str
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OuraRingOptionsFlowHandler(config_entry)

class OuraRingOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Oura Ring options."""

    def __init__(self, config_entry):
        """Initialize OuraRingOptionsFlowHandler."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Required("access_token", default=self.config_entry.data.get("access_token")): str,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
