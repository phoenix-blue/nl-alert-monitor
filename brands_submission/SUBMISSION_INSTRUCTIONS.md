# Home Assistant Brands Submission Instructions

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
