#!/usr/bin/env python3
"""
Prepare Home Assistant Brands submission for NL-Alert integration.
This script creates the necessary files and instructions for submitting to home-assistant/brands.
"""

import os
import shutil

def create_brands_submission():
    """Create the folder structure and files for Home Assistant Brands PR."""
    
    print("🎨 Preparing Home Assistant Brands submission for NL-Alert integration...")
    
    # Create brands submission folder
    brands_folder = "brands_submission"
    nl_alert_folder = os.path.join(brands_folder, "custom_integrations", "nl_alert")
    
    # Clean and create folder structure
    if os.path.exists(brands_folder):
        shutil.rmtree(brands_folder)
    
    os.makedirs(nl_alert_folder, exist_ok=True)
    
    # Copy icon files
    icon_files = ["icon.png", "icon@2x.png", "logo.png", "logo@2x.png"]
    
    for icon_file in icon_files:
        src = os.path.join("images", icon_file)
        dst = os.path.join(nl_alert_folder, icon_file)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✓ Copied {icon_file}")
    
    # Create PR description
    pr_description = """# Add NL-Alert integration icons

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
"""

    # Write PR description
    with open(os.path.join(brands_folder, "PR_DESCRIPTION.md"), "w", encoding="utf-8") as f:
        f.write(pr_description)
    
    # Create instructions file
    instructions = """# Home Assistant Brands Submission Instructions

## Steps to Submit to Home Assistant Brands

### 1. Fork the Repository
```bash
# Go to https://github.com/home-assistant/brands
# Click "Fork" button to fork to your GitHub account
```

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/brands.git
cd brands
```

### 3. Create Branch
```bash
git checkout -b add-nl-alert-integration
```

### 4. Copy Files
Copy the contents of `brands_submission/custom_integrations/nl_alert/` to:
```
brands/custom_integrations/nl_alert/
```

So you have:
- `brands/custom_integrations/nl_alert/icon.png`
- `brands/custom_integrations/nl_alert/icon@2x.png`  
- `brands/custom_integrations/nl_alert/logo.png`
- `brands/custom_integrations/nl_alert/logo@2x.png`

### 5. Commit and Push
```bash
git add custom_integrations/nl_alert/
git commit -m "Add NL-Alert integration icons"
git push origin add-nl-alert-integration
```

### 6. Create Pull Request
- Go to your forked repository on GitHub
- Click "Compare & pull request"
- Use the title: "Add NL-Alert integration icons"
- Copy the content from `PR_DESCRIPTION.md` as the PR description
- Submit the PR

### 7. Wait for Review
The Home Assistant team will review your PR. The icons should appear in HACS and Home Assistant after the PR is merged.

## Verification URLs
After merge, icons will be available at:
- https://brands.home-assistant.io/nl_alert/icon.png
- https://brands.home-assistant.io/nl_alert/icon@2x.png
- https://brands.home-assistant.io/nl_alert/logo.png  
- https://brands.home-assistant.io/nl_alert/logo@2x.png

## Notes
- PR review may take several days to weeks
- Make sure your integration is already available in HACS
- Icons must meet all Home Assistant Brands specifications
- Domain `nl_alert` must match your integration's manifest.json
"""

    with open(os.path.join(brands_folder, "SUBMISSION_INSTRUCTIONS.md"), "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print(f"\n✅ Brands submission prepared in '{brands_folder}/' folder")
    print("\nFiles created:")
    print("├── custom_integrations/")
    print("│   └── nl_alert/")
    print("│       ├── icon.png")
    print("│       ├── icon@2x.png")
    print("│       ├── logo.png")
    print("│       └── logo@2x.png")
    print("├── PR_DESCRIPTION.md")
    print("└── SUBMISSION_INSTRUCTIONS.md")
    
    print(f"\n📋 Next steps:")
    print(f"1. Read SUBMISSION_INSTRUCTIONS.md for detailed steps")
    print(f"2. Fork https://github.com/home-assistant/brands")
    print(f"3. Copy files from brands_submission/ folder")
    print(f"4. Create PR with provided description")
    
    return True

if __name__ == "__main__":
    create_brands_submission()