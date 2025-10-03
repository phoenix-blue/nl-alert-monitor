"""Sensor platform for NL-Alert integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from datetime import datetime, timezone
from .const import (
    DOMAIN,
    ATTR_ALERT_ID,
    ATTR_SEVERITY,
    ATTR_AREAS,
    ATTR_DESCRIPTION,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="alert_count",
        name="🚨 Actieve Waarschuwingen",
        icon="mdi:bullhorn-variant",
        native_unit_of_measurement="meldingen",
    ),
    SensorEntityDescription(
        key="severe_alerts",
        name="⚠️ Gevaarlijke Incidenten",
        icon="mdi:chemical-weapon",
        native_unit_of_measurement="meldingen",
    ),
    SensorEntityDescription(
        key="historical_alerts",
        name="📋 Incident Archief",
        icon="mdi:archive-alert-outline",
        native_unit_of_measurement="meldingen",
    ),
    SensorEntityDescription(
        key="historical_alerts_text",
        name="📝 Incident Archief Tekst",
        icon="mdi:text-box-multiple-outline",
    ),
    SensorEntityDescription(
        key="danger_compass",
        name="🧭 Pluim Risico Kompas",
        icon="mdi:compass-rose",
        native_unit_of_measurement="%",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NL-Alert sensors."""
    
    # Get coordinator from shared data (created in __init__.py)
    coordinator_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = coordinator_data["coordinator"]
    
    # Services are registered in __init__.py
    
    # Debug coordinator state
    _LOGGER.debug("Coordinator data available: %s", coordinator.data is not None)
    if coordinator.data:
        _LOGGER.debug("Coordinator data keys: %s", list(coordinator.data.keys()))
    
    # Add sensors
    entities = []
    for description in SENSOR_DESCRIPTIONS:
        sensor = NLAlertSensor(coordinator, description)
        entities.append(sensor)
        _LOGGER.debug("Creating sensor: %s (%s)", description.name, description.key)
    
    _LOGGER.info("Adding %d NL-Alert sensors", len(entities))
    try:
        async_add_entities(entities, True)
        _LOGGER.info("Successfully added %d NL-Alert sensors", len(entities))
    except Exception as e:
        _LOGGER.error("Failed to add NL-Alert sensors: %s", e)
        raise



class NLAlertSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NL-Alert sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        # Remove the "NL-Alert" prefix since we use has_entity_name
        self._attr_name = description.name
        self._attr_has_entity_name = True
        # Use device info from coordinator to group all entities
        self._attr_device_info = coordinator.device_info
        
        # Debug logging
        _LOGGER.debug("Initialized sensor: %s with unique_id: %s", 
                     self._attr_name, self._attr_unique_id)

    @property
    def native_value(self) -> int | str | None:
        """Return the state of the sensor."""
        if self.entity_description.key == "alert_count":
            value = self.coordinator.data.get("active_count", 0)
        elif self.entity_description.key == "severe_alerts":
            value = self.coordinator.data.get("severe_count", 0)
        elif self.entity_description.key == "historical_alerts":
            value = self.coordinator.data.get("historical_count", 0)
            _LOGGER.debug("Historical alerts sensor value: %s", value)
        elif self.entity_description.key == "historical_alerts_text":
            # Format historical alerts as readable text
            value = self._format_historical_alerts_text()
        elif self.entity_description.key == "danger_compass":
            home_danger = self.coordinator.data.get("home_danger", {})
            value = home_danger.get("risk_percentage", 0)
        else:
            return None
            
        _LOGGER.debug("Sensor %s (%s) value: %s", 
                     self.entity_description.name, 
                     self.entity_description.key, 
                     value)
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.entity_description.key == "historical_alerts":
            historical_alerts = self.coordinator.data.get("historical_alerts", [])
            
            # Extract and flatten alert data from nested info structure
            formatted_alerts = []
            for alert in historical_alerts[-10:]:  # Last 10 for attributes
                # Extract info data (can be list or dict)
                info_data = {}
                if isinstance(alert.get("info"), list) and len(alert["info"]) > 0:
                    info_data = alert["info"][0]
                elif isinstance(alert.get("info"), dict):
                    info_data = alert["info"]
                
                # Extract area description
                area_desc = ""
                if isinstance(info_data.get("area"), list) and len(info_data["area"]) > 0:
                    area_desc = info_data["area"][0].get("areaDesc", "")
                elif isinstance(info_data.get("area"), dict):
                    area_desc = info_data["area"].get("areaDesc", "")
                
                formatted_alerts.append({
                    "id": alert.get("identifier"),
                    "ernst": info_data.get("severity"),
                    "gebied": area_desc,
                    "beschrijving": info_data.get("headline"),
                    "verstuurd": alert.get("sent"),
                    "geldig_tot": alert.get("expires"),
                })
            
            return {
                "historische_meldingen": formatted_alerts,
                "totaal_aantal": len(historical_alerts),
            }
        elif self.entity_description.key == "danger_compass":
            home_danger = self.coordinator.data.get("home_danger", {})
            weather_data = self.coordinator.data.get("weather_data", {})
            
            # Create compass visualization data
            risk_percentage = home_danger.get("risk_percentage", 0)
            wind_direction = weather_data.get("wind_direction", 0)
            plume_direction = home_danger.get("plume_direction", 0)
            
            return {
                "status": home_danger.get("status", "safe"),
                "in_danger": home_danger.get("in_danger", False),
                "risk_percentage": risk_percentage,
                "distance_km": home_danger.get("distance_km", 0),
                "wind_direction": wind_direction,
                "wind_direction_text": self._direction_to_compass(wind_direction),
                "plume_direction": plume_direction,
                "plume_direction_text": self._direction_to_compass(plume_direction),
                "alert_headline": home_danger.get("alert_headline", ""),
                "message": home_danger.get("message", "Geen gevaar gedetecteerd"),
                "concentration": home_danger.get("concentration", 0),
                "wind_speed": weather_data.get("wind_speed", 0),
                "temperature": weather_data.get("temperature", 0),
                # Compass visualization data
                "compass_data": self._create_compass_visualization(home_danger, weather_data),
                "risk_color": self._get_risk_color(risk_percentage),
                "risk_level": self._get_risk_level(risk_percentage),
            }
        
        alerts = self.coordinator.data.get("alerts", [])
        if not alerts:
            return {}
        
        # Return info about the most recent alert
        latest_alert = alerts[0] if alerts else {}
        
        # Extract info data (can be list or dict)
        info_data = {}
        if isinstance(latest_alert.get("info"), list) and len(latest_alert["info"]) > 0:
            info_data = latest_alert["info"][0]
        elif isinstance(latest_alert.get("info"), dict):
            info_data = latest_alert["info"]
        
        # Extract area description
        area_desc = ""
        if isinstance(info_data.get("area"), list) and len(info_data["area"]) > 0:
            area_desc = info_data["area"][0].get("areaDesc", "")
        elif isinstance(info_data.get("area"), dict):
            area_desc = info_data["area"].get("areaDesc", "")
        
        return {
            ATTR_ALERT_ID: latest_alert.get("identifier"),
            ATTR_SEVERITY: info_data.get("severity"),
            ATTR_AREAS: area_desc,
            ATTR_DESCRIPTION: info_data.get("headline"),
        }

    def _direction_to_compass(self, bearing: float) -> str:
        """Convert bearing to Dutch compass direction."""
        directions = ["N", "NNO", "NO", "ONO", "O", "OZO", "ZO", "ZZO",
                     "Z", "ZZW", "ZW", "WZW", "W", "WNW", "NW", "NNW"]
        
        index = round(bearing / 22.5) % 16
        return directions[index]
    
    def _create_compass_visualization(self, danger_data: dict, weather_data: dict) -> dict:
        """Create compass visualization data for frontend."""
        return {
            "center_text": f"{danger_data.get('risk_percentage', 0):.1f}%",
            "wind_arrow": weather_data.get("wind_direction", 0),
            "danger_sector": {
                "direction": danger_data.get("plume_direction", 0),
                "width": min(60, max(10, danger_data.get("risk_percentage", 0) * 2)),  # Sector width based on risk
                "intensity": danger_data.get("risk_percentage", 0) / 100,
            },
            "sectors": [
                {"direction": i * 45, "label": self._direction_to_compass(i * 45)} 
                for i in range(8)
            ]
        }
    
    def _get_risk_color(self, risk_percentage: float) -> str:
        """Get color based on risk percentage."""
        if risk_percentage >= 75:
            return "#FF0000"  # Red - Extreme danger
        elif risk_percentage >= 50:
            return "#FF8C00"  # Orange - High risk
        elif risk_percentage >= 25:
            return "#FFD700"  # Yellow - Medium risk
        elif risk_percentage >= 10:
            return "#ADFF2F"  # Light green - Low risk
        else:
            return "#00FF00"  # Green - Safe
    
    def _get_risk_level(self, risk_percentage: float) -> str:
        """Get risk level text."""
        if risk_percentage >= 75:
            return "Extreem Gevaar"
        elif risk_percentage >= 50:
            return "Hoog Risico"
        elif risk_percentage >= 25:
            return "Gemiddeld Risico"
        elif risk_percentage >= 10:
            return "Laag Risico"
        else:
            return "Veilig"

    def _format_historical_alerts_text(self) -> str:
        """Format historical alerts as readable text."""
        historical_alerts = self.coordinator.data.get("historical_alerts", [])
        
        if not historical_alerts:
            return "Geen historische meldingen beschikbaar"
        
        # Format last 10 alerts as text
        text_lines = [f"Historische Meldingen ({len(historical_alerts)} totaal):", ""]
        
        for idx, alert in enumerate(historical_alerts[-10:], 1):  # Last 10 alerts
            # Extract info data (can be list or dict)
            info_data = {}
            if isinstance(alert.get("info"), list) and len(alert["info"]) > 0:
                info_data = alert["info"][0]
            elif isinstance(alert.get("info"), dict):
                info_data = alert["info"]
            
            # Extract area description
            area_desc = ""
            if isinstance(info_data.get("area"), list) and len(info_data["area"]) > 0:
                area_desc = info_data["area"][0].get("areaDesc", "Onbekend gebied")
            elif isinstance(info_data.get("area"), dict):
                area_desc = info_data["area"].get("areaDesc", "Onbekend gebied")
            
            # Format alert information
            headline = info_data.get("headline", "Geen beschrijving")
            severity = info_data.get("severity", "Onbekend")
            sent = alert.get("sent", "Onbekende datum")
            
            # Add formatted alert to text
            text_lines.append(f"{idx}. {headline}")
            text_lines.append(f"   Ernst: {severity} | Gebied: {area_desc}")
            text_lines.append(f"   Verstuurd: {sent}")
            text_lines.append("")
        
        return "\n".join(text_lines)


