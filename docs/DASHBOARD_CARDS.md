# 🎨 NL-Alert Rookpluim Detector - Custom Cards & Services

## 🧭 **Compass Risk Card**

Een prachtige visuele kaart met windrichting, risico-percentage en kompas!

### 📊 **Picture Elements Card - Compass Dashboard**

```yaml
type: picture-elements
image: /local/nl-alert/compass-background.png  # Upload een kompas afbeelding
elements:
  # Risk percentage in het midden
  - type: state-label
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    style:
      top: 50%
      left: 50%
      font-size: 28px
      font-weight: bold
      color: >
        {% set risk = states('sensor.nl_alert_pluim_monitor_pluim_risico_kompas') | int %}
        {% if risk >= 75 %}red
        {% elif risk >= 50 %}orange  
        {% elif risk >= 25 %}yellow
        {% elif risk >= 10 %}lightgreen
        {% else %}green
        {% endif %}
      text-shadow: 2px 2px 4px rgba(0,0,0,0.8)
    
  # Risk level text
  - type: state-label
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: risk_level
    style:
      top: 62%
      left: 50%
      font-size: 14px
      font-weight: bold
      color: white
      text-shadow: 1px 1px 2px rgba(0,0,0,0.8)
  
  # Wind direction indicator
  - type: icon
    icon: mdi:navigation
    style:
      top: 25%
      left: 50%
      transform: >
        rotate({{ state_attr('sensor.nl_alert_pluim_monitor_pluim_risico_kompas', 'wind_direction') | int }}deg)
      color: cyan
      --mdc-icon-size: 30px
      filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.8))
  
  # Danger sector visualization (if risk > 10%)
  - type: conditional
    conditions:
      - entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
        state_not: "0"
    elements:
      - type: icon  
        icon: mdi:cone
        style:
          top: 35%
          left: 50%
          transform: >
            rotate({{ state_attr('sensor.nl_alert_pluim_monitor_pluim_risico_kompas', 'plume_direction') | int }}deg)
          color: >
            {% set risk = states('sensor.nl_alert_pluim_monitor_pluim_risico_kompas') | int %}
            {% if risk >= 50 %}red
            {% elif risk >= 25 %}orange  
            {% else %}yellow
            {% endif %}
          opacity: 0.7
          --mdc-icon-size: 40px
  
  # Status message at bottom
  - type: state-label
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: message
    style:
      top: 85%
      left: 50%
      font-size: 12px
      max-width: 280px
      color: white
      text-align: center
      text-shadow: 1px 1px 2px rgba(0,0,0,0.8)
      background-color: rgba(0,0,0,0.3)
      border-radius: 10px
      padding: 5px
```

### 📈 **Gauge Card - Risk Meter**

```yaml
type: gauge
entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
name: 🌪️ Pluim Risico
unit: '%'
min: 0
max: 100
severity:
  green: 0
  yellow: 10
  orange: 25
  red: 50
needle: true
```

### 🎛️ **Entities Card - Complete Status**

```yaml
type: entities
title: 🌪️ NL-Alert Pluim Monitor Status
show_header_toggle: false
entities:
  # Status indicators
  - type: section
    label: "🚨 Alert Status"
  - entity: binary_sensor.nl_alert_pluim_monitor_alert_status
    name: Alert Actief
    icon: mdi:alert-decagram
  - entity: binary_sensor.nl_alert_pluim_monitor_gevaar_alarm  
    name: Gevaar Gedetecteerd
    icon: mdi:fire-alert
  - entity: sensor.nl_alert_pluim_monitor_actieve_waarschuwingen
    name: Actieve Meldingen
    
  # Risk assessment  
  - type: section
    label: "🧭 Risico Analyse"
  - entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    name: Risico Percentage
    icon: mdi:percent
  - type: attribute
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: risk_level
    name: Risico Niveau
    icon: mdi:alert-circle-outline
  - type: attribute
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: distance_km
    name: Afstand Incident (km)
    icon: mdi:map-marker-distance
    
  # Weather conditions
  - type: section  
    label: "🌬️ Weersomstandigheden"
  - type: attribute
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: wind_direction_text
    name: Wind Richting
    icon: mdi:compass-outline
  - type: attribute
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: wind_speed
    name: Wind Snelheid (m/s)
    icon: mdi:weather-windy
  - type: attribute
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: temperature
    name: Temperatuur (°C)
    icon: mdi:thermometer
    
  # Historical data
  - type: section
    label: "📋 Historische Data"
  - entity: sensor.nl_alert_pluim_monitor_incident_archief
    name: Gearchiveerde Incidenten
    icon: mdi:archive-alert
state_color: true
```

### 🎨 **Custom Button Card (met card-mod)**

Installeer eerst `card-mod` via HACS, dan kun je deze gebruiken:

