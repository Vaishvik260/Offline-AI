#!/usr/bin/env python3
"""
Limbor AI - Your Intelligent Computer Assistant
Integrates with your system and can browse the web for real answers
"""

import os
import sys
import json
import queue
import threading
import time
import subprocess
import platform
import webbrowser
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import sounddevice as sd
    import vosk
    import requests
    from bs4 import BeautifulSoup
    import pynput
    from pynput import keyboard
except ImportError as e:
    print(f"Installing required libraries...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sounddevice", "vosk", "requests", "beautifulsoup4", "pynput"])
    import sounddevice as sd
    import vosk
    import requests
    from bs4 import BeautifulSoup
    import pynput
    from pynput import keyboard

class LimborAI:
    def __init__(self):
        self.name = "Limbor"
        self.wake_word = "hey limbor"
        self.is_listening = False
        self.is_active = False
        self.conversation_history = []
        self.user_preferences = self.load_preferences()
        
        print(f"🤖 Initializing {self.name} AI...")
        self.setup_voice_recognition()
        self.setup_system_integration()
        
    def load_preferences(self):
        """Load user preferences"""
        prefs_file = Path.home() / ".limbor_preferences.json"
        default_prefs = {
            "user_name": "User",
            "preferred_browser": "default",
            "search_engine": "google",
            "voice_enabled": True,
            "auto_search": True
        }
        
        try:
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    return {**default_prefs, **json.load(f)}
        except:
            pass
        
        return default_prefs
    
    def save_preferences(self):
        """Save user preferences"""
        prefs_file = Path.home() / ".limbor_preferences.json"
        try:
            with open(prefs_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Could not save preferences: {e}")
    
    def setup_voice_recognition(self):
        """Setup voice recognition"""
        try:
            if os.path.exists("vosk-model"):
                self.vosk_model = vosk.Model("vosk-model")
                self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                self.audio_queue = queue.Queue()
                print("✅ Voice recognition ready")
                return True
            else:
                print("❌ Voice model not found. Downloading...")
                self.download_voice_model()
                return self.setup_voice_recognition()
        except Exception as e:
            print(f"Voice setup error: {e}")
            return False
    
    def download_voice_model(self):
        """Download voice recognition model"""
        import zipfile
        
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        model_file = "vosk-model.zip"
        
        try:
            print("Downloading voice model...")
            urllib.request.urlretrieve(model_url, model_file)
            
            with zipfile.ZipFile(model_file, 'r') as zip_ref:
                zip_ref.extractall()
            
            if os.path.exists("vosk-model-small-en-us-0.15"):
                os.rename("vosk-model-small-en-us-0.15", "vosk-model")
            
            os.remove(model_file)
            print("✅ Voice model downloaded!")
            
        except Exception as e:
            print(f"Failed to download voice model: {e}")
    
    def setup_system_integration(self):
        """Setup system-wide integration"""
        try:
            # Global hotkey for activation
            if platform.system() == "Darwin":
                hotkey = '<cmd>+<shift>+l'
            else:
                hotkey = '<ctrl>+<shift>+l'
            
            self.hotkey_listener = pynput.keyboard.GlobalHotKeys({
                hotkey: self.toggle_limbor
            })
            self.hotkey_listener.start()
            print(f"✅ Global hotkey active: {hotkey}")
            
        except Exception as e:
            print(f"System integration error: {e}")
    
    def speak(self, text):
        """Text-to-speech"""
        try:
            if platform.system() == "Darwin":
                subprocess.run(['say', '-v', 'Samantha', text])
            elif platform.system() == "Windows":
                subprocess.run(['powershell', '-Command', 
                              f'Add-Type -AssemblyName System.Speech; '
                              f'$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                              f'$synth.SelectVoice("Microsoft Zira Desktop"); '
                              f'$synth.Speak("{text}")'])
            elif platform.system() == "Linux":
                subprocess.run(['espeak', '-s', '150', text])
        except Exception as e:
            print(f"Speech error: {e}")
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            if platform.system() == "Darwin":
                subprocess.run([
                    'osascript', '-e',
                    f'display notification "{message}" with title "{title}" sound name "Glass"'
                ])
            elif platform.system() == "Windows":
                subprocess.run([
                    'powershell', '-Command',
                    f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; '
                    f'$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); '
                    f'$template.SelectSingleNode("//text[@id=\'1\']").AppendChild($template.CreateTextNode("{title}")) > $null; '
                    f'$template.SelectSingleNode("//text[@id=\'2\']").AppendChild($template.CreateTextNode("{message}")) > $null; '
                    f'$toast = [Windows.UI.Notifications.ToastNotification]::new($template); '
                    f'[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Limbor AI").Show($toast)'
                ])
        except Exception as e:
            print(f"Notification error: {e}")
    
    def search_web(self, query):
        """Search the web and get intelligent answers"""
        try:
            # Encode the search query
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Make the request
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract a direct answer
            answer_box = soup.find('div', class_='BNeawe')
            if answer_box:
                return answer_box.get_text().strip()
            
            # Try to get featured snippet
            featured = soup.find('div', {'data-attrid': True})
            if featured:
                return featured.get_text().strip()
            
            # Get search results
            results = []
            for result in soup.find_all('div', class_='BVG0Nb')[:3]:
                text = result.get_text().strip()
                if text and len(text) > 20:
                    results.append(text)
            
            if results:
                return f"Here's what I found: {results[0][:200]}..."
            
            return f"I searched for '{query}' but couldn't get a clear answer. Let me open the search results for you."
            
        except Exception as e:
            print(f"Web search error: {e}")
            return f"I couldn't search the web right now, but let me open Google for '{query}'"
    
    def open_web_search(self, query):
        """Open web search in browser"""
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            webbrowser.open(search_url)
            return f"Opening Google search for '{query}'"
        except Exception as e:
            return f"Couldn't open browser: {e}"
    
    def process_command(self, command):
        """Process user commands intelligently"""
        command_lower = command.lower().strip()
        
        # Greeting
        if any(word in command_lower for word in ["hello", "hi", "hey"]):
            responses = [
                f"Hello {self.user_preferences['user_name']}! I'm Limbor, your AI assistant. How can I help you today?",
                f"Hi there! Limbor here, ready to assist you with anything you need.",
                f"Hey {self.user_preferences['user_name']}! What can I do for you?"
            ]
            return responses[hash(command) % len(responses)]
        
        # Time and date
        if any(phrase in command_lower for phrase in ["what time", "time is it", "current time"]):
            current_time = datetime.now().strftime("%I:%M %p")
            return f"It's {current_time}"
        
        if any(phrase in command_lower for phrase in ["what date", "today's date", "what day"]):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}"
        
        # Web search queries
        if any(phrase in command_lower for phrase in ["search for", "look up", "find information about", "what is", "who is", "how to", "why", "when", "where"]):
            # Extract the search query
            search_terms = command_lower
            for phrase in ["search for", "look up", "find information about", "what is", "who is", "tell me about"]:
                search_terms = search_terms.replace(phrase, "").strip()
            
            if len(search_terms) > 2:
                self.speak("Let me search that for you...")
                result = self.search_web(search_terms)
                
                # Also open browser if needed
                if "couldn't get a clear answer" in result:
                    self.open_web_search(search_terms)
                
                return result
            else:
                return "What would you like me to search for?"
        
        # Computer control
        if "open" in command_lower:
            return self.handle_open_command(command)
        
        # System information
        if any(phrase in command_lower for phrase in ["system info", "computer info", "specs"]):
            return self.get_system_info()
        
        # File operations
        if any(phrase in command_lower for phrase in ["create file", "make file", "new file"]):
            return "What type of file would you like me to create and what should I name it?"
        
        # Settings
        if "settings" in command_lower or "preferences" in command_lower:
            return self.handle_settings(command)
        
        # Default: treat as web search
        if len(command.strip()) > 3:
            self.speak("Searching the web for that...")
            result = self.search_web(command)
            self.open_web_search(command)
            return result
        
        return "I'm here to help! You can ask me questions, search the web, control your computer, or just have a conversation."
    
    def handle_open_command(self, command):
        """Handle application opening"""
        command_lower = command.lower()
        
        try:
            if any(word in command_lower for word in ["browser", "chrome", "safari", "firefox"]):
                if platform.system() == "Darwin":
                    subprocess.run(["open", "-a", "Safari"])
                elif platform.system() == "Windows":
                    subprocess.run(["start", "chrome"], shell=True)
                return "Opening your web browser"
            
            elif any(word in command_lower for word in ["terminal", "command prompt", "cmd"]):
                if platform.system() == "Darwin":
                    subprocess.run(["open", "-a", "Terminal"])
                elif platform.system() == "Windows":
                    subprocess.run(["start", "cmd"], shell=True)
                return "Opening terminal"
            
            elif any(word in command_lower for word in ["finder", "files", "explorer"]):
                if platform.system() == "Darwin":
                    subprocess.run(["open", "."])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", "."])
                return "Opening file manager"
            
            elif "calculator" in command_lower:
                if platform.system() == "Darwin":
                    subprocess.run(["open", "-a", "Calculator"])
                elif platform.system() == "Windows":
                    subprocess.run(["calc"], shell=True)
                return "Opening calculator"
            
            else:
                return "What application would you like me to open?"
                
        except Exception as e:
            return f"Sorry, I couldn't open that application: {e}"
    
    def get_system_info(self):
        """Get system information"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return f"""System Information:
