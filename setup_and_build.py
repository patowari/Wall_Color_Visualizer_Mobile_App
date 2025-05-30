#!/usr/bin/env python3
"""
Setup and build script for Wall Color Visualizer app
Handles environment setup, dependency installation, and APK building
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class AppBuilder:
    def __init__(self):
        self.project_root = Path.cwd()
        self.is_windows = platform.system() == "Windows"
        
    def check_requirements(self):
        """Check if all required tools are installed"""
        print("🔍 Checking requirements...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ is required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Check Java
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Java is installed")
            else:
                print("❌ Java is not installed or not in PATH")
                return False
        except FileNotFoundError:
            print("❌ Java is not installed")
            return False
        
        # Check Android SDK
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if not android_home or not os.path.exists(android_home):
            print("⚠️  ANDROID_HOME not set. Buildozer will download Android SDK")
        else:
            print(f"✅ Android SDK found at {android_home}")
        
        return True
    
    def setup_virtual_environment(self):
        """Setup Python virtual environment"""
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        print("🔧 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        
        # Determine pip executable
        if self.is_windows:
            pip_exe = self.project_root / "venv" / "Scripts" / "pip.exe"
        else:
            pip_exe = self.project_root / "venv" / "bin" / "pip"
        
        if not pip_exe.exists():
            print("❌ Virtual environment not properly set up")
            return False
        
        # Upgrade pip first
        try:
            subprocess.run([str(pip_exe), 'install', '--upgrade', 'pip'], check=True)
            print("✅ Pip upgraded")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Pip upgrade failed: {e}")
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.run([str(pip_exe), 'install', '-r', str(requirements_file)], check=True)
                print("✅ Requirements installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install requirements: {e}")
                return False
        
        # Install buildozer
        try:
            subprocess.run([str(pip_exe), 'install', 'buildozer', 'cython'], check=True)
            print("✅ Buildozer and Cython installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install buildozer: {e}")
            return False
    
    def setup_buildozer(self):
        """Initialize buildozer configuration"""
        buildozer_spec = self.project_root / "buildozer.spec"
        
        if buildozer_spec.exists():
            print("✅ buildozer.spec already exists")
            return True
        
        print("🔧 Initializing buildozer...")
        try:
            # Use pip from virtual environment
            if self.is_windows:
                buildozer_exe = self.project_root / "venv" / "Scripts" / "buildozer.exe"
            else:
                buildozer_exe = self.project_root / "venv" / "bin" / "buildozer"
            
            if buildozer_exe.exists():
                subprocess.run([str(buildozer_exe), 'init'], check=True, cwd=self.project_root)
            else:
                subprocess.run(['buildozer', 'init'], check=True, cwd=self.project_root)
            
            print("✅ Buildozer initialized")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize buildozer: {e}")
            return False
    
    def test_app_locally(self):
        """Test the app locally before building"""
        print("🧪 Testing app locally...")
        
        # Determine python executable
        if self.is_windows:
            python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.project_root / "venv" / "bin" / "python"
        
        main_py = self.project_root / "main.py"
        if not main_py.exists():
            print("❌ main.py not found")
            return False
        
        print("ℹ️  Running app locally (press Ctrl+C to stop)...")
        try:
            subprocess.run([str(python_exe), str(main_py)], cwd=self.project_root)
            return True
        except KeyboardInterrupt:
            print("\n✅ Local test stopped by user")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Local test failed: {e}")
            return False
    
    def build_debug_apk(self):
        """Build debug APK"""
        print("🔨 Building debug APK...")
        print("⚠️  This may take a long time on first build (downloading dependencies)...")
        
        try:
            # Use buildozer from virtual environment
            if self.is_windows:
                buildozer_exe = self.project_root / "venv" / "Scripts" / "buildozer.exe"
            else:
                buildozer_exe = self.project_root / "venv" / "bin" / "buildozer"
            
            if buildozer_exe.exists():
                result = subprocess.run([str(buildozer_exe), 'android', 'debug'], 
                                      cwd=self.project_root, capture_output=False)
            else:
                result = subprocess.run(['buildozer', 'android', 'debug'], 
                                      cwd=self.project_root, capture_output=False)
            
            if result.returncode == 0:
                print("✅ Debug APK built successfully!")
                
                # Find the APK file
                bin_dir = self.project_root / "bin"
                apk_files = list(bin_dir.glob("*.apk")) if bin_dir.exists() else []
                
                if apk_files:
                    apk_path = apk_files[0]
                    print(f"📱 APK location: {apk_path}")
                    print(f"📊 APK size: {apk_path.stat().st_size / (1024*1024):.2f} MB")
                
                return True
            else:
                print("❌ APK build failed")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Build process failed: {e}")
            return False
    
    def build_release_apk(self):
        """Build release APK (requires keystore)"""
        print("🔨 Building release APK...")
        
        # Check if keystore exists
        keystore_path = self.project_root / "my-release-key.keystore"
        if not keystore_path.exists():
            print("⚠️  No keystore found. Creating a new one...")
            self.create_keystore()
        
        try:
            # Use buildozer from virtual environment
            if self.is_windows:
                buildozer_exe = self.project_root / "venv" / "Scripts" / "buildozer.exe"
            else:
                buildozer_exe = self.project_root / "venv" / "bin" / "buildozer"
            
            if buildozer_exe.exists():
                result = subprocess.run([str(buildozer_exe), 'android', 'release'], 
                                      cwd=self.project_root, capture_output=False)
            else:
                result = subprocess.run(['buildozer', 'android', 'release'], 
                                      cwd=self.project_root, capture_output=False)
            
            if result.returncode == 0:
                print("✅ Release APK built successfully!")
                return True
            else:
                print("❌ Release APK build failed")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Release build process failed: {e}")
            return False
    
    def create_keystore(self):
        """Create a keystore for release builds"""
        print("🔑 Creating keystore for release builds...")
        
        keystore_path = self.project_root / "my-release-key.keystore"
        
        # Basic keystore creation (user should customize)
        keytool_cmd = [
            'keytool', '-genkey', '-v',
            '-keystore', str(keystore_path),
            '-alias', 'wallcolorizer',
            '-keyalg', 'RSA',
            '-keysize', '2048',
            '-validity', '10000',
            '-storepass', 'password123',
            '-keypass', 'password123',
            '-dname', 'CN=WallColorizer,OU=Dev,O=Company,L=City,S=State,C=US'
        ]
        
        try:
            subprocess.run(keytool_cmd, check=True)
            print("✅ Keystore created")
            print("⚠️  Remember to change the default passwords!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create keystore: {e}")
    
    def clean_build(self):
        """Clean build artifacts"""
        print("🧹 Cleaning build artifacts...")
        
        dirs_to_clean = ['.buildozer', 'bin', '__pycache__']
        
        for dir_name in dirs_to_clean:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
                print(f"✅ Removed {dir_name}")
        
        print("✅ Build cleaned")
    
    def show_usage(self):
        """Show usage instructions"""
        print("""