```yaml
type: custom:button-card
entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
name: 🌪️ Pluim Risico Monitor
show_state: true
show_icon: true
icon: mdi:compass-rose
layout: vertical
styles:
  card:
    - height: 200px
    - border-radius: 15px
    - background: >
        [[[
          const risk = parseInt(entity.state);
          if (risk >= 75) return 'linear-gradient(135deg, #ff4757, #ff3838)';
          if (risk >= 50) return 'linear-gradient(135deg, #ffa502, #ff6348)';  
          if (risk >= 25) return 'linear-gradient(135deg, #ffdd59, #ffc048)';
          if (risk >= 10) return 'linear-gradient(135deg, #7bed9f, #70a1ff)';
          return 'linear-gradient(135deg, #5f27cd, #341f97)';
        ]]]
    - color: white
    - box-shadow: 0 4px 8px rgba(0,0,0,0.3)
  icon:
    - width: 40px
    - height: 40px
    - animation: >
        [[[
          if (entity.state > 10) return 'spin 2s linear infinite';
          return 'none';
        ]]]
  name:
    - font-weight: bold
    - font-size: 14px
  state:
    - font-size: 24px
    - font-weight: bold
custom_fields:
  risk_level: >
    [[[ return entity.attributes.risk_level || 'Veilig'; ]]]
  wind_info: >
    [[[ 
      const wind = entity.attributes.wind_direction_text || 'N';
      const speed = entity.attributes.wind_speed || 0;
      return `🌬️ ${wind} ${speed}m/s`;
    ]]]
  message: >
    [[[ return entity.attributes.message || 'Geen data'; ]]]
```

### 📱 **Mobile-Optimized Card Stack**

Voor mobiel gebruik:

```yaml
type: vertical-stack
cards:
  # Quick status
  - type: glance
    entities:
      - entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
        name: Risico %
      - entity: binary_sensor.nl_alert_pluim_monitor_gevaar_alarm
        name: Gevaar
      - entity: sensor.nl_alert_pluim_monitor_actieve_waarschuwingen  
        name: Actief
    state_color: true
    
  # Risk gauge
  - type: gauge
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    name: Pluim Risico
    needle: true
    severity:
      green: 0
      yellow: 10
      orange: 25
      red: 50
      
  # Quick actions (if you have automation helpers)
  - type: entities
    entities:
      - input_boolean.nl_alert_auto_ventilation
      - input_number.nl_alert_risk_threshold
    state_color: true
```

### 🖼️ **Compass Background Image**

Maak een map `/config/www/nl-alert/` en plaats hier een kompas afbeelding. Je kunt een gratis kompas PNG downloaden van:

- **Pixabay**: zoek op "compass PNG" 
- **Unsplash**: zoek op "compass"
- **Maak je eigen**: gebruik CSS/SVG voor een geanimeerd kompas

### 🎭 **CSS Animaties**

Voeg dit toe aan je `configuration.yaml` voor animations:

```yaml
frontend:
  extra_module_url:
    - /local/nl-alert/compass-animations.js
```

En maak `/config/www/nl-alert/compass-animations.js`:

```javascript
// Rotating compass animation
const style = document.createElement('style');
style.innerHTML = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes pulse-danger {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
  
  .danger-pulse {
    animation: pulse-danger 1s ease-in-out infinite;
  }
`;
document.head.appendChild(style);
```

Perfect! Nu heb je een complete visuele ervaring! 🎨✨

---

## 🧪 **Test & Beheer Services**

### Gebruik de ingebouwde services voor test en reset functionaliteit:

### 🔧 **Service Control Card**

```yaml
type: entities
title: "🌨️ Rookpluim Detector Beheer"
entities:
  - type: call-service
    name: "🧪 Test Alert Simulatie"
    service: nl_alert.test_alert
    icon: mdi:flask
    service_data: {}
  - type: call-service
    name: "🔄 Reset Alle Meldingen"
    service: nl_alert.reset_alerts
    icon: mdi:restart
    service_data: {}
```

### 🎯 **Quick Action Buttons**

```yaml
type: horizontal-stack
cards:
  - type: button
    name: "🧪 Test"
    icon: mdi:flask
    tap_action:
      action: call-service
      service: nl_alert.test_alert
    show_name: true
    show_icon: true
  - type: button
    name: "🔄 Reset"
    icon: mdi:restart
    tap_action:
      action: call-service
      service: nl_alert.reset_alerts
    show_name: true
    show_icon: true
```

### 📋 **Developer Services Panel**

Voor ontwikkelaars - gebruik in Developer Tools → Services:

```yaml
# Test Alert Service
service: nl_alert.test_alert

# Reset Alerts Service  
service: nl_alert.reset_alerts
```

### 🤖 **Automation Examples**

Gebruik services in automatiseringen:

```yaml
# Test alert bij opstarten van Home Assistant
alias: "NL-Alert: Test bij opstarten"
trigger:
  - platform: homeassistant
    event: start
action:
  - delay: "00:01:00"  # Wacht 1 minuut
  - service: nl_alert.test_alert

# Reset alerts elke nacht om 3:00
alias: "NL-Alert: Nachtelijke reset"
trigger:
  - platform: time
    at: "03:00:00"
action:
  - service: nl_alert.reset_alerts
```

**💡 Tip**: Services zijn nu onderdeel van de integratie zelf - geen aparte button entities meer nodig!