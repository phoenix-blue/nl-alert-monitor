"""NL-Alert API client."""
from __future__ import annotations

import asyncio
import logging
import math
from datetime import datetime
from typing import Any

import aiohttp
import async_timeout

from .const import (
    API_ENDPOINT_ALERTS,
    KNMI_STATIONS_ENDPOINT,
    PLUME_STATUS_SAFE,
    PLUME_STATUS_CAUTION, 
    PLUME_STATUS_DANGER,
    DEFAULT_STABILITY_CLASS,
    MAX_PLUME_DISTANCE,
)

_LOGGER = logging.getLogger(__name__)


class NLAlertAPI:
    """Class to communicate with NL-Alert API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.session = session
        self._alerts: list[dict[str, Any]] = []

    async def async_get_alerts(self) -> list[dict[str, Any]]:
        """Get current alerts from NL-Alert API."""
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(API_ENDPOINT_ALERTS) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._alerts = data.get("alerts", [])
                        _LOGGER.debug("Retrieved %d alerts", len(self._alerts))
                        return self._alerts
                    else:
                        _LOGGER.error("API returned status %d", response.status)
                        return []
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout while fetching alerts")
            return []
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error while fetching alerts: %s", err)
            return []
        except Exception as err:
            _LOGGER.error("Unexpected error while fetching alerts: %s", err)
            return []

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get currently active alerts."""
        now = datetime.utcnow()
        active_alerts = []
        
        for alert in self._alerts:
            try:
                # Check if alert is still valid
                expires = alert.get("expires")
                if expires:
                    expires_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                    if expires_dt > now:
                        active_alerts.append(alert)
                else:
                    # If no expiry date, consider it active
                    active_alerts.append(alert)
            except (ValueError, TypeError) as err:
                _LOGGER.warning("Error parsing alert expiry date: %s", err)
                # Include alert if we can't parse the date
                active_alerts.append(alert)
        
        return active_alerts

    def get_alert_count(self) -> int:
        """Get total number of active alerts."""
        return len(self.get_active_alerts())

    def get_severity_counts(self) -> dict[str, int]:
        """Get count of alerts by severity."""
        counts = {"Minor": 0, "Moderate": 0, "Severe": 0, "Extreme": 0}
        
        for alert in self.get_active_alerts():
            severity = alert.get("severity", "Unknown")
            if severity in counts:
                counts[severity] += 1
        
        return counts

    def has_severe_alerts(self) -> bool:
        """Check if there are any severe or extreme alerts."""
        severity_counts = self.get_severity_counts()
        return severity_counts.get("Severe", 0) > 0 or severity_counts.get("Extreme", 0) > 0

    async def async_get_weather_data(self, hass, weather_entity_id: str = None) -> dict[str, Any]:
        """Get weather data from Home Assistant weather entity or KNMI."""
        try:
            if weather_entity_id and hass:
                # Probeer weerdata op te halen van HA weather entiteit
                weather_state = hass.states.get(weather_entity_id)
                if weather_state:
                    attributes = weather_state.attributes
                    
                    # Converteer windsnelheid indien nodig (van km/h naar m/s)
                    wind_speed = attributes.get("wind_speed", 0)
                    wind_speed_unit = attributes.get("wind_speed_unit", "km/h")
                    if wind_speed_unit == "km/h":
                        wind_speed = wind_speed / 3.6  # km/h naar m/s
                    
                    return {
                        "wind_speed": float(wind_speed),
                        "wind_direction": float(attributes.get("wind_bearing", 0)),
                        "temperature": float(attributes.get("temperature", 15)),
                        "pressure": float(attributes.get("pressure", 1013.25)),
                        "humidity": float(attributes.get("humidity", 50)),
                        "stability_class": self._estimate_stability_class(
                            float(attributes.get("temperature", 15)),
                            float(wind_speed),
                            attributes.get("condition", "unknown")
                        ),
                        "source": "ha_weather_entity",
                    }
            
            # Fallback naar mock KNMI data
            return {
                "wind_speed": 3.5,  # m/s
                "wind_direction": 225,  # graden (ZW)
                "temperature": 15.0,  # celsius
                "pressure": 1013.25,  # hPa
                "humidity": 50.0,  # %
                "stability_class": DEFAULT_STABILITY_CLASS,
                "source": "knmi_mock",
            }
        except Exception as err:
            _LOGGER.error("Fout bij ophalen weerdata: %s", err)
            return {
                "wind_speed": 2.0,
                "wind_direction": 180,
                "temperature": 10.0,
                "stability_class": DEFAULT_STABILITY_CLASS,
                "source": "fallback",
            }
    
    def _estimate_stability_class(self, temperature: float, wind_speed: float, condition: str) -> str:
        """Schat atmosferische stabiliteitsklasse in op basis van weerdata."""
        try:
            # Vereenvoudigde stabiliteitsclassificatie
            # A = zeer onstabiel, B = onstabiel, C = licht onstabiel
            # D = neutraal, E = stabiel, F = zeer stabiel
            
            if wind_speed < 2:  # Windstil
                if "sunny" in condition or "clear" in condition:
                    return "A"  # Sterk onstabiel bij zonneschijn
                elif "cloudy" in condition or "overcast" in condition:
                    return "F"  # Stabiel bij bewolking
                else:
                    return "E"  # Licht stabiel
            elif wind_speed < 3:  # Zwakke wind
                if "sunny" in condition:
                    return "B"
                elif "cloudy" in condition:
                    return "E"
                else:
                    return "D"
            elif wind_speed < 5:  # Matige wind
                if "sunny" in condition:
                    return "C"
                else:
                    return "D"  # Neutraal
            else:  # Sterke wind (>5 m/s)
                return "D"  # Neutraal bij sterke wind
                
        except Exception:
            return DEFAULT_STABILITY_CLASS

    def calculate_gaussian_plume(
        self,
        source_lat: float,
        source_lon: float, 
        home_lat: float,
        home_lon: float,
        wind_speed: float,
        wind_direction: float,
        stability_class: str = DEFAULT_STABILITY_CLASS,
    ) -> dict[str, Any]:
        """
        Berekent Gaussiaanse pluim dispersie.
        
        Args:
            source_lat: Latitude van bron (alert locatie)
            source_lon: Longitude van bron 
            home_lat: Latitude van woning
            home_lon: Longitude van woning
            wind_speed: Windsnelheid in m/s
            wind_direction: Windrichting in graden (waar wind naartoe gaat)
            stability_class: Atmosferische stabiliteitsklasse (A-F)
        
        Returns:
            Dict met pluim status en concentratie info
        """
        try:
            # Bereken afstand en richting tussen bron en woning
            distance, bearing = self._calculate_distance_bearing(
                source_lat, source_lon, home_lat, home_lon
            )
            
            if distance > MAX_PLUME_DISTANCE:
                return {
                    "status": PLUME_STATUS_SAFE,
                    "reason": "Te ver van bron",
                    "distance": distance,
                    "concentration": 0.0,
                }
            
            # Bereken of woning in windsector ligt
            wind_angle_diff = abs(self._angle_difference(bearing, wind_direction))
            
            # Pluim spreiding parameters (vereenvoudigd)
            sigma_y = self._calculate_sigma_y(distance, stability_class)
            sigma_z = self._calculate_sigma_z(distance, stability_class)
            
            # Gaussiaanse pluim formule (vereenvoudigd zonder bron sterkte)
            y_offset = distance * math.sin(math.radians(wind_angle_diff))
            
            # Concentratie berekening (relatief)
            if wind_speed < 0.5:  # Windstil
                concentration = 0.5  # Hoge onzekerheid
                status = PLUME_STATUS_CAUTION
                reason = "Windstil - onvoorspelbare verspreiding"
            else:
                # Gaussiaanse verdeling in y-richting
                concentration = math.exp(-(y_offset**2) / (2 * sigma_y**2))
                concentration *= 1 / (wind_speed * sigma_y * sigma_z)
                
                # Bepaal status op basis van concentratie
                if concentration > 0.1:  # Hoge concentratie
                    status = PLUME_STATUS_DANGER
                    reason = "Woning ligt in pluim traject"
                elif concentration > 0.02:  # Matige concentratie  
                    status = PLUME_STATUS_CAUTION
                    reason = "Woning ligt nabij pluim traject"
                else:
                    status = PLUME_STATUS_SAFE
                    reason = "Woning buiten pluim bereik"
            
            return {
                "status": status,
                "reason": reason,
                "distance": distance,
                "bearing": bearing,
                "wind_angle_diff": wind_angle_diff,
                "concentration": concentration,
                "sigma_y": sigma_y,
                "sigma_z": sigma_z,
            }
            
        except Exception as err:
            _LOGGER.error("Error calculating plume: %s", err)
            return {
                "status": PLUME_STATUS_CAUTION,
                "reason": f"Berekeningsfout: {err}",
                "concentration": 0.0,
            }

    def _calculate_distance_bearing(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> tuple[float, float]:
        """Bereken afstand en richting tussen twee punten."""
        # Haversine formule voor afstand
        R = 6371000  # Aardradius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        # Richting berekening
        y = math.sin(dlon) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
        bearing = math.degrees(math.atan2(y, x))
        bearing = (bearing + 360) % 360  # Normaliseer naar 0-360
        
        return distance, bearing

    def _angle_difference(self, angle1: float, angle2: float) -> float:
        """Bereken kleinste hoek tussen twee richtingen."""
        diff = abs(angle1 - angle2)
        return min(diff, 360 - diff)

    def _calculate_sigma_y(self, distance: float, stability_class: str) -> float:
        """Bereken horizontale dispersie parameter."""
        # Vereenvoudigde Pasquill-Gifford parameters
        distance_km = distance / 1000
        
        if stability_class in ["A", "B"]:  # Onstabiel
            return 0.32 * distance_km * (1 + 0.0004 * distance_km) ** -0.5
        elif stability_class == "C":  # Licht onstabiel
            return 0.22 * distance_km * (1 + 0.0004 * distance_km) ** -0.5
        elif stability_class == "D":  # Neutraal
            return 0.16 * distance_km * (1 + 0.0004 * distance_km) ** -0.5
        else:  # E, F - Stabiel
            return 0.11 * distance_km * (1 + 0.0004 * distance_km) ** -0.5

    def _calculate_sigma_z(self, distance: float, stability_class: str) -> float:
        """Bereken verticale dispersie parameter."""
        distance_km = distance / 1000
        
        if stability_class in ["A", "B"]:  # Onstabiel
            return 0.24 * distance_km * (1 + 0.001 * distance_km) ** 0.5
        elif stability_class == "C":  # Licht onstabiel
            return 0.20 * distance_km
        elif stability_class == "D":  # Neutraal
            return 0.14 * distance_km * (1 + 0.0003 * distance_km) ** -0.5
        else:  # E, F - Stabiel
            return 0.08 * distance_km * (1 + 0.0015 * distance_km) ** -0.5