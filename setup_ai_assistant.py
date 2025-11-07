#!/usr/bin/env python3
"""
AI Assistant Setup Script
Installs and configures your offline AI assistant
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    
    packages = [
        "sounddevice",
        "vosk", 
        "transformers",
        "torch",
        "numpy",
        "pynput"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ All packages installed!")
    return True

def download_vosk_model():
    """Download Vosk speech recognition model"""
    print("🎤 Setting up voice recognition...")
    
    if os.path.exists("vosk-model"):
        print("✅ Vosk model already exists!")
        return True
    
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_file = "vosk-model-small-en-us-0.15.zip"
    
    try:
        print("Downloading voice recognition model (this may take a few minutes)...")
        urllib.request.urlretrieve(model_url, model_file)
        
        print("Extracting model...")
        with zipfile.ZipFile(model_file, 'r') as zip_ref:
            zip_ref.extractall()
        
        # Rename to expected directory name
        if os.path.exists("vosk-model-small-en-us-0.15"):
            os.rename("vosk-model-small-en-us-0.15", "vosk-model")
        
        # Clean up zip file
        os.remove(model_file)
        
        print("✅ Voice recognition model ready!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download voice model: {e}")
        print("You can manually download from: https://alphacephei.com/vosk/models/")
        return False

def setup_system_integration():
    """Setup system-wide integration"""
    print("🔧 Setting up system integration...")
    
    current_dir = Path.cwd()
    
    if platform.system() == "Darwin":  # macOS
        # Create LaunchAgent for macOS
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.ai-assistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{current_dir}/system_ai_service.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
</dict>
</plist>"""
        
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        launch_agents_dir.mkdir(exist_ok=True)
        
        plist_file = launch_agents_dir / "com.user.ai-assistant.plist"
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        print("✅ macOS LaunchAgent created!")
        print(f"Service file: {plist_file}")
        
    elif platform.system() == "Windows":
        # Create Windows batch file for startup
        batch_content = f"""@echo off
cd /d "{current_dir}"
"{sys.executable}" system_ai_service.py
"""
        
        startup_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        batch_file = startup_dir / "AI_Assistant.bat"
        
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        print("✅ Windows startup script created!")
        print(f"Startup file: {batch_file}")
    
    elif platform.system() == "Linux":
        # Create systemd user service
        service_content = f"""[Unit]
Description=AI Assistant Service
After=graphical-session.target

[Service]
Type=simple
ExecStart={sys.executable} {current_dir}/system_ai_service.py
WorkingDirectory={current_dir}
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"""
        
        systemd_dir = Path.home() / ".config" / "systemd" / "user"
        systemd_dir.mkdir(parents=True, exist_ok=True)
        
        service_file = systemd_dir / "ai-assistant.service"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print("✅ Linux systemd service created!")
        print(f"Service file: {service_file}")
        print("Run 'systemctl --user enable ai-assistant.service' to enable")

def create_desktop_shortcut():
    """Create desktop shortcut"""
    print("🖥️ Creating desktop shortcut...")
    
    current_dir = Path.cwd()
    
    if platform.system() == "Darwin":
        # Create macOS app bundle
        app_dir = Path.home() / "Desktop" / "AI Assistant.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        
        app_dir.mkdir(exist_ok=True)
        contents_dir.mkdir(exist_ok=True)
        macos_dir.mkdir(exist_ok=True)
        
        # Create Info.plist
        info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ai_assistant</string>
    <key>CFBundleIdentifier</key>
    <string>com.user.ai-assistant</string>
    <key>CFBundleName</key>
    <string>AI Assistant</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>"""
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(info_plist)
        
        # Create executable script
        executable_script = f"""#!/bin/bash
cd "{current_dir}"
"{sys.executable}" offline_ai_assistant.py
"""
        
        executable_file = macos_dir / "ai_assistant"
        with open(executable_file, 'w') as f:
            f.write(executable_script)
        
        os.chmod(executable_file, 0o755)
        
        print("✅ macOS app created on Desktop!")
    
    elif platform.system() == "Windows":
        # Create Windows shortcut
        desktop = Path.home() / "Desktop"
        shortcut_content = f"""[InternetShortcut]
URL=file:///{current_dir}/offline_ai_assistant.py
IconFile={sys.executable}
"""
        
        with open(desktop / "AI Assistant.url", 'w') as f:
            f.write(shortcut_content)
        
        print("✅ Windows shortcut created on Desktop!")

def main():
    """Main setup function"""
    print("🚀 AI Assistant Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    print("✅ Python version OK")
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed - couldn't install requirements")
        sys.exit(1)
    
    # Download voice model
    download_vosk_model()
    
    # Setup system integration
    setup_system_integration()
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("Your AI Assistant is ready!")
    print("\nTo start:")
    print("1. Run: python offline_ai_assistant.py")
    print("2. Or use the desktop shortcut")
    print("3. System service runs automatically")
    print(f"\nGlobal hotkey: {'Cmd+Shift+A' if platform.system() == 'Darwin' else 'Ctrl+Shift+A'}")
    print("\nEnjoy your personal offline AI! 🤖")

if __name__ == "__main__":
    main()