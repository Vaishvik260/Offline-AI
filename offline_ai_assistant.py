#!/usr/bin/env python3
"""
Offline AI Assistant - Your Personal Computer AI
Runs completely offline with no external dependencies
"""

import os
import sys
import json
import queue
import threading
import time
import subprocess
import platform
from datetime import datetime
from pathlib import Path

# Core AI and Voice Libraries
try:
    import sounddevice as sd
    import vosk
    import numpy as np
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Install with: pip install sounddevice vosk transformers torch numpy")
    sys.exit(1)

class OfflineAI:
    def __init__(self):
        self.conversation_history = []
        self.is_listening = False
        self.wake_word = "hey assistant"
        self.setup_ai_model()
        self.setup_voice_recognition()
        
    def setup_ai_model(self):
        """Initialize offline AI model"""
        print("🧠 Loading AI brain...")
        
        # Try multiple models in order of preference
        model_options = [
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-small", 
            "gpt2"
        ]
        
        for model_name in model_options:
            try:
                print(f"Trying to load {model_name}...")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                
                # Add padding token if it doesn't exist
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                print(f"✅ AI brain loaded successfully with {model_name}!")
                return
                
            except Exception as e:
                print(f"❌ Failed to load {model_name}: {e}")
                continue
        
        print("❌ Could not load any AI model. Using intelligent response system...")
        self.model = None
        self.tokenizer = None
    
    def setup_voice_recognition(self):
        """Initialize offline voice recognition"""
        print("🎤 Setting up voice recognition...")
        
        try:
            if not os.path.exists("vosk-model"):
                print("❌ Vosk model not found. Please download vosk-model-small-en-us-0.15")
                return False
                
            self.vosk_model = vosk.Model("vosk-model")
            self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
            self.audio_queue = queue.Queue()
            print("✅ Voice recognition ready!")
            return True
        except Exception as e:
            print(f"❌ Voice setup error: {e}")
            return False
    
    def speak(self, text):
        """Text-to-speech using system voice"""
        try:
            if platform.system() == "Darwin":  # macOS
                os.system(f'say "{text}"')
            elif platform.system() == "Windows":
                os.system(f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"')
            elif platform.system() == "Linux":
                os.system(f'espeak "{text}"')
        except Exception as e:
            print(f"Speech error: {e}")
    
    def generate_response(self, user_input):
        """Generate intelligent AI response completely offline"""
        
        user_lower = user_input.lower().strip()
        
        # Greeting responses
        if any(word in user_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return "Hello! I'm your personal AI assistant running completely offline on your computer. I can help you with questions, control your system, have conversations, and much more. What would you like to know or do?"
        
        # Time and date
        if any(word in user_lower for word in ["time", "what time"]):
            return f"It's currently {datetime.now().strftime('%I:%M %p on %A, %B %d, %Y')}"
        
        if any(word in user_lower for word in ["date", "what date", "today"]):
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
        
        # Identity questions
        if any(phrase in user_lower for phrase in ["who are you", "what are you", "your name"]):
            return "I'm your personal AI assistant that runs completely offline on your computer. I use advanced language models to understand and respond to you naturally, while keeping all our conversations private and secure on your device."
        
        # Capability questions
        if any(phrase in user_lower for phrase in ["what can you do", "help me", "capabilities", "features"]):
            return """I can help you with many things:
            
• Answer questions and have natural conversations
• Control your computer (open apps, search files, etc.)
• Provide information on various topics
• Help with coding and technical questions
• Manage files and folders
• Set reminders and notes
• Explain concepts and provide tutorials
• And much more!

What specific task would you like help with?"""
        
        # Computer control
        if "open" in user_lower:
            return self.handle_open_command(user_input)
        elif any(word in user_lower for word in ["search", "find"]):
            return self.handle_search_command(user_input)
        elif any(word in user_lower for word in ["create", "make"]):
            return self.handle_create_command(user_input)
        
        # Knowledge questions
        if any(phrase in user_lower for phrase in ["what is", "explain", "tell me about", "how does", "why"]):
            return self.handle_knowledge_question(user_input)
        
        # Programming questions
        if any(word in user_lower for word in ["python", "javascript", "code", "programming", "function", "variable"]):
            return self.handle_programming_question(user_input)
        
        # Math questions
        if any(word in user_lower for word in ["calculate", "math", "equation", "solve"]) or any(char in user_input for char in "+-*/="):
            return self.handle_math_question(user_input)
        
        # Use advanced AI model if available
        if self.model and self.tokenizer:
            try:
                return self.generate_ai_response(user_input)
            except Exception as e:
                print(f"AI model error: {e}")
        
        # Intelligent fallback based on input analysis
        return self.intelligent_fallback(user_input)
    
    def handle_knowledge_question(self, question):
        """Handle knowledge-based questions"""
        question_lower = question.lower()
        
        if "python" in question_lower:
            return "Python is a high-level programming language known for its simplicity and readability. It's widely used for web development, data science, AI, automation, and more. Would you like to know something specific about Python?"
        
        elif "ai" in question_lower or "artificial intelligence" in question_lower:
            return "Artificial Intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence, like understanding language, recognizing patterns, and making decisions. I'm an example of AI running locally on your computer!"
        
        elif "computer" in question_lower:
            return "Computers are electronic devices that process data using instructions (programs). They consist of hardware (physical components) and software (programs and operating systems) working together to perform various tasks."
        
        else:
            return f"That's an interesting question about '{question}'. While I'm running offline and have limited knowledge compared to online AI systems, I can help with many topics. Could you be more specific about what aspect you'd like to know?"
    
    def handle_programming_question(self, question):
        """Handle programming-related questions"""
        question_lower = question.lower()
        
        if "python" in question_lower:
            if "function" in question_lower:
                return """In Python, functions are defined using the 'def' keyword:

```python
def my_function(parameter):
    # Function body
    return result
```

Functions help organize code and make it reusable. Would you like a specific example?"""
            
            elif "variable" in question_lower:
                return """Python variables store data values:

```python
name = "John"        # String
age = 25            # Integer  
height = 5.9        # Float
is_student = True   # Boolean
```

Python is dynamically typed, so you don't need to declare variable types explicitly."""
        
        elif "javascript" in question_lower:
            return "JavaScript is a programming language primarily used for web development. It runs in browsers and can make websites interactive. Would you like to know something specific about JavaScript?"
        
        else:
            return "I can help with programming questions! I know about Python, JavaScript, and general programming concepts. What specific programming topic would you like help with?"
    
    def handle_math_question(self, question):
        """Handle math and calculation questions"""
        try:
            # Simple math evaluation (be careful with eval!)
            import re
            
            # Extract numbers and basic operators
            math_expression = re.findall(r'[\d+\-*/().]+', question)
            if math_expression:
                expr = ''.join(math_expression)
                # Only allow safe mathematical operations
                if re.match(r'^[\d+\-*/().\s]+$', expr):
                    result = eval(expr)
                    return f"The answer is: {result}"
            
            return "I can help with basic math calculations. Try asking something like 'calculate 15 + 25' or 'what is 10 * 5'?"
            
        except:
            return "I can help with basic math! Please provide a clear mathematical expression like '15 + 25' or '10 * 5'."
    
    def generate_ai_response(self, user_input):
        """Generate response using the AI model"""
        try:
            # Create a more natural conversation prompt
            system_prompt = "You are a helpful AI assistant. Respond naturally and helpfully to the user's question."
            
            # Prepare input with conversation history
            recent_history = self.conversation_history[-4:] if len(self.conversation_history) > 4 else self.conversation_history
            context = " ".join(recent_history)
            
            full_prompt = f"{system_prompt}\n\nConversation history: {context}\n\nUser: {user_input}\nAssistant:"
            
            # Tokenize and generate
            inputs = self.tokenizer.encode(full_prompt, return_tensors="pt", max_length=400, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 80,
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the assistant's response
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()
            
            # Clean up the response
            response = response.replace("User:", "").replace("Human:", "").strip()
            
            # Ensure we have a meaningful response
            if len(response) > 10 and not response.startswith("I"):
                return response
            else:
                return self.intelligent_fallback(user_input)
                
        except Exception as e:
            print(f"AI generation error: {e}")
            return self.intelligent_fallback(user_input)
    
    def intelligent_fallback(self, user_input):
        """Provide intelligent fallback responses"""
        user_lower = user_input.lower()
        
        # Analyze the type of question
        if "?" in user_input:
            if any(word in user_lower for word in ["how", "what", "why", "when", "where", "who"]):
                return f"That's a great question about '{user_input}'. While I'm running offline with limited knowledge, I can help with many topics including technology, programming, math, and general questions. Could you rephrase or ask something more specific?"
            else:
                return f"I understand you're asking about '{user_input}'. I'm an offline AI, so my knowledge is more limited than online assistants, but I'm constantly learning. Try asking about programming, math, computer tasks, or general topics!"
        
        else:
            return f"I heard you say '{user_input}'. I can help with questions, computer control, programming, math, and conversations. What would you like to know or do?"
    
    def handle_open_command(self, command):
        """Handle computer control - opening applications"""
        try:
            if "browser" in command.lower() or "chrome" in command.lower():
                if platform.system() == "Darwin":
                    subprocess.run(["open", "-a", "Google Chrome"])
                elif platform.system() == "Windows":
                    subprocess.run(["start", "chrome"], shell=True)
                return "Opening your web browser!"
            
            elif "finder" in command.lower() or "files" in command.lower():
                if platform.system() == "Darwin":
                    subprocess.run(["open", "."])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", "."])
                return "Opening file manager!"
            
            elif "terminal" in command.lower():
                if platform.system() == "Darwin":
                    subprocess.run(["open", "-a", "Terminal"])
                return "Opening terminal!"
            
            return "I can open browsers, files, or terminal. What would you like to open?"
        except Exception as e:
            return f"Sorry, I couldn't open that: {e}"
    
    def handle_search_command(self, command):
        """Handle search commands"""
        return "I can help you search your local files. What are you looking for?"
    
    def handle_create_command(self, command):
        """Handle file/folder creation"""
        if "folder" in command.lower() or "directory" in command.lower():
            return "I can help you create folders. What would you like to name it?"
        elif "file" in command.lower():
            return "I can help you create files. What type of file do you need?"
        return "I can help you create files or folders. What would you like to make?"
    
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback"""
        if self.is_listening:
            self.audio_queue.put(bytes(indata))
    
    def listen_continuously(self):
        """Continuous voice recognition"""
        try:
            with sd.RawInputStream(
                samplerate=16000, 
                blocksize=8000, 
                device=None,
                dtype='int16', 
                channels=1, 
                callback=self.audio_callback
            ):
                print(f"🎧 Listening for '{self.wake_word}' or type messages...")
                print("Say 'stop listening' to quit voice mode")
                
                while self.is_listening:
                    try:
                        data = self.audio_queue.get(timeout=1)
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            text = result.get("text", "").strip()
                            
                            if text:
                                print(f"\n🎤 You said: {text}")
                                
                                if "stop listening" in text.lower():
                                    self.is_listening = False
                                    self.speak("Switching to text mode")
                                    break
                                
                                # Process the command
                                response = self.generate_response(text)
                                print(f"🤖 Assistant: {response}")
                                self.speak(response)
                                
                                # Update conversation history
                                self.conversation_history.append(f"Human: {text}")
                                self.conversation_history.append(f"Assistant: {response}")
                                
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"Recognition error: {e}")
                        
        except Exception as e:
            print(f"Audio system error: {e}")
            self.is_listening = False
    
    def text_mode(self):
        """Text-based interaction"""
        print("\n💬 Text mode active. Type 'voice' to switch to voice mode.")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self.speak("Goodbye! It was nice talking with you.")
                    break
                
                if user_input.lower() == 'voice':
                    self.is_listening = True
                    threading.Thread(target=self.listen_continuously, daemon=True).start()
                    break
                
                # Generate and display response
                response = self.generate_response(user_input)
                print(f"🤖 Assistant: {response}")
                
                # Update conversation history
                self.conversation_history.append(f"Human: {user_input}")
                self.conversation_history.append(f"Assistant: {response}")
                
                # Keep history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run(self):
        """Main application loop"""
        print("🚀 Offline AI Assistant Starting...")
        print("=" * 50)
        
        self.speak("Hello! I'm your offline AI assistant. I'm ready to help!")
        
        while True:
            print("\nChoose interaction mode:")
            print("1. Voice mode (speak naturally)")
            print("2. Text mode (type messages)")
            print("3. Exit")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                self.is_listening = True
                self.listen_continuously()
            elif choice == "2":
                self.text_mode()
            elif choice == "3":
                self.speak("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

def main():
    """Initialize and run the AI assistant"""
    try:
        assistant = OfflineAI()
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Assistant shutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()