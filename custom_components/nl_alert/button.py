"""Service platform for NL-Alert integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .coordinator import NLAlertCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_BUTTONS = [
    ButtonEntityDescription(
        key="test_alert_service",
        name="🧪 Test NL-Alert Simulatie",
        icon="mdi:test-tube",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonEntityDescription(
        key="reset_alerts_service", 
        name="🔄 Reset Alle Meldingen",
        icon="mdi:refresh-circle",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonEntityDescription(
        key="force_update_service",
        name="⚡ Force Data Update", 
        icon="mdi:update",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonEntityDescription(
        key="clear_historical_service",
        name="🗑️ Wis Historische Data",
        icon="mdi:delete-sweep",
        entity_category=EntityCategory.CONFIG,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NL-Alert service buttons from a config entry."""
    coordinator: NLAlertCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    for description in SERVICE_BUTTONS:
        entities.append(NLAlertServiceButton(coordinator, description))
    
    async_add_entities(entities)


class NLAlertServiceButton(CoordinatorEntity[NLAlertCoordinator], ButtonEntity):
    """Representation of a NL-Alert service button."""

    def __init__(
        self,
        coordinator: NLAlertCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the service button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Handle the button press - execute corresponding service."""
        _LOGGER.info(f"Service button pressed: {self.entity_description.key}")
        
        if self.entity_description.key == "test_alert_service":
            await self._execute_test_alert()
        elif self.entity_description.key == "reset_alerts_service":
            await self._execute_reset_alerts()
        elif self.entity_description.key == "force_update_service":
            await self._execute_force_update()
        elif self.entity_description.key == "clear_historical_service":
            await self._execute_clear_historical()

    async def _execute_test_alert(self) -> None:
        """Execute test alert service."""
        try:
            _LOGGER.info("🧪 Button: Executing test alert service...")
            # Call the test alert service through coordinator
            await self.hass.services.async_call(
                DOMAIN,
                "test_alert",
                {},
                blocking=True,
            )
            _LOGGER.info("✅ Button: Test alert service executed successfully")
        except Exception as e:
            _LOGGER.error(f"Error executing test alert service: {e}")

    async def _execute_reset_alerts(self) -> None:
        """Execute reset alerts service."""
        try:
            # Call the reset alerts service through coordinator
            await self.hass.services.async_call(
                DOMAIN,
                "reset_alerts",
                {},
                blocking=True,
            )
            _LOGGER.info("Reset alerts service executed successfully")
        except Exception as e:
            _LOGGER.error(f"Error executing reset alerts service: {e}")

    async def _execute_force_update(self) -> None:
        """Force data update from NL-Alert API."""
        try:
            _LOGGER.info("⚡ Button: Forcing data update from NL-Alert API...")
            await self.coordinator.async_refresh()
            _LOGGER.info("✅ Button: Force update completed successfully")
        except Exception as e:
            _LOGGER.error(f"❌ Button: Error during force update: {e}")

    async def _execute_clear_historical(self) -> None:
        """Clear historical alerts data."""
        try:
            # Clear historical data in coordinator
            if hasattr(self.coordinator, 'clear_historical_data'):
                await self.coordinator.clear_historical_data()
            _LOGGER.info("Historical data cleared successfully")
        except Exception as e:
            _LOGGER.error(f"Error clearing historical data: {e}")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success