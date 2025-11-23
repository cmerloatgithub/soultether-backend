# SoulTether: iOS App Store Deployment Guide

This guide covers deploying the Python backend to Railway and building the native iOS app for the App Store.

## Part 1: Deploy Flask Backend to Railway

### Prerequisites
- Railway account (free at railway.app)
- GitHub repository with your SoulTether code
- Git CLI installed locally

### Steps

1. **Push code to GitHub**
   ```bash
   cd /Applications/soultether
   git init
   git add .
   git commit -m "Initial SoulTether backend commit"
   git remote add origin https://github.com/YOUR_USERNAME/soultether.git
   git branch -M main
   git push -u origin main
   ```

2. **Create Railway project**
   - Go to railway.app and sign in
   - Click "Create a new project"
   - Select "Deploy from GitHub"
   - Authorize GitHub and select your soultether repository

3. **Configure Railway environment**
   - Railway auto-detects Flask app from `app.py`
   - It will use `Procfile` to run: `gunicorn app:app`
   - The app will be accessible at a Railway-provided URL (e.g., `https://soultether-production.up.railway.app`)

4. **Set environment variables (if needed)**
   - In Railway dashboard, go to your project
   - Click "Variables"
   - Add `GEOAPIFY_API_KEY` if you have a Geoapify account (optional; app falls back to Nominatim)
   - Add `PORT=5000` (Railway assigns a port dynamically, but Flask defaults to 5000)

5. **Deploy**
   - Railway auto-deploys when you push to GitHub
   - Monitor deployment in the Railway dashboard
   - Once live, test the API:
     ```bash
     curl https://your-railway-url/health
     ```

### Backend API Endpoints

**Health check:**
```
GET /health
Response: {"status": "ok", "service": "SoulTether API"}
```

**Calculate reading:**
```
POST /calculate_reading
Content-Type: application/json

{
  "birth_date": "1995-06-15",
  "hour": 14,
  "minute": 30,
  "is_am": false,
  "location": "New York, USA"
}

Response:
{
  "success": true,
  "reading": "...",
  "chart_data": { ... },
  "error": null
}
```

**Training data logs:**
- Stored in `training_data.jsonl` on the server
- Each line: `{"timestamp": "...", "chart_date": "...", "fol_hits_count": N, "interpretation": "..."}`
- Contains only interpretations, not raw birth data

---

## Part 2: Build Native iOS App in Xcode

### Prerequisites
- macOS with Xcode 14+
- Apple Developer account ($99/year for App Store submission)
- Your Railway backend URL

### Project Setup

1. **Create new Xcode project**
   - Open Xcode
   - File → New → Project
   - Choose "App"
   - Name: `SoulTether`
   - Interface: SwiftUI
   - Life Cycle: SwiftUI App

2. **Add app files**
   Copy these Swift files into your Xcode project:
   - `SoulTetherApp.swift` → Main app file with AppViewModel
   - `Views/OpeningScreenView.swift` → Opening screen
   - `Views/BirthDataScreenView.swift` → Birth data input
   - `Views/ReaderScreenView.swift` → Reading display

3. **Add image assets**
   - Drag `SoulTetherOpen.png`, `SoulTetherIcon.png`, `SoulTetherWhiteIcon.png` into Assets.xcassets
   - Name them: `SoulTetherOpen`, `SoulTetherIcon`, `SoulTetherWhiteIcon`

4. **Configure backend URL**
   - In `SoulTetherApp.swift`, find: `private let baseURL = "https://your-railway-app.up.railway.app"`
   - Replace with your actual Railway URL

5. **Set app metadata**
   - Select project root in Xcode
   - Select "SoulTether" target
   - General tab:
     - Display Name: "SoulTether"
     - Bundle Identifier: "com.soultether.app"
     - Version: "1.0.0"
     - Build: "1"
     - Supported Platforms: iOS 14.0+

6. **Configure icons and launch screen**
   - Assets.xcassets → Add app icon (1024x1024 PNG)
   - Xcode will auto-generate all sizes

### Test on Simulator

```bash
# From Xcode, select iPhone 15 from simulator dropdown
# Product → Run (⌘R)
```

The app should:
1. Show Opening screen with blue fingerprint button
2. Navigate to Birth Data screen when button pressed
3. Accept date/time/location input
4. Call your Railway API and show the reading

### Build for App Store

1. **Create app signing certificate**
   - Xcode → Preferences → Accounts
   - Add Apple ID
   - Let Xcode auto-manage signing

2. **Create App Store listing**
   - Go to App Store Connect (appstoreconnect.apple.com)
   - Click "My Apps"
   - Click "+"
   - Create new app with:
     - Bundle ID: `com.soultether.app`
     - Name: `SoulTether`
     - Primary Language: English
     - Category: Lifestyle

3. **Archive and upload**
   - In Xcode: Product → Archive
   - Once complete, "Distribute App" → App Store Connect
   - Follow prompts to upload build
   - Fill in metadata on App Store Connect:
     - Description (max 4000 chars)
     - Keywords
     - Preview screenshots (iPhone, iPad)
     - Support URL
     - Privacy Policy URL

4. **Submit for review**
   - Click "Submit for Review" on App Store Connect
   - Apple reviews within 24-48 hours
   - Once approved, it becomes live

### App Store Submission Checklist

- [ ] App name: "SoulTether"
- [ ] Privacy policy URL pointing to your privacy statement
- [ ] Category: "Lifestyle" or "Health & Fitness"
- [ ] Support contact email
- [ ] Screenshots (iPhone 6.5", iPad Pro 12.9" preferred)
- [ ] Description explaining it requires internet connection
- [ ] No hardcoded API keys
- [ ] Build passes App Store review (no warnings/errors)

---

## Part 3: Post-Launch

### Monitor Backend
- Railway dashboard shows real-time logs
- Check `training_data.jsonl` for accumulated interpretation logs
- Use interpretation data to fine-tune your LLM over time

### Update App
- Bug fixes: Submit new build to App Store (24-48hr review)
- Feature updates: Same process
- Backend updates: Deploy to Railway (instant, no app update needed for API changes)

### Privacy Compliance
- Keep privacy policy updated
- No personally identifiable info stored
- Birth dates used only to generate readings
- Interpretations anonymized for training

---

## Troubleshooting

**Backend not responding:**
```bash
curl https://your-railway-url/health
# Should return: {"status": "ok", "service": "SoulTether API"}
```

**App can't reach backend:**
- Check URL in `SoulTetherApp.swift` matches Railway URL
- Ensure Railway app is still running (check dashboard)
- Check network connectivity (try on WiFi first)

**Geocoding fails:**
- Nominatim service may be rate-limited
- Add GEOAPIFY_API_KEY to Railway environment
- Location format: "City, Country" (e.g., "New York, USA")

**App Store rejection:**
- Review App Store Connect feedback
- Common issues: Missing privacy policy, misleading claims, crashes
- Test thoroughly before resubmitting
