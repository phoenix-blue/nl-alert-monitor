"""Data update coordinator for NL-Alert integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta, datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .api import NLAlertAPI

_LOGGER = logging.getLogger(__name__)


class NLAlertCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching NL-Alert data."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        api: NLAlertAPI,
        config_entry_data: dict[str, Any],
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=config_entry_data.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            ),
        )
        self.api = api
        self.config_data = config_entry_data
        self._historical_alerts = []  # Store historical alerts in memory
        
        # Device info for grouping entities
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, "nl_alert_api")},
            name="�️ NL-Alert Rookpluim Detector",
            manufacturer="Nederlandse Overheid",
            model="NL-Alert Monitoring Systeem",
            sw_version="2.1.0",
            configuration_url="https://www.nederlandwereldwijd.nl/themas/crisis-en-calamiteiten/nl-alert",
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from NL-Alert API."""
        try:
            # Haal actuele alerts op (voor current status)
            current_alerts = await self.api.async_get_alerts()
            active_alerts = self.api.get_active_alerts()
            
            # Haal recente alerts op (afgelopen 24h voor historical data)
            recent_alerts = await self.api.async_get_recent_alerts()
            _LOGGER.info(f"🔍 Retrieved {len(current_alerts)} current alerts and {len(recent_alerts)} recent alerts")
            
            # Add recent alerts to historical collection (only chemical/hazardous material alerts)
            for alert in recent_alerts:
                alert_id = alert.get("identifier")
                
                # Extract headline from info section
                headline = ""
                description = ""
                if isinstance(alert.get("info"), list) and len(alert["info"]) > 0:
                    info = alert["info"][0]
                    headline = info.get("headline", "").lower()
                    description = info.get("description", "").lower()
                elif isinstance(alert.get("info"), dict):
                    headline = alert["info"].get("headline", "").lower()
                    description = alert["info"].get("description", "").lower()
                
                # Only keep alerts related to chemical incidents, fires, or hazardous materials
                is_relevant = any(keyword in headline + " " + description for keyword in [
                    "chemisch", "brand", "rookontwikkeling", "giftige", "schadelijk", 
                    "gevaarlijk", "stof", "gas", "rook", "ontploffing", "lekkage",
                    "chemical", "fire", "smoke", "toxic", "hazardous", "dangerous",
                    "ammonia", "ammoniak", "chlor", "benzeen", "chloor"
                ])
                
                if alert_id and is_relevant and not any(h_alert.get("identifier") == alert_id for h_alert in self._historical_alerts):
                    # Add timestamp for cleanup
                    alert["stored_at"] = datetime.now().isoformat()
                    self._historical_alerts.append(alert)
                    _LOGGER.debug(f"➕ Added relevant alert to history: {headline[:50]}...")
            
            # Clean up old historical alerts (keep only last 30 days and max 50 alerts)
            cutoff_date = datetime.now() - timedelta(days=30)
            self._historical_alerts = [
                alert for alert in self._historical_alerts[-50:]  # Max 50 alerts
                if alert.get("stored_at")
            ]

            data = {
                "alerts": current_alerts,
                "recent_alerts": recent_alerts,
                "active_alerts": active_alerts,
                "active_count": len(active_alerts),
                "alert_count": len(active_alerts),
                "severity_counts": self.api.get_severity_counts(),
                "severe_count": self.api.get_severity_counts().get("Severe", 0) + self.api.get_severity_counts().get("Extreme", 0),
                "has_severe_alerts": self.api.has_severe_alerts(),
                "historical_alerts": self._historical_alerts,
                "historical_count": len(self._historical_alerts),
            }
            
            # Als pluim berekening is ingeschakeld, voeg gevaar data toe
            if self.config_data.get("enable_plume_calculation", False):
                home_danger = await self._async_check_home_danger(active_alerts)
                data["home_danger"] = home_danger
                data["weather_data"] = home_danger.get("weather_data", {})
            else:
                # Zet veilige standaarden als pluim berekening uit staat
                data["home_danger"] = {
                    "in_danger": False,
                    "status": "disabled",
                    "risk_percentage": 0,
                    "message": "Pluim berekening uitgeschakeld"
                }
                data["weather_data"] = {}
            
            return data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _async_check_home_danger(
        self, 
        active_alerts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Check if home location is in danger from active chemical alerts."""
        try:
            # Get weather data
            weather_entity = self.config_data.get("weather_entity")
            if weather_entity:
                weather_data = await self.api.async_get_weather_data(self.hass, weather_entity)
            else:
                weather_data = {"wind_speed": 5, "wind_direction": 180, "temperature": 15}  # Mock data
            
            # Check each active alert for chemical/hazardous content
            for alert in active_alerts:
                # Extract info data (can be list or dict)
                info_data = {}
                if isinstance(alert.get("info"), list) and len(alert["info"]) > 0:
                    info_data = alert["info"][0]
                elif isinstance(alert.get("info"), dict):
                    info_data = alert["info"]
                
                headline = info_data.get("headline", "").lower()
                description = info_data.get("description", "").lower()
                
                # Check if alert is chemical/fire/hazardous related
                is_chemical = any(keyword in headline + " " + description for keyword in [
                    "chemisch", "brand", "rookontwikkeling", "giftige", "schadelijk", 
                    "gevaarlijk", "stof", "gas", "rook", "ontploffing", "lekkage",
                    "chemical", "fire", "smoke", "toxic", "hazardous", "dangerous",
                    "ammonia", "ammoniak", "chlor", "benzeen", "chloor"
                ])
                
                if is_chemical:
                    # Use private atmospheric model for real calculations
                    try:
                        from ._atmospheric_model import calculate_risk_percentage
                        
                        # Mock incident coordinates (should be parsed from alert polygon)
                        incident_lat = 52.3676  # Amsterdam center as example
                        incident_lon = 4.9041
                        
                        if self.home_latitude and self.home_longitude:
                            risk_percentage, distance_km = calculate_risk_percentage(
                                self.home_latitude,
                                self.home_longitude,
                                incident_lat, 
                                incident_lon,
                                weather_data.get("wind_direction", 180),
                                weather_data.get("wind_speed", 5.0)
                            )
                        else:
                            risk_percentage, distance_km = 25.0, 10.0  # Default values
                        
                        plume_direction = (weather_data.get("wind_direction", 180) + 180) % 360
                        
                        return {
                            "in_danger": risk_percentage > 1.0,
                            "status": "danger_detected" if risk_percentage > 1.0 else "low_risk",
                            "risk_percentage": risk_percentage,
                            "distance_km": distance_km,
                            "wind_direction": weather_data.get("wind_direction", 180),
                            "plume_direction": plume_direction,
                            "concentration": risk_percentage / 100.0,
                            "alert_headline": info_data.get("headline", ""),
                            "message": f"🌨️ Rookpluim risico: {risk_percentage:.1f}% op {distance_km:.1f}km afstand",
                            "weather_data": weather_data,
                        }
                    except Exception as e:
                        _LOGGER.error(f"Error calculating plume risk: {e}")
                        # Fallback to mock data
                        return {
                            "in_danger": True,
                            "status": "danger_detected",
                            "risk_percentage": 35.0,
                            "distance_km": 12.5,
                            "wind_direction": weather_data.get("wind_direction", 180),
                            "plume_direction": 45,
                            "concentration": 0.25,
                            "alert_headline": info_data.get("headline", ""),
                            "message": "🌨️ Rookpluim detector - berekening niet beschikbaar",
                            "weather_data": weather_data,
                        }
            
            return {
                "in_danger": False,
                "status": "safe",
                "risk_percentage": 0,
                "message": "Geen gevaarlijke chemische stoffen gedetecteerd",
                "weather_data": weather_data,
            }
            
        except Exception as e:
            _LOGGER.error("Error checking home danger: %s", e)
            return {
                "in_danger": False,
                "status": "error", 
                "risk_percentage": 0,
                "message": f"Fout bij gevarencheck: {e}",
                "weather_data": {},
            }

    @property
    def historical_alerts(self) -> list[dict[str, Any]]:
        """Get historical alerts list."""
        return self._historical_alerts
    
    @historical_alerts.setter
    def historical_alerts(self, value: list[dict[str, Any]]) -> None:
        """Set historical alerts list."""
        self._historical_alerts = value

    async def clear_historical_data(self) -> None:
        """Clear historical alerts data."""
        try:
            self._historical_alerts = []
            _LOGGER.info("Historical alerts data cleared")
            # Trigger update to notify all listeners
            await self.async_refresh()
        except Exception as e:
            _LOGGER.error(f"Error clearing historical data: {e}")
            raise