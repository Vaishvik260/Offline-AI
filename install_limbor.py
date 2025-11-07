#!/usr/bin/env python3
"""
Limbor AI System Installer
Installs Limbor as a system-wide AI assistant
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def install_requirements():
    """Install all required packages"""
    print("📦 Installing Limbor dependencies...")
    
    packages = [
        "sounddevice",
        "vosk", 
        "requests",
        "beautifulsoup4",
        "pynput",
        "psutil"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ All dependencies installed!")
    return True

def download_voice_model():
    """Download voice recognition model"""
    print("🎤 Setting up voice recognition...")
    
    if os.path.exists("vosk-model"):
        print("✅ Voice model already exists!")
        return True
    
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_file = "vosk-model.zip"
    
    try:
        print("Downloading voice model (this may take a few minutes)...")
        urllib.request.urlretrieve(model_url, model_file)
        
        print("Extracting voice model...")
        with zipfile.ZipFile(model_file, 'r') as zip_ref:
            zip_ref.extractall()
        
        if os.path.exists("vosk-model-small-en-us-0.15"):
            os.rename("vosk-model-small-en-us-0.15", "vosk-model")
        
        os.remove(model_file)
        print("✅ Voice model ready!")
        return True
        
    except Exception as e:
        print(f"❌ Voice model download failed: {e}")
        return False

def create_system_service():
    """Create system service for Limbor"""
    print("🔧 Creating system service...")
    
    current_dir = Path.cwd()
    limbor_script = current_dir / "limbor_ai.py"
    
    if platform.system() == "Darwin":  # macOS
        # Create LaunchAgent
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.limbor.ai-assistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{limbor_script}</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    <key>StandardOutPath</key>
    <string>/tmp/limbor.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/limbor.error.log</string>
</dict>
</plist>"""
        
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        launch_agents_dir.mkdir(exist_ok=True)
        
        plist_file = launch_agents_dir / "com.limbor.ai-assistant.plist"
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        print("✅ macOS LaunchAgent created!")
        
        # Create command line tool
        bin_dir = Path.home() / "bin"
        bin_dir.mkdir(exist_ok=True)
        
        limbor_command = f"""#!/bin/bash
cd "{current_dir}"
"{sys.executable}" limbor_ai.py "$@"
"""
        
        command_file = bin_dir / "limbor"
        with open(command_file, 'w') as f:
            f.write(limbor_command)
        
        os.chmod(command_file, 0o755)
        print(f"✅ Command line tool created: ~/bin/limbor")
        
    elif platform.system() == "Windows":
        # Create Windows service script
        service_script = f"""@echo off
cd /d "{current_dir}"
"{sys.executable}" limbor_ai.py %*
"""
        
        # Create in a standard location
        program_files = Path.home() / "AppData" / "Local" / "Limbor"
        program_files.mkdir(exist_ok=True)
        
        batch_file = program_files / "limbor.bat"
        with open(batch_file, 'w') as f:
            f.write(service_script)
        
        print(f"✅ Windows script created: {batch_file}")
        
        # Add to startup (optional)
        startup_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_script = f"""@echo off
start /min "{sys.executable}" "{current_dir}\\limbor_ai.py"
"""
        
        startup_file = startup_dir / "Limbor_AI.bat"
        with open(startup_file, 'w') as f:
            f.write(startup_script)
        
        print("✅ Added to Windows startup!")

def create_desktop_integration():
    """Create desktop shortcuts and integration"""
    print("🖥️ Creating desktop integration...")
    
    current_dir = Path.cwd()
    
    if platform.system() == "Darwin":
        # Create macOS app
        app_dir = Path.home() / "Applications" / "Limbor AI.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        for directory in [app_dir, contents_dir, macos_dir, resources_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Info.plist
        info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>limbor</string>
    <key>CFBundleIdentifier</key>
    <string>com.limbor.ai</string>
    <key>CFBundleName</key>
    <string>Limbor AI</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>limbor.icns</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>"""
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(info_plist)
        
        # Executable
        executable_script = f"""#!/bin/bash
cd "{current_dir}"
"{sys.executable}" limbor_ai.py
"""
        
        executable_file = macos_dir / "limbor"
        with open(executable_file, 'w') as f:
            f.write(executable_script)
        
        os.chmod(executable_file, 0o755)
        
        print("✅ macOS app created in Applications!")
        
    elif platform.system() == "Windows":
        # Create Windows shortcut
        desktop = Path.home() / "Desktop"
        
        shortcut_script = f"""@echo off
cd /d "{current_dir}"
"{sys.executable}" limbor_ai.py
pause
"""
        
        shortcut_file = desktop / "Limbor AI.bat"
        with open(shortcut_file, 'w') as f:
            f.write(shortcut_script)
        
        print("✅ Desktop shortcut created!")

def setup_permissions():
    """Setup required permissions"""
    print("🔐 Setting up permissions...")
    
    if platform.system() == "Darwin":
        print("""
⚠️  IMPORTANT: Grant these permissions for Limbor to work properly:

1. System Preferences → Security & Privacy → Privacy
2. Enable these for Python/Terminal:
   • Microphone (for voice recognition)
   • Accessibility (for global hotkeys)
   • Full Disk Access (for file operations)

3. You may need to restart after granting permissions.
""")
    
    elif platform.system() == "Windows":
        print("""
⚠️  IMPORTANT: You may need to:

1. Allow microphone access in Windows Settings
2. Run as Administrator for some features
3. Allow through Windows Firewall if prompted
""")

def create_config_file():
    """Create initial configuration"""
    print("⚙️ Creating configuration...")
    
    config = {
        "user_name": "User",
        "wake_word": "hey limbor",
        "voice_enabled": True,
        "auto_search": True,
        "preferred_browser": "default",
        "search_engine": "google",
        "hotkey": "cmd+shift+l" if platform.system() == "Darwin" else "ctrl+shift+l"
    }
    
    config_file = Path.home() / ".limbor_config.json"
    
    import json
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to {config_file}")

def main():
    """Main installer"""
    print("🤖 Limbor AI System Installer")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    print("✅ Python version OK")
    
    # Install requirements
    if not install_requirements():
        print("❌ Installation failed")
        sys.exit(1)
    
    # Download voice model
    if not download_voice_model():
        print("⚠️  Voice recognition may not work without the model")
    
    # Create system integration
    create_system_service()
    create_desktop_integration()
    create_config_file()
    setup_permissions()
    
    print("\n🎉 Limbor AI Installation Complete!")
    print("=" * 40)
    
    print(f"""
🚀 Limbor is now installed and ready!

Quick Start:
• Say "Hey Limbor" and ask questions
• Press {('Cmd+Shift+L' if platform.system() == 'Darwin' else 'Ctrl+Shift+L')} anywhere to activate
• Run 'limbor' in terminal (macOS) or use desktop shortcut

Features:
✅ Web search and intelligent answers
✅ Voice recognition and speech
✅ System control and automation  
✅ Global hotkey activation
✅ Natural conversation

Try saying:
• "Hey Limbor, what's the weather like?"
• "Hey Limbor, open my browser"
• "Hey Limbor, search for Python tutorials"

Enjoy your new AI assistant! 🤖
""")

if __name__ == "__main__":
    main()