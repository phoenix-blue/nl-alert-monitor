"""Binary sensor platform for NL-Alert integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NLAlertCoordinator

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_DESCRIPTIONS = [
    BinarySensorEntityDescription(
        key="active_alert",
        name="🔔 Alert Status",
        icon="mdi:alert-decagram-outline",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    BinarySensorEntityDescription(
        key="severe_alert", 
        name="🚨 Gevaar Alarm",
        icon="mdi:fire-alert",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NL-Alert binary sensors."""
    
    # Get coordinator from shared data
    coordinator_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = coordinator_data["coordinator"]
    
    # Debug coordinator state
    _LOGGER.debug("Binary sensor setup - Coordinator data available: %s", coordinator.data is not None)
    
    entities = []
    for description in BINARY_SENSOR_DESCRIPTIONS:
        binary_sensor = NLAlertBinarySensor(coordinator, description)
        entities.append(binary_sensor)
        _LOGGER.debug("Creating binary sensor: %s (%s)", description.name, description.key)
    
    _LOGGER.info("Adding %d NL-Alert binary sensors", len(entities))
    try:
        async_add_entities(entities, True)
        _LOGGER.info("Successfully added %d NL-Alert binary sensors", len(entities))
    except Exception as e:
        _LOGGER.error("Failed to add NL-Alert binary sensors: %s", e)
        raise


class NLAlertBinarySensor(CoordinatorEntity[NLAlertCoordinator], BinarySensorEntity):
    """Representation of a NL-Alert binary sensor."""

    def __init__(
        self,
        coordinator: NLAlertCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        # Remove the "NL-Alert" prefix since we use has_entity_name
        self._attr_name = description.name
        self._attr_has_entity_name = True
        # Use device info from coordinator to group all entities
        self._attr_device_info = coordinator.device_info
        
        # Debug logging
        _LOGGER.debug("Initialized binary sensor: %s with unique_id: %s", 
                     self._attr_name, self._attr_unique_id)

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return False
            
        if self.entity_description.key == "active_alert":
            return self.coordinator.data.get("alert_count", 0) > 0
        elif self.entity_description.key == "severe_alert":
            return self.coordinator.data.get("has_severe_alerts", False)
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
            
        attrs = {
            "alert_count": self.coordinator.data.get("active_count", 0),
            "last_updated": self.coordinator.last_update_success,
            "severity_counts": self.coordinator.data.get("severity_counts", {}),
        }
        
        # Voeg extra info toe voor actieve alerts
        if self.entity_description.key == "active_alert":
            attrs.update({
                "historical_count": self.coordinator.data.get("historical_count", 0),
                "severe_count": self.coordinator.data.get("severe_count", 0),
            })
        elif self.entity_description.key == "severe_alert":
            severe_alerts = []
            for alert in self.coordinator.data.get("alerts", []):
                if alert.get("severity") in ["Severe", "Extreme"]:
                    severe_alerts.append({
                        "id": alert.get("identifier"),
                        "severity": alert.get("severity"),
                        "headline": alert.get("headline"),
                        "areas": alert.get("areaDesc"),
                    })
            attrs["severe_alerts"] = severe_alerts[:5]  # Laatste 5 ernstige alerts
            
        return attrs