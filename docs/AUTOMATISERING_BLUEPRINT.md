# 🌪️ NL-Alert Smart Ventilatie Automatiseringen

## 🚨 Noodventilatiesysteem bij Chemische Incidenten

Deze automatiseringen helpen je ventilatie automatisch te beheren bij chemische incidenten in de buurt.

### ✋ **Automatische Ventilator STOP bij Gevaar**

Gebruik deze automatisering om je ventilatie **automatisch uit te schakelen** wanneer er gevaarlijke chemische stoffen gedetecteerd worden.

```yaml
# Automatisering: Stop ventilatie bij chemisch gevaar
alias: "🚨 NL-Alert: STOP Ventilatie bij Gevaar"
description: "Schakelt ventilatie uit bij chemische incidenten"
trigger:
  - platform: numeric_state
    entity_id: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    above: 15  # Risico percentage boven 15%
  - platform: state
    entity_id: binary_sensor.nl_alert_pluim_monitor_gevaar_alarm
    to: "on"
condition:
  - condition: state
    entity_id: binary_sensor.nl_alert_pluim_monitor_gevaar_alarm
    state: "on"
action:
  # 🔴 STOP alle ventilatoren
  - service: switch.turn_off
    target:
      entity_id: 
        - switch.mechanische_ventilatie  # Vervang door jouw ventilator
        - switch.badkamer_afzuiging      # Voeg meer ventilatoren toe
        - switch.keuken_afzuigkap        
  
  # 📱 Stuur notificatie
  - service: notify.mobile_app_jouw_telefoon  # Vervang door jouw device
    data:
      title: "🚨 VENTILATIE GESTOPT"
      message: >
        Chemisch incident gedetecteerd! 
        Risico: {{ states('sensor.nl_alert_pluim_monitor_pluim_risico_kompas') }}%
        Bericht: {{ state_attr('sensor.nl_alert_pluim_monitor_pluim_risico_kompas', 'message') }}
      data:
        actions:
          - action: "HANDMATIG_AANZETTEN"
            title: "Handmatig aanzetten"
        priority: high
        
  # 🔊 Spraakmelding (optioneel)
  - service: tts.speak
    target:
      entity_id: media_player.google_home  # Vervang door jouw speaker
    data:
      message: >
        Attentie! Chemisch incident in de buurt. Alle ventilatie is automatisch uitgeschakeld 
        vanwege {{ state_attr('sensor.nl_alert_pluim_monitor_pluim_risico_kompas', 'risk_level') }}.

mode: single
```

### 🔄 **Automatische Ventilator HERSTART na Gevaar**

```yaml
# Automatisering: Herstart ventilatie na gevaar
alias: "✅ NL-Alert: Herstart Ventilatie na Veiligheid"
description: "Herstart ventilatie wanneer gevaar voorbij is"
trigger:
  - platform: numeric_state
    entity_id: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    below: 5   # Risico percentage onder 5%
    for: "00:30:00"  # 30 minuten veilig
  - platform: state
    entity_id: binary_sensor.nl_alert_pluim_monitor_gevaar_alarm
    to: "off"
    for: "00:30:00"
condition:
  - condition: numeric_state
    entity_id: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    below: 5
action:
  # 📱 Vraag bevestiging
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: "✅ Veilig om ventilatie te herstarten"
      message: "Risico is gedaald naar {{ states('sensor.nl_alert_pluim_monitor_pluim_risico_kompas') }}%. Ventilatie herstarten?"
      data:
        actions:
          - action: "HERSTART_VENTILATIE"
            title: "Ja, herstart ventilatie"
          - action: "BLIJF_UIT"
            title: "Nee, laat uit staan"

  # Wacht op gebruiker actie of automatisch na 5 minuten
  - wait_for_trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "HERSTART_VENTILATIE"
    timeout: "00:05:00"
    
  # 🟢 Start ventilatie (als bevestigd of timeout)
  - service: switch.turn_on
    target:
      entity_id: 
        - switch.mechanische_ventilatie
        - switch.badkamer_afzuiging     
        
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: "🟢 Ventilatie Hersteld"
      message: "Normale ventilatie is hervat. Risico: {{ states('sensor.nl_alert_pluim_monitor_pluim_risico_kompas') }}%"

mode: single
```