🏗️  Wall Color Visualizer Build Script

Usage: python setup_and_build.py [command]

Commands:
  setup     - Setup development environment
  test      - Test app locally
  debug     - Build debug APK
  release   - Build release APK  
  clean     - Clean build artifacts
  all       - Setup + Build debug APK

Requirements:
  - Python 3.8+
  - Java 8+
  - Android SDK (optional, buildozer can download)

First time setup:
  1. python setup_and_build.py setup
  2. python setup_and_build.py test
  3. python setup_and_build.py debug
        """)

def main():
    builder = AppBuilder()
    
    if len(sys.argv) < 2:
        builder.show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        print("🚀 Setting up development environment...")
        if not builder.check_requirements():
            return
        if not builder.setup_virtual_environment():
            return
        if not builder.install_dependencies():
            return
        builder.setup_buildozer()
        print("✅ Setup complete!")
        
    elif command == 'test':
        builder.test_app_locally()
        
    elif command == 'debug':
        builder.build_debug_apk()
        
    elif command == 'release':
        builder.build_release_apk()
        
    elif command == 'clean':
        builder.clean_build()
        
    elif command == 'all':
        print("🚀 Full setup and build...")
        if not builder.check_requirements():
            return
        if not builder.setup_virtual_environment():
            return
        if not builder.install_dependencies():
            return
        if not builder.setup_buildozer():
            return
        builder.build_debug_apk()
        
    else:
        print(f"❌ Unknown command: {command}")
        builder.show_usage()

if __name__ == "__main__":
    main()
