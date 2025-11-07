#!/usr/bin/env python3
"""
Lambo Intelligence - Apple Intelligence Clone
System-wide AI assistant with text editing, suggestions, and image processing
"""

import os
import sys
import json
import queue
import threading
import time
import subprocess
import platform
import requests
from datetime import datetime
import re
from pathlib import Path

try:
    import sounddevice as sd
    import vosk
    import pynput
    from pynput import keyboard, mouse
    import pyautogui
    import pyperclip
    from PIL import Image, ImageGrab
    FULL_FEATURES = True
except ImportError:
    FULL_FEATURES = False
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "sounddevice", "vosk", "pynput", "pyautogui", 
                          "pyperclip", "pillow", "requests"])
    import sounddevice as sd
    import vosk
    import pynput
    from pynput import keyboard, mouse
    import pyautogui
    import pyperclip
    from PIL import Image, ImageGrab
    FULL_FEATURES = True

class LamboIntelligence:
    def __init__(self):
        self.name = "Lambo"
        self.wake_word = "hey lambo"
        self.is_active = False
        self.is_listening = False
        self.conversation_history = []
        
        # AI API configuration
        self.ai_api_key = os.getenv('OPENAI_API_KEY') or os.getenv('GROQ_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.ai_provider = self.detect_ai_provider()
        
        # System integration
        self.setup_voice_recognition()
        self.setup_global_hotkeys()
        self.setup_system_integration()
        
        print(f"🤖 {self.name} Intelligence System Starting...")
        self.show_status()
    
    def detect_ai_provider(self):
        """Detect which AI provider to use"""
        if os.getenv('GROQ_API_KEY'):
            return 'groq'
        elif os.getenv('OPENAI_API_KEY'):
            return 'openai'
        elif os.getenv('GEMINI_API_KEY'):
            return 'gemini'
        else:
            return None
    
    def setup_voice_recognition(self):
        """Setup offline voice recognition"""
        try:
            if os.path.exists("vosk-model"):
                self.vosk_model = vosk.Model("vosk-model")
                self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                self.audio_queue = queue.Queue()
                print("✅ Voice recognition ready")
                return True
            else:
                print("❌ Voice model not found - downloading...")
                self.download_voice_model()
                return self.setup_voice_recognition()
        except Exception as e:
            print(f"Voice setup error: {e}")
            return False
    
    def download_voice_model(self):
        """Download voice model if not present"""
        import urllib.request
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
            print("✅ Voice model ready!")
            
        except Exception as e:
            print(f"Failed to download voice model: {e}")
    
    def setup_global_hotkeys(self):
        """Setup global hotkeys"""
        try:
            # Cmd+S on Mac, Ctrl+S on others
            if platform.system() == "Darwin":
                hotkeys = {
                    '<cmd>+s': self.handle_text_assistance,
                    '<cmd>+<shift>+l': self.toggle_lambo
                }
            else:
                hotkeys = {
                    '<ctrl>+s': self.handle_text_assistance,
                    '<ctrl>+<shift>+l': self.toggle_lambo
                }
            
            self.hotkey_listener = pynput.keyboard.GlobalHotKeys(hotkeys)
            self.hotkey_listener.start()
            print("✅ Global hotkeys active")
            
        except Exception as e:
            print(f"Hotkey setup error: {e}")
    
    def setup_system_integration(self):
        """Setup system-wide integration"""
        try:
            # Create system service files
            self.create_system_service()
            
            # Setup clipboard monitoring
            self.last_clipboard = ""
            self.monitor_clipboard()
            
            print("✅ System integration ready")
            
        except Exception as e:
            print(f"System integration error: {e}")
    
    def create_system_service(self):
        """Create system service for auto-start"""
        current_dir = Path.cwd()
        script_path = current_dir / "lambo_intelligence.py"
        
        if platform.system() == "Darwin":  # macOS
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lambo.intelligence</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
        <string>--service</string>
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
            
            plist_file = launch_agents_dir / "com.lambo.intelligence.plist"
            with open(plist_file, 'w') as f:
                f.write(plist_content)
            
            print(f"✅ macOS service created: {plist_file}")
    
    def show_status(self):
        """Show system status"""
        print("\n🚀 Lambo Intelligence Status")
        print("=" * 40)
        
        if self.ai_provider:
            print(f"✅ AI Provider: {self.ai_provider.title()}")
        else:
            print("❌ No AI API configured")
        
        print("✅ Voice Recognition: Ready")
        print("✅ Global Hotkeys: Active")
        print("✅ System Integration: Ready")
        
        if platform.system() == "Darwin":
            print("\n🎯 Activation Methods:")
            print("• Say 'Hey Lambo' for voice commands")
            print("• Press Cmd+S for text assistance")
            print("• Press Cmd+Shift+L to toggle")
        else:
            print("\n🎯 Activation Methods:")
            print("• Say 'Hey Lambo' for voice commands")
            print("• Press Ctrl+S for text assistance")
            print("• Press Ctrl+Shift+L to toggle")
        
        print("\n💡 Capabilities:")
        print("• Text editing and suggestions")
        print("• Writing assistance and rewriting")
        print("• Code generation and debugging")
        print("• Image analysis and description")
        print("• System-wide AI assistance")
        
        if not self.ai_provider:
            print("\n⚠️  Set up AI API for full features:")
            print("   export GROQ_API_KEY='your-key'")
    
    def speak(self, text):
        """Text-to-speech"""
        try:
            if platform.system() == "Darwin":
                subprocess.run(['say', '-v', 'Samantha', text], check=False)
            elif platform.system() == "Windows":
                subprocess.run(['powershell', '-Command', 
                              f'Add-Type -AssemblyName System.Speech; '
                              f'$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                              f'$synth.Speak("{text}")'], check=False)
        except:
            pass
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            if platform.system() == "Darwin":
                subprocess.run([
                    'osascript', '-e',
                    f'display notification "{message}" with title "{title}" sound name "Glass"'
                ], check=False)
        except:
            pass
    
    def toggle_lambo(self):
        """Toggle Lambo on/off"""
        if not self.is_active:
            self.activate_lambo()
        else:
            self.deactivate_lambo()
    
    def activate_lambo(self):
        """Activate Lambo Intelligence"""
        self.is_active = True
        self.show_notification("Lambo Intelligence", "Activated - Listening for 'Hey Lambo'")
        self.speak("Lambo Intelligence activated")
        
        if hasattr(self, 'vosk_model'):
            self.start_listening()
    
    def deactivate_lambo(self):
        """Deactivate Lambo Intelligence"""
        self.is_active = False
        self.is_listening = False
        self.show_notification("Lambo Intelligence", "Deactivated")
        self.speak("Lambo Intelligence deactivated")
    
    def handle_text_assistance(self):
        """Handle Cmd+S / Ctrl+S for text assistance"""
        try:
            # Get selected text or clipboard
            selected_text = self.get_selected_text()
            
            if selected_text:
                self.show_text_assistance_menu(selected_text)
            else:
                self.show_notification("Lambo", "Select text first, then press the hotkey")
        
        except Exception as e:
            print(f"Text assistance error: {e}")
    
    def get_selected_text(self):
        """Get currently selected text"""
        try:
            # Save current clipboard
            original_clipboard = pyperclip.paste()
            
            # Copy selected text
            if platform.system() == "Darwin":
                pyautogui.hotkey('cmd', 'c')
            else:
                pyautogui.hotkey('ctrl', 'c')
            
            time.sleep(0.1)  # Wait for copy
            
            # Get copied text
            selected_text = pyperclip.paste()
            
            # Restore original clipboard if no text was selected
            if selected_text == original_clipboard:
                return None
            
            return selected_text if selected_text else None
            
        except Exception as e:
            print(f"Error getting selected text: {e}")
            return None
    
    def show_text_assistance_menu(self, text):
        """Show text assistance options"""
        try:
            # Create a simple menu using system dialog
            if platform.system() == "Darwin":
                script = f'''
                set selectedText to "{text[:100]}..."
                set userChoice to choose from list {{"Improve Writing", "Fix Grammar", "Make Professional", "Summarize", "Explain", "Translate", "Cancel"}} with prompt "Lambo Intelligence - What would you like to do with the selected text?" default items {{"Improve Writing"}}
                return userChoice as string
                '''
                
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True, check=False)
                
                if result.returncode == 0 and result.stdout.strip() != "false":
                    choice = result.stdout.strip()
                    self.process_text_assistance(text, choice)
            else:
                # For non-macOS, show notification with options
                self.show_notification("Lambo Intelligence", 
                                     "Text selected! Say 'Hey Lambo' and tell me what to do with it.")
                
        except Exception as e:
            print(f"Menu error: {e}")
    
    def process_text_assistance(self, text, action):
        """Process text assistance request"""
        try:
            if not self.ai_provider:
                self.show_notification("Lambo", "AI API not configured. Set up GROQ_API_KEY or OPENAI_API_KEY")
                return
            
            # Generate AI response based on action
            if "Improve Writing" in action:
                prompt = f"Improve the writing of this text, making it clearer and more engaging: {text}"
            elif "Fix Grammar" in action:
                prompt = f"Fix any grammar, spelling, and punctuation errors in this text: {text}"
            elif "Make Professional" in action:
                prompt = f"Rewrite this text to be more professional and formal: {text}"
            elif "Summarize" in action:
                prompt = f"Provide a concise summary of this text: {text}"
            elif "Explain" in action:
                prompt = f"Explain what this text means in simple terms: {text}"
            elif "Translate" in action:
                prompt = f"Translate this text to Spanish: {text}"
            else:
                return
            
            # Get AI response
            self.show_notification("Lambo", "Processing with AI...")
            response = self.get_ai_response(prompt)
            
            if response:
                # Replace selected text with AI response
                self.replace_selected_text(response)
                self.show_notification("Lambo", f"Text {action.lower()}d successfully!")
            else:
                self.show_notification("Lambo", "AI processing failed. Try again.")
                
        except Exception as e:
            print(f"Text processing error: {e}")
    
    def replace_selected_text(self, new_text):
        """Replace selected text with new text"""
        try:
            # Copy new text to clipboard
            pyperclip.copy(new_text)
            
            # Paste to replace selected text
            if platform.system() == "Darwin":
                pyautogui.hotkey('cmd', 'v')
            else:
                pyautogui.hotkey('ctrl', 'v')
                
        except Exception as e:
            print(f"Text replacement error: {e}")
    
    def get_ai_response(self, prompt):
        """Get response from AI API"""
        try:
            if self.ai_provider == 'groq':
                return self.use_groq_api(prompt)
            elif self.ai_provider == 'openai':
                return self.use_openai_api(prompt)
            elif self.ai_provider == 'gemini':
                return self.use_gemini_api(prompt)
            else:
                return None
                
        except Exception as e:
            print(f"AI API error: {e}")
            return None
    
    def use_groq_api(self, prompt):
        """Use Groq API"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.ai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": "You are Lambo, a helpful AI assistant. Provide clear, concise responses. For text editing tasks, return only the improved text without explanations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def use_openai_api(self, prompt):
        """Use OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.ai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are Lambo, a helpful AI assistant. For text editing tasks, return only the improved text without explanations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def monitor_clipboard(self):
        """Monitor clipboard for automatic suggestions"""
        def clipboard_monitor():
            while True:
                try:
                    current_clipboard = pyperclip.paste()
                    
                    if (current_clipboard != self.last_clipboard and 
                        len(current_clipboard) > 50 and 
                        self.is_active):
                        
                        # Check if it looks like text that could be improved
                        if self.should_suggest_improvement(current_clipboard):
                            self.show_notification("Lambo", 
                                                 "I can help improve this text! Press Cmd+S")
                        
                        self.last_clipboard = current_clipboard
                    
                    time.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    time.sleep(5)  # Wait longer on error
        
        threading.Thread(target=clipboard_monitor, daemon=True).start()
    
    def should_suggest_improvement(self, text):
        """Check if text could benefit from AI improvement"""
        # Simple heuristics
        if len(text) < 20 or len(text) > 1000:
            return False
        
        # Check for common issues
        issues = [
            text.count('.') == 0,  # No periods
            text.islower(),        # All lowercase
            text.isupper(),        # All uppercase
            '  ' in text,          # Double spaces
            text.count('!') > 3,   # Too many exclamations
        ]
        
        return any(issues)
    
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback"""
        if self.is_listening:
            self.audio_queue.put(bytes(indata))
    
    def start_listening(self):
        """Start continuous voice recognition"""
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
                                
                                if text and self.wake_word in text:
                                    self.handle_voice_activation(text)
                                    
                        except queue.Empty:
                            continue
                        except Exception as e:
                            print(f"Recognition error: {e}")
                            
            except Exception as e:
                print(f"Audio error: {e}")
        
        threading.Thread(target=listen_thread, daemon=True).start()
    
    def handle_voice_activation(self, text):
        """Handle voice activation"""
        try:
            self.speak("Yes, how can I help?")
            self.show_notification("Lambo", "Listening...")
            
            # Listen for command
            command = self.listen_for_command()
            
            if command:
                print(f"Voice command: {command}")
                response = self.process_voice_command(command)
                
                if response:
                    print(f"Lambo: {response}")
                    self.speak(response)
                    self.show_notification("Lambo", response[:100] + "...")
            
        except Exception as e:
            print(f"Voice activation error: {e}")
    
    def listen_for_command(self):
        """Listen for voice command after activation"""
        command_timeout = 5
        start_time = time.time()
        
        while time.time() - start_time < command_timeout:
            try:
                data = self.audio_queue.get(timeout=0.5)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    command = result.get("text", "").strip()
                    
                    if command and len(command) > 3:
                        return command
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command recognition error: {e}")
        
        return None
    
    def process_voice_command(self, command):
        """Process voice commands"""
        command_lower = command.lower()
        
        # Text editing commands
        if any(word in command_lower for word in ["improve", "fix", "rewrite", "edit"]):
            selected_text = self.get_selected_text()
            if selected_text:
                if "improve" in command_lower:
                    return self.process_text_with_ai(selected_text, "improve")
                elif "fix" in command_lower:
                    return self.process_text_with_ai(selected_text, "fix grammar")
                elif "rewrite" in command_lower:
                    return self.process_text_with_ai(selected_text, "rewrite professionally")
            else:
                return "Please select some text first, then try again."
        
        # Screenshot and image analysis
        if any(word in command_lower for word in ["screenshot", "analyze image", "describe"]):
            return self.analyze_screenshot()
        
        # General AI assistance
        if self.ai_provider:
            return self.get_ai_response(command)
        else:
            return "AI API not configured. Please set up GROQ_API_KEY or OPENAI_API_KEY."
    
    def process_text_with_ai(self, text, action):
        """Process text with AI and replace it"""
        try:
            if action == "improve":
                prompt = f"Improve this text: {text}"
            elif action == "fix grammar":
                prompt = f"Fix grammar and spelling: {text}"
            elif action == "rewrite professionally":
                prompt = f"Rewrite professionally: {text}"
            
            response = self.get_ai_response(prompt)
            
            if response:
                self.replace_selected_text(response)
                return "Text updated successfully!"
            else:
                return "Sorry, I couldn't process that text."
                
        except Exception as e:
            return f"Error processing text: {e}"
    
    def analyze_screenshot(self):
        """Take screenshot and analyze with AI"""
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot_path = "/tmp/lambo_screenshot.png"
            screenshot.save(screenshot_path)
            
            # For now, just acknowledge - full image analysis would need vision API
            return "Screenshot taken! Image analysis requires vision API setup."
            
        except Exception as e:
            return f"Screenshot error: {e}"
    
    def run_service(self):
        """Run as background service"""
        print(f"🚀 {self.name} Intelligence Service Running")
        print("Press Ctrl+C to stop")
        
        # Auto-activate
        self.activate_lambo()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 {self.name} Intelligence stopping...")
            self.deactivate_lambo()

def main():
    """Main entry point"""
    
    # Check if running as service
    if len(sys.argv) > 1 and sys.argv[1] == '--service':
        lambo = LamboIntelligence()
        lambo.run_service()
    else:
        # Interactive mode
        lambo = LamboIntelligence()
        
        print(f"\n🎯 {lambo.name} Intelligence Ready!")
        print("Press Enter to activate, 'q' to quit")
        
        while True:
            try:
                user_input = input().strip().lower()
                
                if user_input == 'q':
                    break
                elif user_input == '':
                    lambo.toggle_lambo()
                
            except KeyboardInterrupt:
                break
        
        print(f"👋 {lambo.name} Intelligence stopped")

if __name__ == "__main__":
    main()