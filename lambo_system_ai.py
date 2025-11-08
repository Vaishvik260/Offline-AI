#!/usr/bin/env python3
"""
Lambo System AI - Apple Intelligence Clone for macOS
System-wide AI assistant with Control+S activation and "Hey Lambo" voice control
"""

import os
import sys
import json
import queue
import threading
import time
import subprocess
import platform
from pathlib import Path
import tempfile

try:
    import sounddevice as sd
    import vosk
    import pynput
    from pynput import keyboard
    import pyautogui
    import pyperclip
    import rumps
    DEPS_OK = True
except ImportError:
    DEPS_OK = False

class LamboSystemAI(rumps.App):
    def __init__(self):
        super(LamboSystemAI, self).__init__("🤖 Lambo", quit_button=None)
        
        self.name = "Lambo"
        self.wake_word = "hey lambo"
        self.is_active = True
        self.is_listening = False
        self.conversation_mode = False
        
        # Menu items
        self.menu = [
            rumps.MenuItem("Status: Active", callback=None),
            rumps.separator,
            rumps.MenuItem("Toggle Voice (⌘⇧L)", callback=self.toggle_voice),
            rumps.MenuItem("Text Assist (⌃S)", callback=None),
            rumps.separator,
            rumps.MenuItem("Preferences...", callback=self.show_preferences),
            rumps.MenuItem("About Lambo", callback=self.show_about),
            rumps.separator,
            rumps.MenuItem("Quit Lambo", callback=self.quit_app)
        ]
        
        # Setup
        self.setup_voice_recognition()
        self.setup_global_hotkeys()
        
        # Start voice listening
        if self.is_active:
            self.start_voice_thread()
        
        self.speak("Lambo Intelligence activated")
        self.show_notification("Lambo AI", "Ready! Say 'Hey Lambo' or press Control+S")
    
    def setup_voice_recognition(self):
        """Setup offline voice recognition"""
        try:
            model_path = Path(__file__).parent / "vosk-model"
            if model_path.exists():
                self.vosk_model = vosk.Model(str(model_path))
                self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                self.audio_queue = queue.Queue()
                print("✅ Voice recognition ready")
            else:
                print("❌ Voice model not found")
                self.is_active = False
        except Exception as e:
            print(f"Voice setup error: {e}")
            self.is_active = False
    
    def setup_global_hotkeys(self):
        """Setup global hotkeys"""
        try:
            hotkeys = {
                '<ctrl>+s': self.handle_text_assist,
                '<cmd>+<shift>+l': self.toggle_voice
            }
            
            self.hotkey_listener = pynput.keyboard.GlobalHotKeys(hotkeys)
            self.hotkey_listener.start()
            print("✅ Hotkeys: Control+S (text assist), Cmd+Shift+L (toggle voice)")
        except Exception as e:
            print(f"Hotkey error: {e}")
    
    def speak(self, text):
        """Text-to-speech"""
        try:
            subprocess.Popen(['say', '-v', 'Samantha', text], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except:
            pass
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}" sound name "Glass"'
            ], check=False, capture_output=True)
        except:
            pass
    
    def toggle_voice(self, _=None):
        """Toggle voice listening"""
        self.is_active = not self.is_active
        
        if self.is_active:
            self.menu["Status: Active"].title = "Status: Active"
            self.speak("Voice activated")
            self.show_notification("Lambo", "Voice listening enabled")
            if not self.is_listening:
                self.start_voice_thread()
        else:
            self.menu["Status: Active"].title = "Status: Inactive"
            self.speak("Voice deactivated")
            self.show_notification("Lambo", "Voice listening disabled")
            self.is_listening = False
    
    def handle_text_assist(self):
        """Handle Control+S for text assistance"""
        try:
            selected_text = self.get_selected_text()
            
            if selected_text and len(selected_text) > 3:
                self.show_text_menu(selected_text)
            else:
                self.show_notification("Lambo", "Select text first, then press Control+S")
        except Exception as e:
            print(f"Text assist error: {e}")
    
    def get_selected_text(self):
        """Get currently selected text"""
        try:
            original = pyperclip.paste()
            pyautogui.hotkey('cmd', 'c')
            time.sleep(0.15)
            selected = pyperclip.paste()
            
            if selected != original:
                return selected
            return None
        except:
            return None
    
    def show_text_menu(self, text):
        """Show text assistance menu"""
        try:
            preview = text[:80] + "..." if len(text) > 80 else text
            preview = preview.replace('"', '\\"').replace("'", "\\'")
            
            script = f'''
            set choices to {{"Improve Writing", "Fix Grammar", "Make Professional", "Summarize", "Explain", "Ask Question", "Cancel"}}
            set userChoice to choose from list choices with prompt "Lambo AI - Selected text:\\n\\n{preview}" default items {{"Improve Writing"}}
            return userChoice as string
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and result.stdout.strip() != "false":
                choice = result.stdout.strip()
                if choice != "Cancel":
                    self.process_text_action(text, choice)
        except Exception as e:
            print(f"Menu error: {e}")
    
    def process_text_action(self, text, action):
        """Process text with AI"""
        try:
            self.show_notification("Lambo", f"Processing: {action}...")
            
            # Simulate AI processing (replace with actual AI API)
            result = self.ai_process(text, action)
            
            if result:
                self.replace_text(result)
                self.speak("Done")
                self.show_notification("Lambo", "Text updated!")
            else:
                self.show_notification("Lambo", "Processing failed")
        except Exception as e:
            print(f"Processing error: {e}")
    
    def ai_process(self, text, action):
        """AI processing (placeholder - integrate with your AI)"""
        # This is where you'd integrate with OpenAI, Groq, or local AI
        # For now, return a simple transformation
        
        if "Improve" in action:
            return f"[Improved] {text}"
        elif "Fix Grammar" in action:
            return f"[Grammar Fixed] {text}"
        elif "Professional" in action:
            return f"[Professional Version] {text}"
        elif "Summarize" in action:
            return f"[Summary] {text[:100]}..."
        elif "Explain" in action:
            return f"[Explanation] This text discusses: {text[:50]}..."
        else:
            return text
    
    def replace_text(self, new_text):
        """Replace selected text"""
        try:
            pyperclip.copy(new_text)
            pyautogui.hotkey('cmd', 'v')
        except:
            pass
    
    def start_voice_thread(self):
        """Start voice recognition thread"""
        if self.is_listening:
            return
        
        self.is_listening = True
        threading.Thread(target=self.voice_loop, daemon=True).start()
    
    def voice_loop(self):
        """Voice recognition loop"""
        try:
            def audio_callback(indata, frames, time, status):
                if self.is_listening and self.is_active:
                    self.audio_queue.put(bytes(indata))
            
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=audio_callback
            ):
                print(f"🎧 Listening for '{self.wake_word}'...")
                
                while self.is_listening and self.is_active:
                    try:
                        data = self.audio_queue.get(timeout=1)
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            text = result.get("text", "").strip().lower()
                            
                            if text and self.wake_word in text:
                                self.handle_voice_command()
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"Recognition error: {e}")
        except Exception as e:
            print(f"Voice loop error: {e}")
            self.is_listening = False
    
    def handle_voice_command(self):
        """Handle voice activation"""
        try:
            self.speak("Yes?")
            self.show_notification("Lambo", "Listening...")
            
            command = self.listen_for_command(timeout=5)
            
            if command:
                print(f"Command: {command}")
                response = self.process_voice_command(command)
                
                if response:
                    self.speak(response)
                    self.show_notification("Lambo", response[:100])
        except Exception as e:
            print(f"Voice command error: {e}")
    
    def listen_for_command(self, timeout=5):
        """Listen for voice command"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                data = self.audio_queue.get(timeout=0.5)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    command = result.get("text", "").strip()
                    
                    if command and len(command) > 3:
                        return command
            except queue.Empty:
                continue
        
        return None
    
    def process_voice_command(self, command):
        """Process voice commands"""
        cmd_lower = command.lower()
        
        # Text editing commands
        if any(word in cmd_lower for word in ["improve", "fix", "rewrite"]):
            selected = self.get_selected_text()
            if selected:
                return "Processing your text"
            return "Please select some text first"
        
        # System commands
        if "open" in cmd_lower:
            if "browser" in cmd_lower or "safari" in cmd_lower:
                subprocess.Popen(['open', '-a', 'Safari'])
                return "Opening Safari"
            elif "terminal" in cmd_lower:
                subprocess.Popen(['open', '-a', 'Terminal'])
                return "Opening Terminal"
        
        # Time/date
        if "time" in cmd_lower:
            return f"It's {time.strftime('%I:%M %p')}"
        
        if "date" in cmd_lower:
            return f"Today is {time.strftime('%A, %B %d, %Y')}"
        
        # Default response
        return f"I heard: {command}. How can I help with that?"
    
    def show_preferences(self, _):
        """Show preferences"""
        self.show_notification("Lambo Preferences", "Preferences coming soon!")
    
    def show_about(self, _):
        """Show about dialog"""
        script = '''
        display dialog "Lambo System AI\\n\\nVersion 1.0\\n\\nApple Intelligence-style AI assistant\\n\\n• Say 'Hey Lambo' for voice commands\\n• Press Control+S for text assistance\\n• Press Cmd+Shift+L to toggle voice\\n\\nWorks in every application!" buttons {"OK"} default button "OK" with icon note
        '''
        subprocess.run(['osascript', '-e', script], check=False)
    
    def quit_app(self, _):
        """Quit application"""
        self.speak("Goodbye")
        rumps.quit_application()

def check_dependencies():
    """Check and install dependencies"""
    required = [
        'sounddevice', 'vosk', 'pynput', 
        'pyautogui', 'pyperclip', 'rumps'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing dependencies: {', '.join(missing)}")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--user'
        ] + missing)
        print("✅ Dependencies installed! Please restart the app.")
        sys.exit(0)

def main():
    if not DEPS_OK:
        check_dependencies()
        return
    
    if platform.system() != "Darwin":
        print("❌ This app is designed for macOS")
        sys.exit(1)
    
    app = LamboSystemAI()
    app.run()

if __name__ == "__main__":
    main()
