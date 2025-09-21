# Setup Instructions for Air Quality Monitoring App

## Prerequisites
- **Android Studio** (latest version)
- **Android SDK API Level 26+** (Android 8.0+)
- **Java 11** or higher
- **Git** for cloning the repository

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/crazysandman/air_quality.git
cd air_quality
```

### 2. Setup Mapbox API Key
1. Go to [Mapbox Account](https://account.mapbox.com/access-tokens/)
2. Create a free account (if needed)
3. Generate a new access token
4. Copy the token (starts with `pk.`)

### 3. Configure Android Project
```bash
cd air_quality_app_android
```

Edit `local.properties` file:
```properties
sdk.dir=/path/to/your/Android/sdk
MAPBOX_ACCESS_TOKEN=pk.your_actual_mapbox_token_here
```

### 4. Open in Android Studio
1. Launch Android Studio
2. **File** → **Open** → Select `air_quality_app_android` folder
3. Wait for Gradle sync to complete

### 5. Run the App

#### Option A: Using Emulator
1. **Tools** → **AVD Manager**
2. Create new Virtual Device (API 26+)
3. **Run** → **Run 'app'**

#### Option B: Using Physical Device
1. Enable Developer Options on Android device
2. Enable USB Debugging
3. Connect device via USB
4. **Run** → **Run 'app'**

## Backend (Optional)
The app works with live data from a deployed backend. To run locally:

```bash
cd backend
pip install fastapi uvicorn sqlalchemy python-dotenv requests
uvicorn main:app --reload
```

## Features to Test
- ✅ Interactive map with Berlin air quality stations
- ✅ Color-coded AQI markers (tap for details)
- ✅ GPS location services
- ✅ Station information cards
- ✅ Real-time data updates

## Troubleshooting

### Build Errors
- Ensure Android SDK is properly installed
- Check Java version (Java 11+ required)
- Clean and rebuild: **Build** → **Clean Project**

### Map Not Loading
- Verify Mapbox API token is correctly set
- Check internet connection
- Ensure app has network permissions

### Location Not Working
- Grant location permissions when prompted
- Enable GPS on device/emulator
- In emulator: **Extended Controls** → **Location**

## Expected Behavior
- App shows interactive map centered on Berlin
- ~10-20 air quality stations displayed as colored boxes
- Tap station → detailed information card
- Location button → center map on user's position
- All UI elements positioned at bottom of screen


