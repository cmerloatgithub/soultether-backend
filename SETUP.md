# SoulTether Setup Guide

## Installation

### Dependencies
```bash
pip install swisseph kivy requests
```

### Ephemeris Configuration
1. Download Swiss Ephemeris: `git clone https://github.com/aloistr/swisseph.git`
2. Update `EPHE_PATH` in `soultether_mobile.py` to point to your local ephe directory:
   ```python
   EPHE_PATH = "/path/to/swisseph-master/ephe"
   ```

## Geocoding Setup (Optional)

### Using Geoapify (Recommended)
For faster, more reliable geocoding, set your Geoapify API key as an environment variable:

```bash
export GEOAPIFY_API_KEY=88242886b01442bc9caa4e61eeeecdd9
python soultether_mobile.py
```

**macOS/Linux persistent setup** (add to `~/.bashrc` or `~/.zshrc`):
```bash
echo 'export GEOAPIFY_API_KEY=88242886b01442bc9caa4e61eeeecdd9' >> ~/.zshrc
source ~/.zshrc
```

### Fallback (Free - Nominatim)
If no API key is set, the app automatically falls back to Nominatim (OpenStreetMap) for free geocoding.

## Running the App

```bash
# With Geoapify
export GEOAPIFY_API_KEY=88242886b01442bc9caa4e61eeeecdd9
python soultether_mobile.py

# Without API key (uses free Nominatim)
python soultether_mobile.py
```

## Usage

1. **Birth Date**: Enter in `YYYY-MM-DD` format
2. **Birth Time**: Enter in `HH:MM` (24-hour format)
3. **Location**: Enter city name, optionally with country/state (e.g., "New York, USA" or "Paris")
4. Click **ACTIVATE** to calculate
5. Click **Save .txt** to export the reading

## Features

- **360° Flower of Life**: 19 fixed nodes evenly distributed on the zodiac wheel
- **Cardinal Alignment**: 0° = North; nodes aligned to sacred geometry
- **Celestial Detection**: Checks Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, North Node
- **Interpretation Engine**: Text-driven analysis based on Astrodatabank principles
- **Placidus Houses**: Full 12-house system calculations
- **Mobile-Ready**: Kivy cross-platform UI
