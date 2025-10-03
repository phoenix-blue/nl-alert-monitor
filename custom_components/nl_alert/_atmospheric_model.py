"""
Private atmospheric dispersion module.
Contains proprietary Gaussian plume modeling calculations.
"""

import math
from typing import Tuple, Optional


class _AtmosphericModel:
    """Private atmospheric dispersion calculator."""
    
    # Stability class coefficients (Pasquill-Gifford)
    _STABILITY_PARAMS = {
        'A': {'a': 213, 'b': 440.8, 'c': 1.941, 'd': 9.27, 'f': 459.7},
        'B': {'a': 156, 'b': 106.6, 'c': 1.149, 'd': 3.3, 'f': 108.2},
        'C': {'a': 104, 'b': 61.0, 'c': 0.911, 'd': 0, 'f': 61.0},
        'D': {'a': 68, 'b': 33.2, 'c': 0.725, 'd': -1.7, 'f': 44.5},
        'E': {'a': 50.5, 'b': 22.8, 'c': 0.678, 'd': -1.3, 'f': 37.6},
        'F': {'a': 34, 'b': 14.35, 'c': 0.740, 'd': -0.35, 'f': 18.05}
    }
    
    @staticmethod
    def _calculate_sigma_y(distance_m: float, stability: str) -> float:
        """Calculate horizontal dispersion coefficient."""
        params = _AtmosphericModel._STABILITY_PARAMS.get(stability, 
                 _AtmosphericModel._STABILITY_PARAMS['D'])
        
        x_km = distance_m / 1000.0
        
        if x_km < 1.0:
            theta = 0.017453293 * (params['c'] - params['d'] * math.log(x_km))
            sigma_y = params['a'] * x_km * math.tan(theta)
        else:
            sigma_y = params['b'] * (x_km ** params['f'] / 1000)
            
        return max(sigma_y, 1.0)
    
    @staticmethod 
    def _calculate_sigma_z(distance_m: float, stability: str) -> float:
        """Calculate vertical dispersion coefficient."""
        # Simplified Briggs formulas
        x_km = distance_m / 1000.0
        
        coefficients = {
            'A': lambda x: 0.20 * x,
            'B': lambda x: 0.12 * x,
            'C': lambda x: 0.08 * x * (1 + 0.0001 * x) ** -0.5,
            'D': lambda x: 0.06 * x * (1 + 0.0015 * x) ** -0.5,
            'E': lambda x: 0.03 * x * (1 + 0.0003 * x) ** -1,
            'F': lambda x: 0.016 * x * (1 + 0.0003 * x) ** -1
        }
        
        calc_func = coefficients.get(stability, coefficients['D'])
        sigma_z = calc_func(x_km * 1000)
        
        return max(sigma_z, 1.0)


def _gaussian_plume_concentration(
    distance_m: float,
    crosswind_m: float, 
    height_m: float,
    source_height: float = 20.0,
    emission_rate: float = 1.0,
    wind_speed: float = 5.0,
    stability_class: str = 'D'
) -> float:
    """
    Calculate concentration using Gaussian plume model.
    
    This is a proprietary implementation of atmospheric dispersion
    modeling based on EPA/NOAA standards with custom optimizations.
    """
    
    if distance_m <= 0:
        return 0.0
    
    # Get dispersion coefficients    
    sigma_y = _AtmosphericModel._calculate_sigma_y(distance_m, stability_class)
    sigma_z = _AtmosphericModel._calculate_sigma_z(distance_m, stability_class)
    
    # Crosswind term
    y_term = math.exp(-0.5 * (crosswind_m / sigma_y) ** 2)
    
    # Vertical terms (ground reflection)
    z1_term = math.exp(-0.5 * ((height_m - source_height) / sigma_z) ** 2)
    z2_term = math.exp(-0.5 * ((height_m + source_height) / sigma_z) ** 2)
    
    # Full Gaussian plume equation
    concentration = (emission_rate / (2 * math.pi * wind_speed * sigma_y * sigma_z)) * \
                   y_term * (z1_term + z2_term)
    
    return max(concentration, 0.0)


def calculate_risk_percentage(
    home_lat: float,
    home_lon: float, 
    incident_lat: float,
    incident_lon: float,
    wind_direction: float,
    wind_speed: float = 5.0
) -> Tuple[float, float]:
    """
    Calculate risk percentage for home location.
    
    Returns:
        Tuple[float, float]: (risk_percentage, distance_km)
    """
    try:
        # Calculate distance
        distance_km = _calculate_distance(home_lat, home_lon, incident_lat, incident_lon)
        
        if distance_km > 50.0:  # Beyond significant risk range
            return 0.0, distance_km
        
        # Calculate bearing from incident to home
        bearing = _calculate_bearing(incident_lat, incident_lon, home_lat, home_lon)
        
        # Wind direction adjustment (wind blows FROM direction TO opposite)
        plume_direction = (wind_direction + 180) % 360
        
        # Angular difference between plume and home
        angle_diff = abs(bearing - plume_direction)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # Crosswind distance (perpendicular to plume centerline)
        crosswind_distance = distance_km * 1000 * math.sin(math.radians(angle_diff))
        
        # Calculate concentration at ground level
        concentration = _gaussian_plume_concentration(
            distance_m=distance_km * 1000,
            crosswind_m=crosswind_distance,
            height_m=2.0,  # Ground level (2m)
            source_height=20.0,
            wind_speed=wind_speed,
            stability_class='D'  # Neutral stability
        )
        
        # Convert to risk percentage (proprietary scaling)
        risk_factor = 1000.0  # Calibration constant
        risk_percentage = min(concentration * risk_factor, 100.0)
        
        return risk_percentage, distance_km
        
    except Exception:
        return 0.0, 0.0


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between coordinates using Haversine formula."""
    R = 6371.0  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def _calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing from point 1 to point 2."""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon_rad = math.radians(lon2 - lon1)
    
    y = math.sin(dlon_rad) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad)
    
    bearing = math.atan2(y, x)
    bearing_degrees = math.degrees(bearing)
    
    return (bearing_degrees + 360) % 360