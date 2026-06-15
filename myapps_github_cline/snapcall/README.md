# 📱 SnapCall

**Snap a number. Make the call.**

SnapCall is a mobile app that uses your phone's camera to detect phone numbers from billboards, posters, business cards, and more. Once detected, simply tap to call.

## ✨ Features

- 📸 **Camera Scanning** – Point your camera at any phone number
- 🔍 **OCR Recognition** – Powered by Google ML Kit (on-device, offline)
- 📞 **One-Tap Calling** – Tap any detected number to call immediately
- 🔢 **Multiple Numbers** – Detects all phone numbers in the frame
- 🌍 **International Formats** – Supports various phone number formats worldwide
- 🔒 **Privacy First** – All processing happens on-device, no data leaves your phone
- 🌙 **Dark Mode** – Automatic dark/light theme support (Material 3)

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Framework | Flutter 3.44.2 (Dart 3.12.2) |
| OCR Engine | Google ML Kit Text Recognition |
| Camera | Flutter Camera Plugin |
| Phone Dialing | url_launcher |
| Permissions | permission_handler |
| Build System | Gradle 8.14, AGP 8.11.1, Kotlin 2.2.20 |
| Min Android | API 26 (Android 8.0) |
| Target Android | API 36 |

## 📁 Project Structure

```
snapcall/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── screens/
│   │   ├── home_screen.dart         # Home screen with scan button
│   │   ├── camera_screen.dart       # Camera view + capture
│   │   └── result_screen.dart       # Detected numbers + call
│   └── services/
│       └── ocr_service.dart         # ML Kit OCR + regex parsing
├── android/                         # Android configuration
│   ├── app/build.gradle             # compileSdk 36, minSdk 26
│   ├── settings.gradle              # Kotlin 2.2.20, AGP 8.11.1
│   └── gradle/wrapper/              # Gradle 8.14
├── ios/                             # iOS configuration
├── assets/                          # App assets
├── pubspec.yaml                     # Dependencies
├── HOW_TO_RUN_THIS_APP.txt          # Step-by-step run guide
└── README.md                        # This file
```

## 🚀 Getting Started

### Prerequisites

1. **Flutter SDK** (3.44.2+) at `C:\flutter`
2. **Android Studio** with Android SDK 36
3. **Environment variables:**
   ```bash
   setx ANDROID_HOME "C:\Users\I070494\AppData\Local\Android\Sdk"
   setx JAVA_HOME "C:\Program Files\Android\Android Studio\jbr"
   ```

### Quick Start

```bash
# Navigate to project
cd "C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\snapcall"

# Get dependencies
C:\flutter\bin\flutter pub get

# Connect Android phone (USB Debugging ON) and run
C:\flutter\bin\flutter run
```

### Build Release

```bash
# Build App Bundle (for Google Play)
C:\flutter\bin\flutter build appbundle --release

# Build APK (for direct install)
C:\flutter\bin\flutter build apk --release
```

Output:
- AAB: `build/app/outputs/bundle/release/app-release.aab`
- APK: `build/app/outputs/flutter-apk/app-release.apk`

## 📱 Supported Phone Number Formats

The app recognizes various formats:
- `+421 912 345 678` (international with +)
- `00421 912 345 678` (international with 00)
- `0912 345 678` (local)
- `(02) 1234 5678` (with area code)
- `+1-234-567-8901` (US format)
- `234.567.8901` (dot-separated)
- And many more...

## 🏪 Publishing

### Google Play Store
1. Create account: https://play.google.com/console ($25 one-time fee)
2. Build signed AAB: `flutter build appbundle --release`
3. Upload to Play Console
4. Fill app listing, screenshots, privacy policy
5. Submit for review (1-3 days)

### Apple App Store (future)
1. Create account: https://developer.apple.com ($99/year)
2. Build with Xcode on macOS
3. Upload via App Store Connect
4. Submit for review

## 📄 Privacy Policy

SnapCall processes all images locally on your device using Google ML Kit. No images or phone numbers are transmitted to any server. The app requires camera permission solely for the purpose of scanning phone numbers.

## 📝 License

MIT License - Free to use and modify.

---

*Built with ❤️ using Flutter & Google ML Kit*