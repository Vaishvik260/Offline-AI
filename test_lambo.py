#!/usr/bin/env python3
"""
Test script for Lambo System AI
Checks dependencies and basic functionality
"""

import sys
import subprocess

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} (need 3.7+)")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")
    
    required = {
        'sounddevice': 'Audio input/output',
        'vosk': 'Voice recognition',
        'pynput': 'Global hotkeys',
        'pyautogui': 'GUI automation',
        'pyperclip': 'Clipboard access',
        'rumps': 'Menu bar app'
    }
    
    all_ok = True
    for package, description in required.items():
        try:
            __import__(package)
            print(f"   ✅ {package:15} - {description}")
        except ImportError:
            print(f"   ❌ {package:15} - {description} (missing)")
            all_ok = False
    
    return all_ok

def test_voice_model():
    """Test voice model"""
    print("\n🎤 Testing voice model...")
    import os
    if os.path.exists("vosk-model"):
        print("   ✅ Voice model found")
        return True
    else:
        print("   ❌ Voice model not found")
        print("      Download: https://alphacephei.com/vosk/models/")
        return False

def test_platform():
    """Test platform"""
    print("\n💻 Testing platform...")
    import platform
    if platform.system() == "Darwin":
        print(f"   ✅ macOS {platform.mac_ver()[0]}")
        return True
    else:
        print(f"   ⚠️  {platform.system()} (designed for macOS)")
        return False

def test_permissions():
    """Test permissions"""
    print("\n🔐 Testing permissions...")
    print("   ℹ️  Permissions will be requested when you run the app:")
    print("      • Microphone access (for voice)")
    print("      • Accessibility access (for text assistance)")
    return True

def main():
    """Run all tests"""
    print("🤖 Lambo System AI - Dependency Check")
    print("=" * 50)
    
    results = []
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Voice Model", test_voice_model()))
    results.append(("Platform", test_platform()))
    results.append(("Permissions", test_permissions()))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status:10} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Ready to run Lambo AI.")
        print("\nTo start:")
        print("   python3 lambo_system_ai.py")
    else:
        print("⚠️  Some tests failed. Please fix issues above.")
        print("\nTo install dependencies:")
        print("   pip3 install -r requirements.txt")
        print("\nTo download voice model:")
        print("   bash quick_install.sh")
    print("=" * 50)

if __name__ == "__main__":
    main()
