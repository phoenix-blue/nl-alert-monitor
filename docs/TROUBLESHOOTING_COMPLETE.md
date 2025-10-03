# 🐛 NL-Alert Troubleshooting Guide

## Huidige Situatie
- ✅ Integratie wordt correct geladen
- ✅ 3 sensors worden aangemaakt (logs tonen dit)
- ✅ 2 binary sensors worden verwacht
- ❌ Geen entiteiten zichtbaar in UI na installatie

## Debug Steps

### 1. **Complete Log Check**
Na herinstallatie, zoek naar deze log berichten:

```log
# Verwacht:
INFO [nl_alert] Setting up NL-Alert integration
DEBUG [nl_alert.sensor] Creating sensor: Actieve Meldingen (alert_count)
DEBUG [nl_alert.sensor] Creating sensor: Ernstige Meldingen (severe_alerts)  
DEBUG [nl_alert.sensor] Creating sensor: Historische Meldingen (historical_alerts)
INFO [nl_alert.sensor] Adding 3 NL-Alert sensors
INFO [nl_alert.sensor] Successfully added 3 NL-Alert sensors
DEBUG [nl_alert.binary_sensor] Creating binary sensor: Actieve Melding (active_alert)
DEBUG [nl_alert.binary_sensor] Creating binary sensor: Ernstige Melding (severe_alert)
INFO [nl_alert.binary_sensor] Adding 2 NL-Alert binary sensors
INFO [nl_alert.binary_sensor] Successfully added 2 NL-Alert binary sensors
```

### 2. **Entity Registry Check**
Na installatie, check direct in Developer Tools:

```yaml
# Template Test:
{{ states | selectattr('entity_id', 'search', 'nl_alert') | map(attribute='entity_id') | list }}

# Verwacht resultaat:
[
  "sensor.nl_alert_actieve_meldingen",
  "sensor.nl_alert_ernstige_meldingen", 
  "sensor.nl_alert_historische_meldingen",
  "binary_sensor.nl_alert_actieve_melding",
  "binary_sensor.nl_alert_ernstige_melding"
]
```

### 3. **Stap-voor-Stap Test**

#### A. Verwijder Integratie Compleet
```yaml
1. Instellingen → Apparaten & Services → NL-Alert
2. "..." → Verwijder
3. Bevestig verwijdering
4. Herstart Home Assistant (belangrijk!)
```

#### B. Installeer Opnieuw Met Debug
```yaml
# Eerst logging inschakelen:
# configuration.yaml:
logger:
  default: warning  
  logs:
    custom_components.nl_alert: debug
    homeassistant.helpers.entity_platform: debug
    homeassistant.helpers.entity_registry: debug

# Dan herstart en installeer
```

#### C. Monitor Setup Process
```yaml
# Check logs direct na installatie:
1. Ga naar Instellingen → Systeem → Logs
2. Filter op "nl_alert"
3. Kijk naar de volgorde van berichten
```

## Mogelijke Problemen

### **Probleem 1: Entity Registry Conflict**
```log
# Als je dit ziet:
ERROR [entity_registry] Entity sensor.nl_alert_actieve_meldingen is already registered

# Oplossing:
1. Stop Home Assistant  
2. Verwijder .storage/entity_registry
3. Start Home Assistant
4. Installeer NL-Alert opnieuw
```

### **Probleem 2: Platform Setup Fout**
```log  
# Als je dit ziet:
ERROR [entity_platform] Error setting up platform sensor

# Mogelijke oorzaken:
- Coordinator data niet beschikbaar
- Import fout in code
- Unique ID conflict
```

### **Probleem 3: Async Setup Timing**
```log
# Check of dit in de juiste volgorde gebeurt:
1. __init__.py: coordinator aangemaakt
2. __init__.py: initial data refresh
3. sensor.py: sensoren toegevoegd
4. binary_sensor.py: binary sensoren toegevoegd
```

## Test Commands

### **Live Entity Check**
```yaml
# In Developer Tools → Services:
service: homeassistant.reload_config_entry
data:
  entry_id: [your_nl_alert_entry_id]
```

### **Manual Entity Creation Test**  
```yaml
# In Developer Tools → Services:
service: persistent_notification.create
data:
  title: "NL-Alert Test"
  message: >
    Entities: {{ states | selectattr('entity_id', 'search', 'nl_alert') | list | length }}
    
    Details: {{ states | selectattr('entity_id', 'search', 'nl_alert') | map(attribute='entity_id') | list }}
```

### **State Dump**
```yaml
# In Developer Tools → Services:  
service: system_log.write
data:
  message: "NL-Alert entities: {{ states | selectattr('entity_id', 'search', 'nl_alert') | map(attribute='entity_id') | list }}"
  level: warning
```

## Expected Behavior

Na een succesvolle installatie zou je moeten zien:

### **In Developer Tools → States:**
```yaml
sensor.nl_alert_actieve_meldingen: "0"
sensor.nl_alert_ernstige_meldingen: "0"  
sensor.nl_alert_historische_meldingen: "1"
binary_sensor.nl_alert_actieve_melding: "off"
binary_sensor.nl_alert_ernstige_melding: "off"
```

### **In Entiteiten pagina:**
- 5 entiteiten met "NL-Alert" in de naam
- Allemaal gekoppeld aan het NL-Alert apparaat
- Status "Ingeschakeld"

## Next Action

**Herinstalleer met uitgebreide logging en deel de volledige logs!** 📋