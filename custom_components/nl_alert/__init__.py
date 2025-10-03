"""
The NL-Alert integration for Home Assistant.

This integration provides real-time Dutch emergency alerts from NL-Alert system.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from datetime import datetime, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NL-Alert from a config entry."""
    _LOGGER.info("Setting up NL-Alert integration")
    
    # Import hier om circular imports te voorkomen
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    from .api import NLAlertAPI
    from .coordinator import NLAlertCoordinator
    
    # Store an instance of the "connecting" class
    hass.data.setdefault(DOMAIN, {})
    
    # Create API client and coordinator
    session = async_get_clientsession(hass)
    api = NLAlertAPI(session)
    
    # Combineer data en options voor coordinator
    config_data = {**entry.data, **entry.options}
    coordinator = NLAlertCoordinator(hass, api, config_data)
    
    # Store coordinator for platforms
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "config": config_data,
    }
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    
    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services after platforms are set up
    await asyncio.sleep(1)  # Give platforms time to initialize
    await _register_services(hass, coordinator)
    
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.info("Updating NL-Alert configuration")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading NL-Alert integration")
    
    # Unregister services
    hass.services.async_remove(DOMAIN, "test_alert")
    hass.services.async_remove(DOMAIN, "reset_alerts")
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def _register_services(hass: HomeAssistant, coordinator) -> None:
    """Register services for NL-Alert integration."""
    
    async def async_test_alert(call: ServiceCall) -> None:
        """Service to create a test alert."""
        _LOGGER.info("🧪 NL-Alert test alert service called")
        
        # Create test alert
        test_alert = {
            "identifier": "TEST-2024-001",
            "msgType": "Alert", 
            "scope": "Public",
            "status": "Actual",
            "sent": datetime.now(timezone.utc).isoformat(),
            "info": [{
                "language": "nl-NL",
                "category": "CBRN",
                "event": "🧪 TEST: Chemische stof vrijgekomen",
                "urgency": "Immediate",
                "severity": "Severe",
                "certainty": "Observed",
                "headline": "🧪 TEST MELDING - Rookpluim Simulatie",
                "description": "Dit is een TEST melding voor de NL-Alert rookpluim detector. Simulatie van chemische stof vrijkoming met windrichtingsberekening.",
                "instruction": "Dit is slechts een test. Geen actie vereist.",
                "area": [{
                    "areaDesc": "Test Gebied Nederland",
                    "geocode": [{
                        "valueName": "EMMA_ID", 
                        "value": "NL"
                    }],
                    "polygon": "52.1 4.9 52.2 4.9 52.2 5.0 52.1 5.0 52.1 4.9"
                }]
            }]
        }
        
        # Ensure coordinator data exists
        if coordinator.data is None:
            coordinator.data = {"alerts": []}
        
        # Add to coordinator data
        coordinator.data["alerts"].insert(0, test_alert)
        coordinator.async_set_updated_data(coordinator.data)
        
        _LOGGER.info("✅ Test alert created successfully")
    
    async def async_reset_alerts(call: ServiceCall) -> None:
        """Service to reset all alerts."""
        _LOGGER.info("🔄 NL-Alert reset alerts service called")
        
        # Ensure coordinator data exists
        if coordinator.data is None:
            coordinator.data = {"alerts": []}
        else:
            coordinator.data["alerts"] = []
        
        coordinator.async_set_updated_data(coordinator.data)
        _LOGGER.info("✅ All alerts have been reset")
    
    # Only register if not already registered
    if not hass.services.has_service(DOMAIN, "test_alert"):
        hass.services.async_register(DOMAIN, "test_alert", async_test_alert)
        _LOGGER.info("🧪 Registered service: nl_alert.test_alert")
    
    if not hass.services.has_service(DOMAIN, "reset_alerts"):
        hass.services.async_register(DOMAIN, "reset_alerts", async_reset_alerts)
        _LOGGER.info("🔄 Registered service: nl_alert.reset_alerts")


