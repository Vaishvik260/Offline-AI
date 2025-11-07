#!/usr/bin/env python3
"""
Quick Start Limbor AI
Simple launcher for your AI assistant
"""

import os
import sys
import subprocess
from pathlib import Path

def check_installation():
    """Check if Limbor is properly installed"""
    required_files = ["limbor_ai.py"]
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print("❌ Missing files:", ", ".join(missing))
        print("Run: python3 install_limbor.py")
        return False
    
    return True

def main():
    """Quick launcher"""
    print("🤖 Limbor AI Quick Start")
    print("=" * 30)
    
    if not check_installation():
        choice = input("\nWould you like to install Limbor now? (y/n): ")
        if choice.lower() == 'y':
            subprocess.run([sys.executable, "install_limbor.py"])
        return
    
    print("Starting Limbor AI...")
    print("\nTips:")
    print("• Say 'Hey Limbor' to activate voice mode")
    print("• Ask questions like 'What's the weather?'")
    print("• Try 'Open browser' or 'Search for Python'")
    print("• Press Ctrl+C to exit")
    print()
    
    try:
        subprocess.run([sys.executable, "limbor_ai.py"])
    except KeyboardInterrupt:
        print("\n👋 Limbor stopped!")
    except Exception as e:
        print(f"Error starting Limbor: {e}")

if __name__ == "__main__":
    main()