• CPU Usage: {cpu_percent}%
• Memory: {memory.percent}% used ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)
• Disk: {disk.percent}% used ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)
• Platform: {platform.system()} {platform.release()}"""
            
        except ImportError:
            return f"System: {platform.system()} {platform.release()}"
        except Exception as e:
            return f"Couldn't get system info: {e}"
    
    def handle_settings(self, command):
        """Handle settings and preferences"""
        if "name" in command.lower():
            return f"Your name is set to '{self.user_preferences['user_name']}'. You can change it by saying 'set my name to [new name]'"
        
        return "Settings available: name, browser, search engine. What would you like to change?"
    
    def toggle_limbor(self):
        """Toggle Limbor activation"""
        if not self.is_active:
            self.activate_limbor()
        else:
            self.deactivate_limbor()
    
    def activate_limbor(self):
        """Activate Limbor"""
        self.is_active = True
        self.show_notification("Limbor AI", "Activated - Listening for 'Hey Limbor'")
        self.speak("Limbor activated")
        
        if hasattr(self, 'vosk_model'):
            self.start_listening()
    
    def deactivate_limbor(self):
        """Deactivate Limbor"""
        self.is_active = False
        self.is_listening = False
        self.show_notification("Limbor AI", "Deactivated")
        self.speak("Limbor deactivated")
    
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback"""
        if self.is_listening:
            self.audio_queue.put(bytes(indata))
    
    def start_listening(self):
        """Start continuous listening"""
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
                    print(f"🎧 Listening for '{self.wake_word}'...")
                    
                    while self.is_listening and self.is_active:
                        try:
                            data = self.audio_queue.get(timeout=1)
                            if self.recognizer.AcceptWaveform(data):
                                result = json.loads(self.recognizer.Result())
                                text = result.get("text", "").strip().lower()
                                
                                if text:
                                    print(f"Heard: {text}")
                                    
                                    if self.wake_word in text:
                                        self.speak("Yes?")
                                        self.show_notification("Limbor", "Listening...")
                                        
                                        # Listen for the actual command
                                        self.listen_for_command()
                                    
                                    elif "stop listening" in text or "deactivate" in text:
                                        self.deactivate_limbor()
                                        break
                                        
                        except queue.Empty:
                            continue
                        except Exception as e:
                            print(f"Recognition error: {e}")
                            
            except Exception as e:
                print(f"Audio error: {e}")
        
        threading.Thread(target=listen_thread, daemon=True).start()
    
    def listen_for_command(self):
        """Listen for user command after wake word"""
        command_timeout = 5  # seconds
        start_time = time.time()
        
        while time.time() - start_time < command_timeout:
            try:
                data = self.audio_queue.get(timeout=0.5)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    command = result.get("text", "").strip()
                    
                    if command and len(command) > 2:
                        print(f"Command: {command}")
                        response = self.process_command(command)
                        print(f"Limbor: {response}")
                        self.speak(response)
                        
                        # Add to conversation history
                        self.conversation_history.append(f"User: {command}")
                        self.conversation_history.append(f"Limbor: {response}")
                        
                        # Keep history manageable
                        if len(self.conversation_history) > 20:
                            self.conversation_history = self.conversation_history[-20:]
                        
                        return
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command recognition error: {e}")
        
        self.speak("I didn't catch that. Try saying 'Hey Limbor' again.")
    
    def text_mode(self):
        """Interactive text mode"""
        print(f"\n💬 {self.name} Text Mode")
        print("Type 'voice' to switch to voice mode, 'exit' to quit")
        
        while True:
            try:
                user_input = input(f"\n{self.user_preferences['user_name']}: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self.speak("Goodbye! It was great talking with you.")
                    break
                
                if user_input.lower() == 'voice':
                    self.activate_limbor()
                    break
                
                # Process the command
                response = self.process_command(user_input)
                print(f"{self.name}: {response}")
                
                # Add to conversation history
                self.conversation_history.append(f"User: {user_input}")
                self.conversation_history.append(f"Limbor: {response}")
                
            except KeyboardInterrupt:
                print(f"\n👋 {self.name} signing off!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run(self):
        """Main application loop"""
        print(f"🚀 {self.name} AI Assistant Starting...")
        print("=" * 50)
        
        self.speak(f"Hello! I'm {self.name}, your intelligent AI assistant. I'm ready to help!")
        
        while True:
            print(f"\n{self.name} AI Assistant")
            print("1. Voice Mode (Say 'Hey Limbor')")
            print("2. Text Mode (Type to chat)")
            print("3. Exit")
            
            choice = input("\nChoose mode (1-3): ").strip()
            
            if choice == "1":
                self.activate_limbor()
                input("\nPress Enter to stop voice mode...")
                self.deactivate_limbor()
                
            elif choice == "2":
                self.text_mode()
                
            elif choice == "3":
                self.speak("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

def main():
    """Main entry point"""
    try:
        limbor = LimborAI()
        limbor.run()
    except KeyboardInterrupt:
        print("\n👋 Limbor shutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()