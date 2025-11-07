#!/usr/bin/env python3
"""
System-wide AI Assistant Service
Runs in background and responds to global hotkeys
"""

import os
import sys
import time
import threading
import subprocess
import platform
from pathlib import Path

try:
    import pynput
    from pynput import keyboard
    import sounddevice as sd
    import vosk
    import json
    import queue
except ImportError as e:
    print(f"Missing library: {e}")
    print("Install with: pip install pynput sounddevice vosk")
    sys.exit(1)

class SystemAIService:
    def __init__(self):
        self.is_active = False
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.setup_voice_recognition()
        self.setup_hotkeys()
        
    def setup_voice_recognition(self):
        """Setup offline voice recognition"""
        try:
            if os.path.exists("vosk-model"):
                self.vosk_model = vosk.Model("vosk-model")
                self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                print("✅ Voice recognition ready")
            else:
                print("❌ Vosk model not found")
                self.vosk_model = None
        except Exception as e:
            print(f"Voice setup error: {e}")
            self.vosk_model = None
    
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            # Cmd+Shift+A on Mac, Ctrl+Shift+A on others
            if platform.system() == "Darwin":
                hotkey = '<cmd>+<shift>+a'
            else:
                hotkey = '<ctrl>+<shift>+a'
            
            self.hotkey_listener = pynput.keyboard.GlobalHotKeys({
                hotkey: self.toggle_assistant
            })
            self.hotkey_listener.start()
            print(f"✅ Global hotkey active: {hotkey}")
        except Exception as e:
            print(f"Hotkey setup error: {e}")
    
    def speak(self, text):
        """System text-to-speech"""
        try:
            if platform.system() == "Darwin":
                subprocess.run(['say', text])
            elif platform.system() == "Windows":
                subprocess.run(['powershell', '-Command', 
                              f'Add-Type -AssemblyName System.Speech; '
                              f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'])
            elif platform.system() == "Linux":
                subprocess.run(['espeak', text])
        except Exception as e:
            print(f"Speech error: {e}")
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            if platform.system() == "Darwin":
                subprocess.run([
                    'osascript', '-e',
                    f'display notification "{message}" with title "{title}"'
                ])
            elif platform.system() == "Windows":
                subprocess.run([
                    'powershell', '-Command',
                    f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; '
                    f'$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); '
                    f'$template.SelectSingleNode("//text[@id=\'1\']").AppendChild($template.CreateTextNode("{title}")) > $null; '
                    f'$template.SelectSingleNode("//text[@id=\'2\']").AppendChild($template.CreateTextNode("{message}")) > $null; '
                    f'$toast = [Windows.UI.Notifications.ToastNotification]::new($template); '
                    f'[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("AI Assistant").Show($toast)'
                ])
            elif platform.system() == "Linux":
                subprocess.run(['notify-send', title, message])
        except Exception as e:
            print(f"Notification error: {e}")
    
    def toggle_assistant(self):
        """Toggle AI assistant on/off"""
        if not self.is_active:
            self.activate_assistant()
        else:
            self.deactivate_assistant()
    
    def activate_assistant(self):
        """Activate the AI assistant"""
        self.is_active = True
        self.show_notification("AI Assistant", "Activated - Listening...")
        self.speak("AI Assistant activated")
        
        if self.vosk_model:
            self.start_listening()
        else:
            self.show_notification("AI Assistant", "Voice recognition not available")
    
    def deactivate_assistant(self):
        """Deactivate the AI assistant"""
        self.is_active = False
        self.is_listening = False
        self.show_notification("AI Assistant", "Deactivated")
        self.speak("AI Assistant deactivated")
    
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback"""
        if self.is_listening:
            self.audio_queue.put(bytes(indata))
    
    def start_listening(self):
        """Start voice recognition"""
        self.is_listening = True
        
        def listen_thread():
            try:
                with sd.RawInputStream(
                    samplerate=16000,
                    blocksize=8000,
                    device=None,
                    dtype='int16',
                    channels=1,
                    callback=self.audio_callback
                ):
                    while self.is_listening and self.is_active:
                        try:
                            data = self.audio_queue.get(timeout=1)
                            if self.recognizer.AcceptWaveform(data):
                                result = json.loads(self.recognizer.Result())
                                text = result.get("text", "").strip()
                                
                                if text:
                                    self.process_voice_command(text)
                                    
                        except queue.Empty:
                            continue
                        except Exception as e:
                            print(f"Recognition error: {e}")
                            
            except Exception as e:
                print(f"Audio error: {e}")
        
        threading.Thread(target=listen_thread, daemon=True).start()
    
    def process_voice_command(self, command):
        """Process voice commands"""
        print(f"Voice command: {command}")
        
        # Simple command processing
        if "stop" in command.lower() or "deactivate" in command.lower():
            self.deactivate_assistant()
            return
        
        # Time/date commands
        if "time" in command.lower():
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"It's {current_time}")
            return
        
        if "date" in command.lower():
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
            return
        
        # Application commands
        if "open" in command.lower():
            if "browser" in command.lower():
                self.open_application("browser")
            elif "terminal" in command.lower():
                self.open_application("terminal")
            elif "finder" in command.lower() or "files" in command.lower():
                self.open_application("files")
            else:
                self.speak("What would you like me to open?")
            return
        
        # Search commands
        if "search" in command.lower():
            search_term = command.lower().replace("search", "").replace("for", "").strip()
            if search_term:
                self.web_search(search_term)
            else:
                self.speak("What would you like me to search for?")
            return
        
        # Default response
        self.speak("I heard you say: " + command)
        self.show_notification("AI Assistant", f"Command: {command}")
    
    def open_application(self, app_type):
        """Open system applications"""
        try:
            if app_type == "browser":
                if platform.system() == "Darwin":
                    subprocess.run(["open", "-a", "Safari"])
                elif platform.system() == "Windows":
                    subprocess.run(["start", "msedge"], shell=True)
                self.speak("Opening browser")
                
            elif app_type == "terminal":
                if platform.system() == "Darwin":
                    subprocess.run(["open", "-a", "Terminal"])
                elif platform.system() == "Windows":
                    subprocess.run(["start", "cmd"], shell=True)
                self.speak("Opening terminal")
                
            elif app_type == "files":
                if platform.system() == "Darwin":
                    subprocess.run(["open", "."])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", "."])
                self.speak("Opening file manager")
                
        except Exception as e:
            self.speak(f"Sorry, I couldn't open that application")
            print(f"App open error: {e}")
    
    def web_search(self, query):
        """Perform web search"""
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            
            if platform.system() == "Darwin":
                subprocess.run(["open", f"https://www.google.com/search?q={encoded_query}"])
            elif platform.system() == "Windows":
                subprocess.run(["start", f"https://www.google.com/search?q={encoded_query}"], shell=True)
            
            self.speak(f"Searching for {query}")
        except Exception as e:
            self.speak("Sorry, I couldn't perform that search")
            print(f"Search error: {e}")
    
    def run_service(self):
        """Run the background service"""
        print("🤖 AI Assistant Service Starting...")
        print("Press Cmd+Shift+A (Mac) or Ctrl+Shift+A to activate")
        print("Press Ctrl+C to stop service")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Service stopping...")
            self.hotkey_listener.stop()

def main():
    """Main service entry point"""
    service = SystemAIService()
    service.run_service()

if __name__ == "__main__":
    main()