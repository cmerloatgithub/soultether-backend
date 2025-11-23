---
description: Repository Information Overview
alwaysApply: true
---

# SoulTether Information

## Summary

SoulTether is a mobile-ready astrology application that combines advanced astrological calculations with an intuitive user interface. The application implements Placidus house system, Flower of Life principles, and Phantom Houses for comprehensive natal chart readings and spiritual interpretations. Built with Kivy framework for cross-platform mobile deployment.

## Structure

- **soultether_mobile.py**: Main application file containing UI logic and astrology calculation engine
- **flower-of-life-360.svg**: Asset file for Flower of Life visualization
- **instructions.txt**: Deployment and setup guidelines
- **.pytest_cache/**: Python test cache directory (indicates pytest support)

## Language & Runtime

**Language**: Python
**Version**: 3.13.1+
**Framework**: Kivy (mobile framework)
**Astronomy Library**: Swiss Ephemeris (swisseph)

## Dependencies

**Main Dependencies**:
- **swisseph**: Swiss Ephemeris for astronomical calculations and house system computations
- **kivy**: Cross-platform mobile application framework for UI rendering
- **kivy.uix**: Kivy UI components (BoxLayout, Label, TextInput, Button, Popup, ScrollView)
- **os, json, random, datetime**: Python standard library modules

**Standard Library Modules**:
- os (file and environment operations)
- json (data serialization)
- random (randomization for interpretations)
- datetime (timestamp operations)

## Main Application

**Entry Point**: `soultether_mobile.py`

**Core Features**:
- Natal chart calculation with Placidus house system
- Phantom House layers implementation
- Flower of Life framework integration
- Interpretation database with spiritual guidance
- Mobile-optimized UI with scrollable content
- JSON-based data export for readings

**Configuration**:
- Ephemeris path: `EPHE_PATH = "/swisseph-master/ephe"` (requires local configuration)
- Sign database with all 12 zodiac signs
- Interpretation database for various planetary/house combinations

## Build & Installation

**Setup Commands**:
```bash
# Install dependencies
pip install swisseph kivy

# Configure ephemeris path
# Edit soultether_mobile.py and update EPHE_PATH to your swisseph ephe directory

# Run application
python soultether_mobile.py
```

**Deployment Options** (per instructions.txt):
- **FlutterFlow/Adalo**: Visual no-code mobile builder for UI
- **GitHub Actions**: HTTP trigger to run Python script with local ephemeris
- **GitHub Pages**: Host readings as downloadable text files

## Application Architecture

**Main Classes & Components**:
- Kivy App base class for application lifecycle
- BoxLayout containers for responsive UI
- TextInput fields for birth data entry
- Button controls for calculations and navigation
- Popup windows for detailed information display
- ScrollView for content overflow handling

**Calculation Engine**:
- Swiss Ephemeris wrapper for astronomical calculations
- House system computations (Placidus implementation)
- Phantom layer calculations for multi-dimensional analysis
- Zodiac sign mapping and degree calculations

**Data Processing**:
- JSON serialization for reading storage
- Interpretation database lookup system
- Dynamic text generation for personalized readings
- API integration points for geocoding and astrodata

## Testing

**Framework**: pytest (indicated by .pytest_cache directory)
**Note**: No explicit test files present in repository; testing framework available for future test implementation.