### 🎯 **Slimme Windrichting Ventilatie**

```yaml
# Automatisering: Ventilatie op basis van windrichting
alias: "🌬️ NL-Alert: Slimme Windrichting Ventilatie"
description: "Past ventilatie aan op basis van windrichting en risico"
trigger:
  - platform: state
    entity_id: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: wind_direction
  - platform: numeric_state
    entity_id: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    above: 5
condition:
  - condition: numeric_state
    entity_id: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    above: 5
    below: 15  # Tussen 5-15% risico
action:
  - choose:
      # Wind van het ZUIDEN (pluim naar het noorden)
      - conditions:
          - condition: template
            value_template: >
              {% set wind_dir = state_attr('sensor.nl_alert_pluim_monitor_pluim_risico_kompas', 'wind_direction') %}
              {{ wind_dir >= 135 and wind_dir <= 225 }}
        sequence:
          - service: switch.turn_off
            entity_id: switch.noordzijde_ventilatie  # Uit aan noordzijde
          - service: switch.turn_on  
            entity_id: switch.zuidzijde_ventilatie   # Aan aan zuidzijde
          
      # Wind van het NOORDEN (pluim naar het zuiden) 
      - conditions:
          - condition: template
            value_template: >
              {% set wind_dir = state_attr('sensor.nl_alert_pluim_monitor_pluim_risico_kompas', 'wind_direction') %}
              {{ wind_dir >= 315 or wind_dir <= 45 }}
        sequence:
          - service: switch.turn_off
            entity_id: switch.zuidzijde_ventilatie   # Uit aan zuidzijde
          - service: switch.turn_on
            entity_id: switch.noordzijde_ventilatie  # Aan aan noordzijde

mode: single
```

### 📊 **Dashboard Card Configuratie**

Voeg deze card toe aan je dashboard voor een mooie visuele weergave:

```yaml
# Lovelace Dashboard Card
type: entities
title: 🌪️ NL-Alert Pluim Monitor  
entities:
  - entity: sensor.nl_alert_pluim_monitor_actieve_waarschuwingen
    name: Actieve Waarschuwingen
  - entity: sensor.nl_alert_pluim_monitor_gevaarlijke_incidenten  
    name: Gevaarlijke Incidenten
  - entity: binary_sensor.nl_alert_pluim_monitor_gevaar_alarm
    name: Gevaar Status
  - type: divider
  - entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    name: Risico Percentage
    icon: mdi:compass-rose
  - type: attribute
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: risk_level
    name: Risico Niveau
  - type: attribute  
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas
    attribute: wind_direction_text
    name: Wind Richting
  - type: attribute
    entity: sensor.nl_alert_pluim_monitor_pluim_risico_kompas  
    attribute: message
    name: Status Bericht
state_color: true
```

### 🔧 **Installatie Instructies**

1. **Vervang entity names**: Pas alle `switch.mechanische_ventilatie` etc. aan naar jouw eigen apparaten
2. **Stel notificaties in**: Vervang `notify.mobile_app_jouw_telefoon` door jouw device
3. **Test de automatisering**: Start met een hoge threshold (50%) om te testen
4. **Pas thresholds aan**: Stel risico percentages in die bij jouw situatie passen
5. **Voeg meer apparaten toe**: Denk aan airco, raamopeners, luchtreiniger

### ⚙️ **Geavanceerde Opties**

```yaml
# Input helpers voor configuratie
input_number:
  nl_alert_risk_threshold:
    name: "Risico Drempel (%)"
    min: 0
    max: 100
    step: 5
    initial: 15
    icon: mdi:percent
    
input_boolean:
  nl_alert_auto_ventilation:
    name: "Automatische Ventilatie Controle"
    initial: true
    icon: mdi:auto-fix
```

**Pro Tip**: Start met **handmatige controle** en schakel geleidelijk over naar automatisch! 🎯