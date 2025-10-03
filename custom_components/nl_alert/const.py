"""Constants for the NL-Alert integration."""
from __future__ import annotations

from typing import Final

# Integration domain
DOMAIN: Final = "nl_alert"

# Configuration keys
CONF_LOCATION_FILTER: Final = "location_filter"
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_SEVERITY_FILTER: Final = "severity_filter"
CONF_LANGUAGE: Final = "language"
CONF_WEATHER_ENTITY: Final = "weather_entity"

# API constants
API_BASE_URL: Final = "https://api.public-warning.app/api/v1"
API_ENDPOINT_ALERTS: Final = f"{API_BASE_URL}/providers/nl-alert/alerts"

# Default values
DEFAULT_UPDATE_INTERVAL: Final = 300  # 5 minutes
DEFAULT_SEVERITY_FILTER: Final = ["Minor", "Moderate", "Severe", "Extreme"]
DEFAULT_LANGUAGE: Final = "nl"

# Alert severities
SEVERITY_MINOR: Final = "Minor"
SEVERITY_MODERATE: Final = "Moderate" 
SEVERITY_SEVERE: Final = "Severe"
SEVERITY_EXTREME: Final = "Extreme"

# Device class
DEVICE_CLASS_NL_ALERT: Final = "nl_alert"

# Dispersion modeling
CONF_WEATHER_SOURCE: Final = "weather_source"
CONF_WIND_SENSOR: Final = "wind_speed_sensor"
CONF_WIND_DIRECTION_SENSOR: Final = "wind_direction_sensor"
CONF_TEMPERATURE_SENSOR: Final = "temperature_sensor"
CONF_ENABLE_PLUME_CALC: Final = "enable_plume_calculation"

# KNMI API
KNMI_API_BASE: Final = "https://api.knmi.nl/open-data/v1"
KNMI_STATIONS_ENDPOINT: Final = f"{KNMI_API_BASE}/datasets/observations_latest/versions/latest/files"

# Plume calculation status
PLUME_STATUS_SAFE: Final = "safe"  # Groen
PLUME_STATUS_CAUTION: Final = "caution"  # Oranje  
PLUME_STATUS_DANGER: Final = "danger"  # Rood

# Gaussian plume model constants
STABILITY_CLASSES: Final = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6}
DEFAULT_STABILITY_CLASS: Final = "D"  # Neutrale atmosfeer
MAX_PLUME_DISTANCE: Final = 10000  # 10km maximum berekenafstand

# Attributes
ATTR_ALERT_ID: Final = "alert_id"
ATTR_ALERT_TYPE: Final = "alert_type"
ATTR_SEVERITY: Final = "severity"
ATTR_CERTAINTY: Final = "certainty"
ATTR_URGENCY: Final = "urgency"
ATTR_AREAS: Final = "areas"
ATTR_DESCRIPTION: Final = "description"
ATTR_INSTRUCTIONS: Final = "instructions"
ATTR_SENT_TIME: Final = "sent_time"
ATTR_EFFECTIVE_TIME: Final = "effective_time"
ATTR_EXPIRES_TIME: Final = "expires_time"