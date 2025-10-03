# 🎨 NL-Alert Integration Icons

Dit project bevat nu professionele iconen voor de NL-Alert integratie die zichtbaar zijn in HACS en Home Assistant!

## 🖼️ Icon Design

Het icoon is ontworpen met de volgende elementen:

### Visual Elements
- **🇳🇱 Nederlandse Kleuren**: Oranje en blauwe gradient achtergrond (Nederlandse vlag)
- **⚠️ Waarschuwingsdriehoek**: Rode waarschuwingsdriehoek met uitroepteken voor noodsituaties  
- **💨 Windpatroon**: Golvende grijze lijnen die rook/chemische pluimverspreiding voorstellen
- **🧭 Kompasroos**: Witte kompas indicator voor windrichtingfunctionaliteit
- **"NL" Tekst**: Duidelijke identificatie van Nederlandse oorsprong

### Technische Specificaties
- **Formaat**: PNG met transparantie
- **Verhouding**: 1:1 (vierkant)
- **Standaard Grootte**: 256x256 pixels
- **HiDPI Grootte**: 512x512 pixels  
- **Optimalisatie**: Lossless compressie geoptimaliseerd voor web

## 📁 Bestanden

- `images/icon.png` - Standaard resolutie icoon (256x256px)
- `images/icon@2x.png` - Hoge resolutie icoon (512x512px)
- `images/logo.png` - Standaard resolutie logo (256x256px) 
- `images/logo@2x.png` - Hoge resolutie logo (512x512px)

## 🏠 Home Assistant Brands

Voor volledige HACS ondersteuning moeten de iconen worden toegevoegd aan het Home Assistant Brands repository:

### Automatische Weergave
Na toevoeging aan Home Assistant Brands verschijnen de iconen automatisch in:
- ✅ HACS integration store
- ✅ Home Assistant integratie setup  
- ✅ Device en entity cards
- ✅ Integratie configuratiepagina's

### URL Toegang
De iconen worden geserveerd vanaf:
```
https://brands.home-assistant.io/nl_alert/icon.png
https://brands.home-assistant.io/nl_alert/icon@2x.png
https://brands.home-assistant.io/nl_alert/logo.png
https://brands.home-assistant.io/nl_alert/logo@2x.png
```

## 📤 Home Assistant Brands Submission

De `brands_submission/` folder bevat alles wat nodig is voor de Pull Request naar home-assistant/brands:

### Stappen voor Submission:
1. **Fork** https://github.com/home-assistant/brands
2. **Copy** bestanden van `brands_submission/custom_integrations/nl_alert/` 
3. **Plaats** in je fork: `custom_integrations/nl_alert/`
4. **Create PR** met beschrijving uit `PR_DESCRIPTION.md`

### Gedetailleerde Instructies
Zie `brands_submission/SUBMISSION_INSTRUCTIONS.md` voor complete stap-voor-stap gids.

## 🔍 Preview Iconen

Je kunt de iconen nu al bekijken in de `images/` folder van dit repository:
- [icon.png](images/icon.png)
- [icon@2x.png](images/icon@2x.png)

## ⏳ Timeline

1. ✅ **Iconen gemaakt** - Nederlandse themed design met alle vereiste elementen
2. ✅ **Repository geüpdatet** - Iconen toegevoegd aan GitHub repository
3. 🔄 **Brands submission** - Pull Request naar home-assistant/brands (handmatig)
4. ⏳ **Review process** - Home Assistant team review (enkele dagen tot weken)
5. 🎯 **Live in HACS** - Iconen verschijnen automatisch na merge

## 🛠️ Technische Details

De iconen zijn gemaakt met Python/PIL en voldoen aan alle Home Assistant Brands vereisten:
- Correcte bestandsformaten en grootten
- Optimale compressie voor web gebruik
- Transparantie ondersteuning  
- Domain matching (`nl_alert` uit manifest.json)
- Voldoet aan visuele richtlijnen

Na de Home Assistant Brands submission zul je het mooie NL-Alert icoon zien in HACS! 🎨✨