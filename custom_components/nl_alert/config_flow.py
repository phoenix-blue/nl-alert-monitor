"""Config flow for NL-Alert integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import (
    DOMAIN, 
    CONF_UPDATE_INTERVAL, 
    DEFAULT_UPDATE_INTERVAL,
    CONF_ENABLE_PLUME_CALC,
    CONF_WEATHER_SOURCE,
    CONF_WIND_SENSOR,
    CONF_WIND_DIRECTION_SENSOR,
    CONF_TEMPERATURE_SENSOR,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
    CONF_WEATHER_ENTITY,
)

_LOGGER = logging.getLogger(__name__)

def get_weather_entities(hass: HomeAssistant) -> dict[str, str]:
    """Get all available weather entities."""
    weather_entities = {}
    
    # Voeg een "geen" optie toe
    weather_entities[""] = "Geen weer entiteit (gebruik KNMI data)"
    
    # Zoek alle weather entiteiten
    for entity_id in hass.states.async_entity_ids("weather"):
        state = hass.states.get(entity_id)
        if state:
            # Gebruik friendly_name of entity_id als display naam
            friendly_name = state.attributes.get("friendly_name", entity_id)
            weather_entities[entity_id] = friendly_name
    
    # Voeg ook sensor entiteiten toe die geschikt zijn voor windsnelheid
    for entity_id in hass.states.async_entity_ids("sensor"):
        state = hass.states.get(entity_id)
        if state and state.attributes.get("device_class") in ["wind_speed", "temperature"]:
            friendly_name = state.attributes.get("friendly_name", entity_id)
            weather_entities[entity_id] = f"🌡️ {friendly_name}"
            
    return weather_entities

STEP_PLUME_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_WEATHER_SOURCE, default="knmi"): vol.In(["knmi", "sensors"]),
        vol.Optional(CONF_WIND_SENSOR): str,
        vol.Optional(CONF_WIND_DIRECTION_SENSOR): str, 
        vol.Optional(CONF_TEMPERATURE_SENSOR): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.
    
    TODO: Replace this with actual API connection validation.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO: validate the data can be used to set up a connection.
    
    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    hub = PlaceholderHub(data.get("host", "api.public-warning.app"))

    if not await hub.authenticate(data.get("username", ""), data.get("password", "")):
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "NL-Alert Integration"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NL-Alert."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return NLAlertOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        # Dynamisch schema met beschikbare weather entiteiten
        weather_entities = get_weather_entities(self.hass)
        
        data_schema = vol.Schema({
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): 
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=30, 
                        max=3600, 
                        step=30,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="seconden"
                    )
                ),
            vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): 
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["nl", "en"],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="language"
                    )
                ),
            vol.Optional(CONF_ENABLE_PLUME_CALC, default=False): bool,
            vol.Optional(CONF_WEATHER_ENTITY, default=""): 
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(weather_entities.keys()),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=True
                    )
                ),
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors,
            description_placeholders={
                "weather_entities": "\n".join([f"• {name}" for name in weather_entities.values()][:5])
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class NLAlertOptionsFlow(config_entries.OptionsFlow):
    """Handle NL-Alert options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the NL-Alert options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Haal huidige configuratie op
        current_config = {**self.config_entry.data, **self.config_entry.options}
        
        # Dynamisch schema met beschikbare weather entiteiten
        weather_entities = get_weather_entities(self.hass)
        
        options_schema = vol.Schema({
            vol.Optional(
                CONF_UPDATE_INTERVAL, 
                default=current_config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=30, 
                    max=3600, 
                    step=30,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="seconden"
                )
            ),
            vol.Optional(
                CONF_LANGUAGE, 
                default=current_config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=["nl", "en"],
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(
                CONF_ENABLE_PLUME_CALC, 
                default=current_config.get(CONF_ENABLE_PLUME_CALC, False)
            ): bool,
            vol.Optional(
                CONF_WEATHER_ENTITY, 
                default=current_config.get(CONF_WEATHER_ENTITY, "")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(weather_entities.keys()),
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True
                )
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
            description_placeholders={
                "current_weather": weather_entities.get(
                    current_config.get(CONF_WEATHER_ENTITY, ""), 
                    "Geen weer entiteit"
                )
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""