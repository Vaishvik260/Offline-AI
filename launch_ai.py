#!/usr/bin/env python3
"""
AI Assistant Launcher
Quick start for your offline AI assistant
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_setup():
    """Check if AI assistant is properly set up"""
    required_files = [
        "offline_ai_assistant.py",
        "system_ai_service.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing files:", ", ".join(missing_files))
        print("Run setup_ai_assistant.py first!")
        return False
    
    if not os.path.exists("vosk-model"):
        print("❌ Voice model not found!")
        print("Run setup_ai_assistant.py to download it!")
        return False
    
    return True

def show_menu():
    """Show launcher menu"""
    print("🤖 AI Assistant Launcher")
    print("=" * 30)
    print("1. Start Interactive AI Assistant")
    print("2. Start System Service (Background)")
    print("3. Run Setup")
    print("4. Test Voice Recognition")
    print("5. Exit")
    print()

def start_interactive():
    """Start the interactive AI assistant"""
    print("🚀 Starting Interactive AI Assistant...")
    try:
        subprocess.run([sys.executable, "offline_ai_assistant.py"])
    except KeyboardInterrupt:
        print("\n👋 AI Assistant stopped")

def start_service():
    """Start the system service"""
    print("🔧 Starting System Service...")
    print("Press Ctrl+C to stop")
    try:
        subprocess.run([sys.executable, "system_ai_service.py"])
    except KeyboardInterrupt:
        print("\n🛑 Service stopped")

def run_setup():
    """Run the setup script"""
    print("⚙️ Running Setup...")
    try:
        subprocess.run([sys.executable, "setup_ai_assistant.py"])
    except Exception as e:
        print(f"Setup error: {e}")

def test_voice():
    """Test voice recognition"""
    print("🎤 Testing Voice Recognition...")
    
    try:
        import sounddevice as sd
        import vosk
        import json
        import queue
        
        if not os.path.exists("vosk-model"):
            print("❌ Voice model not found! Run setup first.")
            return
        
        model = vosk.Model("vosk-model")
        recognizer = vosk.KaldiRecognizer(model, 16000)
        audio_queue = queue.Queue()
        
        def callback(indata, frames, time, status):
            audio_queue.put(bytes(indata))
        
        print("🎧 Say something (press Ctrl+C to stop)...")
        
        with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None,
                             dtype='int16', channels=1, callback=callback):
            while True:
                try:
                    data = audio_queue.get(timeout=1)
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            print(f"✅ Recognized: {text}")
                except queue.Empty:
                    continue
                except KeyboardInterrupt:
                    print("\n🛑 Voice test stopped")
                    break
                    
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        print("Run setup first!")
    except Exception as e:
        print(f"❌ Voice test error: {e}")

def main():
    """Main launcher function"""
    while True:
        show_menu()
        
        try:
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == "1":
                if check_setup():
                    start_interactive()
                else:
                    input("Press Enter to continue...")
                    
            elif choice == "2":
                if check_setup():
                    start_service()
                else:
                    input("Press Enter to continue...")
                    
            elif choice == "3":
                run_setup()
                input("Press Enter to continue...")
                
            elif choice == "4":
                test_voice()
                input("Press Enter to continue...")
                
            elif choice == "5":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()