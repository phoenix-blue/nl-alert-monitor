# Add NL-Alert integration icons

This PR adds brand assets for the NL-Alert Home Assistant integration.

## Integration Details
- **Domain**: `nl_alert`
- **Name**: NL-Alert Rookpluim Detector  
- **Type**: Custom Integration
- **Repository**: https://github.com/phoenix-blue/nl-alert-monitor
- **HACS**: Yes, HACS compatible

## Description
NL-Alert integration for Home Assistant that monitors Dutch emergency alerts and provides advanced chemical incident detection with GPS-based plume modeling, atmospheric dispersion calculations, and wind direction analysis.

## Icon Design
The icon incorporates Dutch flag colors (orange/blue) with:
- Warning triangle for emergency alerts
- Wind pattern lines for smoke/chemical plume detection  
- Compass rose for wind direction indication
- "NL" text for Dutch identification

## Files Added
- `custom_integrations/nl_alert/icon.png` (256x256px)
- `custom_integrations/nl_alert/icon@2x.png` (512x512px)  
- `custom_integrations/nl_alert/logo.png` (256x256px)
- `custom_integrations/nl_alert/logo@2x.png` (512x512px)

## Verification
- [x] All images are PNG format
- [x] Icons are 256x256 (standard) and 512x512 (hDPI)
- [x] Images have transparency
- [x] Images are optimized for web
- [x] Domain matches integration manifest.json
- [x] Integration is available in HACS

## Integration Repository
The integration is available at: https://github.com/phoenix-blue/nl-alert-monitor
