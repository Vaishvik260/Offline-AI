#!/usr/bin/env python3
"""
Powered AI - Uses ChatGPT, Gemini, and other AI APIs
Full-featured AI assistant with code generation, summarization, and more
"""

import os
import sys
import json
import requests
from datetime import datetime
import re

class PoweredAI:
    def __init__(self):
        self.name = "Limbor"
        self.conversation_history = []
        
        # API configurations
        self.apis = {
            'openai': {
                'enabled': False,
                'key': os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-3.5-turbo'
            },
            'gemini': {
                'enabled': False,
                'key': os.getenv('GEMINI_API_KEY'),
                'model': 'gemini-pro'
            },
            'groq': {
                'enabled': False,
                'key': os.getenv('GROQ_API_KEY'),
                'model': 'mixtral-8x7b-32768'
            }
        }
        
        self.setup_apis()
        self.show_welcome()
    
    def setup_apis(self):
        """Setup and check available AI APIs"""
        
        # Check OpenAI (ChatGPT)
        if self.apis['openai']['key']:
            self.apis['openai']['enabled'] = True
            print("✅ ChatGPT (OpenAI) API connected")
        
        # Check Gemini
        if self.apis['gemini']['key']:
            self.apis['gemini']['enabled'] = True
            print("✅ Gemini API connected")
        
        # Check Groq (Fast and free alternative)
        if self.apis['groq']['key']:
            self.apis['groq']['enabled'] = True
            print("✅ Groq API connected")
        
        # If no APIs configured, show setup instructions
        if not any(api['enabled'] for api in self.apis.values()):
            print("\n⚠️  No AI APIs configured yet!")
            print("I can still help with basic tasks, but for full AI power, set up an API:\n")
            self.show_api_setup_instructions()
    
    def show_api_setup_instructions(self):
        """Show how to set up AI APIs"""
        print("🔧 **How to Enable AI APIs:**\n")
        
        print("**Option 1: ChatGPT (OpenAI) - Most Popular**")
        print("1. Get API key from: https://platform.openai.com/api-keys")
        print("2. Set environment variable:")
        print("   export OPENAI_API_KEY='your-key-here'\n")
        
        print("**Option 2: Gemini (Google) - Free Tier Available**")
        print("1. Get API key from: https://makersuite.google.com/app/apikey")
        print("2. Set environment variable:")
        print("   export GEMINI_API_KEY='your-key-here'\n")
        
        print("**Option 3: Groq - Fast & Free**")
        print("1. Get API key from: https://console.groq.com")
        print("2. Set environment variable:")
        print("   export GROQ_API_KEY='your-key-here'\n")
        
        print("After setting up, restart this program!\n")
    
    def show_welcome(self):
        """Show welcome message"""
        print(f"\n🤖 {self.name} - Powered AI Assistant")
        print("=" * 50)
        
        if any(api['enabled'] for api in self.apis.values()):
            print("🚀 AI-Powered Features Active!")
            print("I can help with:")
            print("• Code generation and debugging")
            print("• Text summarization and analysis")
            print("• Creative writing and content")
            print("• Complex problem solving")
            print("• Natural conversations")
        else:
            print("💡 Basic mode - Set up an API for full AI power!")
            print("I can still help with:")
            print("• Web search and information")
            print("• Basic text processing")
            print("• Programming help")
            print("• Calculations")
        
        print("\nType 'help' for commands, 'exit' to quit\n")
    
    def chat(self, user_input):
        """Main chat function"""
        
        # Add to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Process input
        response = self.process_input(user_input)
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def process_input(self, user_input):
        """Process user input and generate response"""
        
        user_lower = user_input.lower().strip()
        
        # Special commands
        if user_lower in ['help', 'commands']:
            return self.show_help()
        
        if user_lower == 'setup':
            self.show_api_setup_instructions()
            return "Follow the instructions above to set up AI APIs!"
        
        if user_lower == 'status':
            return self.show_status()
        
        # If AI APIs are available, use them for everything
        if any(api['enabled'] for api in self.apis.values()):
            return self.ai_powered_response(user_input)
        
        # Fallback to basic responses
        return self.basic_response(user_input)
    
    def ai_powered_response(self, user_input):
        """Generate response using AI APIs"""
        
        # Try APIs in order of preference
        api_order = ['groq', 'gemini', 'openai']  # Groq is fastest and free
        
        for api_name in api_order:
            if self.apis[api_name]['enabled']:
                try:
                    print(f"🤖 Thinking with {api_name.title()}...")
                    
                    if api_name == 'openai':
                        return self.use_openai(user_input)
                    elif api_name == 'gemini':
                        return self.use_gemini(user_input)
                    elif api_name == 'groq':
                        return self.use_groq(user_input)
                    
                except Exception as e:
                    print(f"❌ {api_name.title()} error: {e}")
                    continue
        
        # If all APIs fail, use basic response
        return self.basic_response(user_input)
    
    def use_openai(self, user_input):
        """Use OpenAI ChatGPT API"""
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.apis['openai']['key']}",
            "Content-Type": "application/json"
        }
        
        # Prepare messages with conversation history
        messages = [
            {"role": "system", "content": "You are Limbor, a helpful AI assistant. Provide clear, accurate, and friendly responses. For code, use proper formatting. For summaries, be concise but comprehensive."}
        ]
        
        # Add recent conversation history
        messages.extend(self.conversation_history[-10:])
        
        data = {
            "model": self.apis['openai']['model'],
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def use_gemini(self, user_input):
        """Use Google Gemini API"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.apis['gemini']['model']}:generateContent?key={self.apis['gemini']['key']}"
        
        # Prepare conversation context
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-6:]])
        
        full_prompt = f"""You are Limbor, a helpful AI assistant. Provide clear, accurate, and friendly responses.

Previous conversation:
{context}

User: {user_input}As
sistant: Please provide a helpful response."""
        
        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }
        
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    
    def use_groq(self, user_input):
        """Use Groq API (Fast and free)"""
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.apis['groq']['key']}",
            "Content-Type": "application/json"
        }
        
        # Prepare messages
        messages = [
            {"role": "system", "content": "You are Limbor, a helpful AI assistant. Provide clear, accurate, and friendly responses. For code, use proper formatting with ```language blocks. For summaries, be concise but comprehensive."}
        ]
        
        # Add recent conversation history
        messages.extend(self.conversation_history[-8:])
        
        data = {
            "model": self.apis['groq']['model'],
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def basic_response(self, user_input):
        """Basic responses when no AI APIs available"""
        
        user_lower = user_input.lower()
        
        # Greetings
        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm {self.name}. I can help with basic tasks, but for full AI power, please set up an API key. Type 'setup' for instructions!"
        
        # Summarization requests
        if any(word in user_lower for word in ["summarize", "summary", "tldr"]):
            text_to_summarize = self.extract_text_to_summarize(user_input)
            if text_to_summarize:
                return self.basic_summarize(text_to_summarize)
            else:
                return "I can summarize text! Format: 'Summarize: [your text here]'"
        
        # Programming questions
        if any(word in user_lower for word in ["code", "programming", "python", "javascript"]):
            return "I can help with programming! For advanced code generation, please set up an AI API. Type 'setup' for instructions."
        
        # Web search
        return self.web_search_response(user_input)
    
    def extract_text_to_summarize(self, user_input):
        """Extract text for summarization"""
        patterns = [
            r'summarize:?\s*(.*)',
            r'summary:?\s*(.*)',
            r'tldr:?\s*(.*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1).strip()
                if len(text) > 50:
                    return text
        
        return None
    
    def basic_summarize(self, text):
        """Basic text summarization without AI"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        if len(sentences) <= 3:
            return f"**Summary:** This text is already concise:\n\n{text}"
        
        # Take first, middle, and last sentences as basic summary
        key_sentences = [sentences[0]]
        if len(sentences) > 2:
            key_sentences.append(sentences[len(sentences)//2])
        key_sentences.append(sentences[-1])
        
        summary = "**Summary:**\n"
        for i, sentence in enumerate(key_sentences, 1):
            summary += f"{i}. {sentence.strip()}.\n"
        
        return summary
    
    def web_search_response(self, query):
        """Search web for information"""
        try:
            print(f"🔍 Searching web for: {query}")
            
            # Simple web search
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; PoweredAI/1.0)'}
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return f"I found some information about '{query}'. For detailed AI-powered analysis and responses, please set up an API key (type 'setup')."
            else:
                return f"I searched for '{query}' but couldn't get detailed results. For better search and AI responses, set up an API key (type 'setup')."
                
        except Exception as e:
            return f"Search error. For full AI-powered responses, please set up an API key (type 'setup')."
    
    def show_help(self):
        """Show help information"""
        help_text = f"""
**{self.name} AI Assistant Commands:**

**General:**
• Just ask questions naturally!
• 'help' - Show this help
• 'setup' - Show API setup instructions
• 'status' - Check API status
• 'exit' - Quit

**With AI APIs enabled:**
• Code generation: "Write a Python function to..."
• Summarization: "Summarize: [your text]"
• Creative writing: "Write a story about..."
• Problem solving: "How do I solve..."
• Explanations: "Explain quantum computing"

**Current Status:**"""
        
        for api_name, api_info in self.apis.items():
            status = "✅ Connected" if api_info['enabled'] else "❌ Not configured"
            help_text += f"\n• {api_name.title()}: {status}"
        
        if not any(api['enabled'] for api in self.apis.values()):
            help_text += "\n\n💡 Set up an API for full AI power! Type 'setup' for instructions."
        
        return help_text
    
    def show_status(self):
        """Show current API status"""
        status = f"**{self.name} Status Report:**\n\n"
        
        for api_name, api_info in self.apis.items():
            if api_info['enabled']:
                status += f"✅ {api_name.title()}: Connected (Model: {api_info['model']})\n"
            else:
                status += f"❌ {api_name.title()}: Not configured\n"
        
        status += f"\n**Conversation History:** {len(self.conversation_history)} messages"
        status += f"\n**Time:** {datetime.now().strftime('%I:%M %p on %B %d, %Y')}"
        
        if not any(api['enabled'] for api in self.apis.values()):
            status += "\n\n💡 Type 'setup' to configure AI APIs for full power!"
        
        return status

def main():
    """Main chat loop"""
    
    # Install required packages if missing
    try:
        import urllib.parse
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
        import urllib.parse
    
    ai = PoweredAI()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"\n{ai.name}: Thanks for chatting! Set up an API key for even better conversations next time! 👋")
                break
            
            # Get AI response
            response = ai.chat(user_input)
            print(f"\n{ai.name}: {response}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{ai.name}: Goodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Let's keep chatting! Try again.")

if __name__ == "__main__":
    main()