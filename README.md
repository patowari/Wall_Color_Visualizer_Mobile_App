# Wall Color Visualizer Mobile App

A powerful mobile application that allows users to visualize different paint colors on their walls in real-time using computer vision and augmented reality techniques.

## 🌟 Features

- **📷 Camera Integration**: Capture photos directly from your phone's camera
- **🖼️ Gallery Support**: Upload existing images from your device
- **🤖 AI Wall Detection**: Automatic wall detection using advanced computer vision
- **🎨 Color Picker**: Choose from any color to apply to detected walls
- **🔧 Adjustable Blending**: Control how the color blends with the original wall
- **💾 Save & Share**: Save processed images and share with others
- **📱 Mobile Optimized**: Built specifically for Android devices

## 🛠️ Technology Stack

- **Frontend**: Kivy (Python mobile framework)
- **Computer Vision**: OpenCV for image processing and wall detection
- **Build System**: Buildozer for Android APK generation
- **Image Processing**: NumPy for efficient array operations
- **Device Integration**: Plyer for native device features

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Java 8 or higher (for Android building)
- Android SDK (optional - Buildozer can download automatically)
- 4GB+ RAM recommended for building
- 10GB+ free disk space

### Python Dependencies
```
kivy>=2.1.0
opencv-python>=4.8.0
numpy>=1.21.0
plyer>=2.1.0
Pillow>=9.0.0
buildozer>=1.4.0
cython>=0.29.0
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/patowari/Wall_Color_Visualizer_Mobile_App.git
cd Wall_Color_Visualizer_Mobile_App

# Run automated setup
python setup_and_build.py setup
```

### 2. Test Locally (Optional)
```bash
# Test the app on your computer first
python setup_and_build.py test
```

### 3. Build APK
```bash
# Build debug APK
python setup_and_build.py debug

# Or build everything at once
python setup_and_build.py all
```

## 📱 Installation Steps

### Manual Setup (Alternative)

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install buildozer cython
   ```

2. **Initialize Buildozer**
   ```bash
   buildozer init
   ```

3. **Build the APK**
   ```bash
   # For debug version
   buildozer android debug
   
   # For release version (requires keystore)
   buildozer android release
   ```

## 🏗️ Project Structure

```
wall-color-visualizer/
├── main.py                 # Main application file
├── wall_detector.py        # Advanced wall detection module
├── requirements.txt        # Python dependencies
├── buildozer.spec         # Buildozer configuration
├── setup_and_build.py     # Automated build script
├── README.md              # This file
└── assets/                # App assets (if any)
```

## 🎯 How It Works

### 1. Image Acquisition
- **Camera Mode**: Uses Kivy's Camera widget to capture real-time photos
- **Gallery Mode**: FileChooser widget for selecting existing images
- Automatic permission handling for camera and storage access

### 2. Wall Detection Algorithm
The app uses multiple computer vision techniques:

- **Edge Detection**: Canny edge detection to find wall boundaries
- **Color Segmentation**: HSV color space analysis for typical wall colors
- **Texture Analysis**: Local texture patterns to identify smooth wall surfaces
- **Combined Approach**: Weighted combination of all methods for robust detection

### 3. Color Application
- **Mask-based Overlay**: Applies selected color only to detected wall regions
- **Blending Control**: Adjustable opacity for realistic color preview
- **Lighting Preservation**: Maintains original lighting and shadows

### 4. Post-Processing
- **Morphological Operations**: Cleans up detection artifacts
- **Contour Analysis**: Finds the largest wall surface
- **Smart Blending**: Natural color integration with existing wall texture

## 🔧 Advanced Configuration

### Buildozer Customization

Edit `buildozer.spec` to customize:

```ini
[app]
title = Your App Name
package.name = yourappname
package.domain = com.yourcompany

# Android permissions
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# App icon and other resources
# icon.filename = %(source.dir)s/data/icon.png
```

### Wall Detection Tuning

Modify `wall_detector.py` parameters:

```python
# Adjust detection sensitivity
edges = cv2.Canny(blurred, 50, 150)  # Lower values = more sensitive

# Color range for wall detection
wall_ranges = [
    ([0, 0, 150], [180, 30, 255]),    # Light colors
    ([10, 20, 100], [25, 100, 200]),  # Beige/tan
]
```

## 🐛 Troubleshooting

### Common Build Issues

1. **Java Not Found**
   ```bash
   # Install Java 8
   sudo apt install openjdk-8-jdk  # Ubuntu/Debian
   brew install java               # macOS
   ```

2. **Android SDK Issues**
   ```bash
   # Set environment variables
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
   ```

3. **Buildozer Fails**
   ```bash
   # Clean and retry
   python setup_and_build.py clean
   buildozer android debug
   ```

4. **OpenCV Issues**
   ```bash
   # Install system dependencies (Ubuntu/Debian)
   sudo apt install python3-opencv libopencv-dev
   
   # Or use headless version
   pip install opencv-python-headless
   ```

### Runtime Issues

1. **Camera Not Working**
   - Ensure camera permissions are granted
   - Test on physical device (emulator camera may not work)

2. **Gallery Access Denied**
   - Check storage permissions in app settings
   - Try selecting images from different folders

3. **Wall Detection Poor**
   - Ensure good lighting conditions
   - Try different detection methods in the advanced module
   - Capture walls with good contrast to surroundings

## 📄 App Permissions

The app requires these Android permissions:

- **CAMERA**: For capturing photos
- **READ_EXTERNAL_STORAGE**: For accessing gallery images
- **WRITE_EXTERNAL_STORAGE**: For saving processed images
- **INTERNET**: For potential future features (analytics, updates)

## 🔐 Release Building

For production release:

1. **Create Keystore**
   ```bash
   keytool -genkey -v -keystore my-release-key.keystore -alias wallcolorizer -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Update buildozer.spec**
   ```ini
   [app:android]
   android.release_artifact = aab  # For Google Play
   # android.release_artifact = apk  # For direct distribution
   ```

3. **Build Release**
   ```bash
   python setup_and_build.py release
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Performance Tips

- **Image Size**: Resize large images for faster processing
- **Detection Speed**: Use 'color' method for faster detection
- **Memory Usage**: Clear processed images when switching photos
- **Battery**: Close camera when not in use

## 🔮 Future Enhancements

- [ ] Multiple wall detection in single image
- [ ] Color matching with real paint brands
- [ ] Texture overlay (brick, wood grain, etc.)
- [ ] AR real-time preview
- [ ] Cloud storage integration
- [ ] Social sharing features

## 📞 Support

- **Issues**: Report bugs via GitHub Issues  
- **Documentation**: Check Wiki for detailed guides
- **Community**: Join our Discord server for help


## 🙏 Acknowledgments

- OpenCV community for computer vision algorithms
- Kivy team for the excellent mobile framework
- Contributors and testers who helped improve the app

---

**Happy Wall Painting! 🎨**
