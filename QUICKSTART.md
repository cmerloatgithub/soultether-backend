# SoulTether: Quick Start Guide

## What You Have

1. **Flask Backend** (`app.py`)
   - REST API for calculating astrological readings
   - Logs interpretations for LLM learning
   - Geocodes birth locations
   - Returns readings in JSON format

2. **Native iOS App** (Swift/SwiftUI)
   - Three screens: Opening, Birth Data, Reader
   - Matches your design mockups exactly
   - Calls Flask backend via HTTP
   - Saves readings locally on device

3. **Deployment Files**
   - `Procfile` for Railway deployment
   - `requirements.txt` with all Python dependencies

---

## Deploy Backend in 5 Minutes

1. Push code to GitHub
2. Sign up for Railway.app (free)
3. Connect your GitHub repo
4. Railway auto-deploys (gets you a URL like `https://soultether-abc.up.railway.app`)
5. Copy that URL into the iOS app code

**Backend is now live and available 24/7.**

---

## Build iOS App in Xcode

1. Open Xcode
2. Create new SwiftUI project
3. Copy the Swift files into your project:
   - `SoulTetherApp.swift`
   - `Views/OpeningScreenView.swift`
   - `Views/BirthDataScreenView.swift`
   - `Views/ReaderScreenView.swift`
4. Add your images: `SoulTetherOpen.png`, `SoulTetherIcon.png`, `SoulTetherWhiteIcon.png`
5. Replace `"https://your-railway-app.up.railway.app"` with your actual Railway URL
6. Run on simulator: Product → Run

**App is now working on your device.**

---

## Submit to App Store

1. Sign up for Apple Developer Program ($99/year)
2. Create app listing on App Store Connect
3. Build for release: Product → Archive → Distribute App
4. Fill in metadata (description, screenshots, etc.)
5. Submit for review
6. Apple reviews within 24-48 hours
7. Once approved, it goes live automatically

**Your app is now on the App Store.**

---

## How Data Flows

```
User fills birth date/time/location
  ↓
iOS app sends HTTP POST to Railway backend
  ↓
Flask backend calculates chart + FOL nodes
  ↓
Backend logs interpretation text (not birth data) for LLM training
  ↓
Backend returns reading to iOS app
  ↓
iOS displays reading and lets user save to device
```

**No data stored anywhere** except:
- Interpretations logged on backend for LLM fine-tuning
- Readings saved locally on user's device only

---

## After Launch

Monitor and improve:
- Railway dashboard shows API activity
- `training_data.jsonl` accumulates interpretations
- Use this data to fine-tune your LLM model
- Push backend improvements live instantly (no app update needed)
- Fix bugs in app → resubmit to App Store (takes 24-48hr)

---

## Key Files

- **Backend**: `/Applications/soultether/app.py`
- **Deployment**: `/Applications/soultether/DEPLOYMENT.md`
- **iOS Code**: `/Applications/soultether/Views/*.swift` + `SoulTetherApp.swift`
- **Configuration**: `buildozer.spec` (no longer needed with Swift app)

---

## Support

- Railway docs: railway.app/docs
- SwiftUI reference: developer.apple.com/tutorials/SwiftUI
- App Store submission: appstoreconnect.apple.com
