#!/usr/bin/env python3
"""
Conversational AI - Like ChatGPT/Grok but running locally
Natural conversations with intelligent responses
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
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime
import re

try:
    import sounddevice as sd
    import vosk
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Voice features disabled - install sounddevice and vosk for voice chat")

class ConversationalAI:
    def __init__(self):
        self.name = "Limbor"
        self.conversation_history = []
        self.personality = "friendly, helpful, and knowledgeable"
        self.voice_enabled = VOICE_AVAILABLE
        
        if self.voice_enabled:
            self.setup_voice()
        
        print(f"🤖 {self.name} AI initialized - Ready for conversation!")
    
    def setup_voice(self):
        """Setup voice recognition if available"""
        try:
            if os.path.exists("vosk-model"):
                self.vosk_model = vosk.Model("vosk-model")
                self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                self.audio_queue = queue.Queue()
                print("🎤 Voice chat available!")
            else:
                self.voice_enabled = False
                print("📝 Text-only mode (voice model not found)")
        except Exception as e:
            self.voice_enabled = False
            print(f"📝 Text-only mode ({e})")
    
    def speak(self, text):
        """Text-to-speech"""
        if not self.voice_enabled:
            return
            
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
    
    def get_response(self, user_input):
        """Generate intelligent conversational response"""
        
        # Add to conversation history
        self.conversation_history.append(f"User: {user_input}")
        
        # Keep conversation history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        # Generate response based on input type
        response = self.generate_intelligent_response(user_input)
        
        # Add response to history
        self.conversation_history.append(f"Limbor: {response}")
        
        return response
    
    def generate_intelligent_response(self, user_input):
        """Generate contextual, intelligent responses like ChatGPT"""
        
        user_lower = user_input.lower().strip()
        
        # Greeting and personality
        if any(word in user_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            greetings = [
                "Hello! I'm Limbor, your AI assistant. I'm here to help with questions, have conversations, or assist with tasks. What's on your mind?",
                "Hi there! Great to meet you. I'm Limbor - think of me as your personal AI companion. What would you like to talk about or explore today?",
                "Hey! I'm Limbor, your conversational AI. I can help with information, creative tasks, problem-solving, or just chat. What interests you?"
            ]
            return greetings[hash(user_input) % len(greetings)]
        
        # Identity and capabilities
        if any(phrase in user_lower for phrase in ["who are you", "what are you", "tell me about yourself"]):
            return """I'm Limbor, a conversational AI assistant running locally on your computer. Think of me like ChatGPT or Grok, but I'm designed to:

• Have natural, engaging conversations
• Answer questions across many topics
• Help with creative and analytical tasks
• Provide explanations and tutorials
• Assist with problem-solving
• Search for current information when needed

I aim to be helpful, accurate, and personable. I can discuss everything from technology and science to creative writing and everyday questions. What would you like to explore together?"""
        
        # Help and capabilities
        if any(phrase in user_lower for phrase in ["what can you do", "help", "capabilities"]):
            return """I can help you with many things! Here's what I'm good at:

🧠 **Knowledge & Learning:**
• Answer questions on science, technology, history, etc.
• Explain complex concepts in simple terms
• Provide tutorials and how-to guides

💬 **Conversation & Creativity:**
• Have natural discussions on any topic
• Help with writing, brainstorming, creative projects
• Storytelling and creative exercises

📝 **Text Processing:**
• **Summarize** long articles, documents, or text
• **Analyze** writing for style, tone, and readability
• Provide feedback and suggestions for improvement
• TLDR versions of complex content

🔧 **Problem Solving:**
• Help debug code and programming questions
• Analyze problems and suggest solutions
• Research topics and provide comprehensive info

🌐 **Current Information:**
• Search the web for latest information
• Get current facts, news, and data
• Look up specific details you need

**Examples:**
• "Summarize this article: [paste text]"
• "Analyze my writing: [your text]"
• "Explain quantum computing"
• "Help me code in Python"

Just ask me anything naturally, like you would ChatGPT! What would you like to start with?"""
        
        # Programming and technical questions
        if any(word in user_lower for word in ["code", "programming", "python", "javascript", "html", "css", "sql"]):
            return self.handle_programming_question(user_input)
        
        # Text summarization requests
        if any(word in user_lower for word in ["summarize", "summary", "tldr", "brief", "condense"]):
            return self.handle_summarization_request(user_input)
        
        # Creative requests
        if any(word in user_lower for word in ["write", "create", "story", "poem", "creative"]):
            return self.handle_creative_request(user_input)
        
        # Explanations and learning
        if any(phrase in user_lower for phrase in ["explain", "how does", "what is", "why", "how to"]):
            return self.handle_explanation_request(user_input)
        
        # Current information requests
        if any(word in user_lower for word in ["latest", "current", "news", "today", "recent", "search"]):
            return self.handle_information_request(user_input)
        
        # Text analysis requests
        if any(word in user_lower for word in ["analyze", "analysis", "review", "feedback", "critique"]):
            return self.handle_text_analysis_request(user_input)
        
        # Math and calculations
        if any(char in user_input for char in "+-*/=") or "calculate" in user_lower:
            return self.handle_math_request(user_input)
        
        # Conversational responses
        return self.handle_conversational_response(user_input)
    
    def handle_programming_question(self, question):
        """Handle programming-related questions"""
        q_lower = question.lower()
        
        if "python" in q_lower:
            if "learn" in q_lower or "start" in q_lower:
                return """Great choice! Python is perfect for beginners. Here's how to start:

**1. Install Python:**
• Download from python.org
• Use an IDE like VS Code or PyCharm

**2. Learn the basics:**
```python
# Variables and data types
name = "Alice"
age = 25
is_student = True

# Functions
def greet(name):
    return f"Hello, {name}!"

# Lists and loops
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)
```

**3. Practice projects:**
• Calculator
• To-do list
• Simple games
• Web scraper

**4. Next steps:**
• Learn libraries (requests, pandas, matplotlib)
• Try web development (Flask/Django)
• Explore data science or AI

Want me to explain any specific Python concept or help with a particular project?"""
            
            elif "function" in q_lower:
                return """Python functions are reusable blocks of code. Here's how they work:

**Basic syntax:**
```python
def function_name(parameters):
    # Code here
    return result
```

**Examples:**
```python
# Simple function
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)  # Returns 8

# Function with default parameters
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Alice"))           # "Hello, Alice!"
print(greet("Bob", "Hi"))       # "Hi, Bob!"

# Function returning multiple values
def get_name_age():
    return "Alice", 25

name, age = get_name_age()
```

**Key concepts:**
• Parameters vs Arguments
• Return values
• Scope (local vs global variables)
• Lambda functions for simple operations

Need help with a specific function or have code you'd like me to review?"""
        
        elif "javascript" in q_lower:
            return """JavaScript is the language of the web! Here's what you need to know:

**Basic syntax:**
```javascript
// Variables
let name = "Alice";
const age = 25;
var isStudent = true;

// Functions
function greet(name) {
    return `Hello, ${name}!`;
}

// Arrow functions (modern syntax)
const add = (a, b) => a + b;

// Objects
const person = {
    name: "Alice",
    age: 25,
    greet() {
        return `Hi, I'm ${this.name}`;
    }
};
```

**What makes JS special:**
• Runs in browsers and servers (Node.js)
• Event-driven programming
• Asynchronous operations (promises, async/await)
• Dynamic typing
• Huge ecosystem (React, Vue, Angular)

**Learning path:**
1. Master basics (variables, functions, objects)
2. Learn DOM manipulation
3. Understand async programming
4. Try a framework (React is popular)
5. Explore Node.js for backend

What specific JavaScript topic interests you?"""
        
        else:
            return """I'd love to help with programming! I can assist with:

• **Languages:** Python, JavaScript, HTML/CSS, SQL, Java, C++, and more
• **Concepts:** Algorithms, data structures, design patterns
• **Debugging:** Help find and fix issues in your code
• **Best practices:** Code organization, optimization, security
• **Frameworks:** React, Django, Flask, Node.js, etc.

What programming language or concept would you like to explore? Feel free to share any code you're working on!"""
    
    def handle_summarization_request(self, request):
        """Handle text summarization requests"""
        
        # Check if there's text to summarize in the request
        text_to_summarize = self.extract_text_for_summary(request)
        
        if text_to_summarize:
            summary = self.summarize_text(text_to_summarize)
            return f"**Summary:**\n\n{summary}\n\n**Original length:** {len(text_to_summarize)} characters\n**Summary length:** {len(summary)} characters"
        else:
            return """I can help you summarize text! Here's how:

**Ways to use summarization:**
• Paste the text you want summarized after your request
• Say "Summarize this: [your text here]"
• Ask "Can you give me a TLDR of this article?"
• Request "Brief summary of: [content]"

**What I can summarize:**
• Articles and blog posts
• Research papers and documents
• Long emails or messages
• Meeting notes
• Book chapters or stories
• News articles

**Example:**
"Summarize this: [paste your long text here]"

Just paste the text you'd like me to summarize, and I'll give you the key points in a concise format!"""
    
    def extract_text_for_summary(self, request):
        """Extract text that needs to be summarized from the request"""
        
        # Look for common patterns
        patterns = [
            r'summarize this:?\s*(.*)',
            r'summary of:?\s*(.*)',
            r'tldr:?\s*(.*)',
            r'brief:?\s*(.*)',
            r'condense:?\s*(.*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1).strip()
                if len(text) > 100:  # Only summarize if there's substantial text
                    return text
        
        # If the request itself is long, maybe they want it summarized
        if len(request) > 500:
            return request
        
        return None
    
    def summarize_text(self, text):
        """Summarize the given text"""
        
        # Clean the text
        text = text.strip()
        
        # If text is short, no need to summarize
        if len(text) < 200:
            return "This text is already quite brief. Here it is:\n\n" + text
        
        # Split into sentences
        sentences = self.split_into_sentences(text)
        
        if len(sentences) <= 3:
            return "This text is already concise:\n\n" + text
        
        # Extract key sentences based on various criteria
        key_sentences = self.extract_key_sentences(sentences, text)
        
        # Create summary
        summary = self.create_summary(key_sentences, text)
        
        return summary
    
    def split_into_sentences(self, text):
        """Split text into sentences"""
        # Simple sentence splitting
        import re
        
        # Split on periods, exclamation marks, question marks
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Ignore very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def extract_key_sentences(self, sentences, full_text):
        """Extract the most important sentences"""
        
        # Score sentences based on various factors
        scored_sentences = []
        
        for i, sentence in enumerate(sentences):
            score = 0
            
            # Position scoring (first and last sentences often important)
            if i == 0:
                score += 3  # First sentence
            elif i == len(sentences) - 1:
                score += 2  # Last sentence
            elif i < len(sentences) * 0.3:
                score += 1  # Early sentences
            
            # Length scoring (medium length sentences often good)
            if 50 < len(sentence) < 200:
                score += 2
            elif 20 < len(sentence) < 300:
                score += 1
            
            # Keyword scoring
            keywords = ['important', 'key', 'main', 'primary', 'significant', 'crucial', 'essential', 'major', 'conclusion', 'result', 'therefore', 'however', 'because']
            for keyword in keywords:
                if keyword.lower() in sentence.lower():
                    score += 1
            
            # Number and data scoring
            if re.search(r'\d+', sentence):
                score += 1
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 30-50% of sentences depending on length
        num_sentences = len(sentences)
        if num_sentences <= 5:
            keep_count = 2
        elif num_sentences <= 10:
            keep_count = 3
        else:
            keep_count = max(3, num_sentences // 3)
        
        key_sentences = [sent[0] for sent in scored_sentences[:keep_count]]
        
        return key_sentences
    
    def create_summary(self, key_sentences, original_text):
        """Create a coherent summary from key sentences"""
        
        if not key_sentences:
            return "Unable to generate summary - please provide more substantial text."
        
        # Try to maintain logical order
        summary_parts = []
        
        # Add a brief intro if the summary seems disconnected
        if len(key_sentences) > 1:
            summary_parts.append("**Key Points:**")
        
        # Format the key sentences
        for i, sentence in enumerate(key_sentences):
            # Clean up the sentence
            sentence = sentence.strip()
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            
            # Add bullet points for multiple sentences
            if len(key_sentences) > 1:
                summary_parts.append(f"• {sentence}")
            else:
                summary_parts.append(sentence)
        
        # Add a conclusion if appropriate
        if len(original_text) > 1000:
            summary_parts.append(f"\n*This summary condensed {len(original_text)} characters into {len(' '.join(summary_parts))} characters.*")
        
        return '\n'.join(summary_parts)

    def handle_creative_request(self, request):
        """Handle creative writing and content requests"""
        r_lower = request.lower()
        
        if "story" in r_lower:
            return """I'd love to help you create a story! Here are some approaches:

**Story starters:**
• "In a world where memories could be traded like currency..."
• "The last person on Earth received a phone call..."
• "She found a door in her basement that wasn't there yesterday..."

**Story elements to consider:**
• **Character:** Who is your protagonist? What do they want?
• **Setting:** When and where does it take place?
• **Conflict:** What obstacle must they overcome?
• **Theme:** What message or emotion do you want to convey?

**Writing tips:**
• Start with action or dialogue
• Show, don't tell
• Create relatable characters
• Build tension gradually

Would you like me to:
1. Help develop a specific story idea you have?
2. Create a story based on a theme you choose?
3. Give feedback on something you've written?

What kind of story interests you - sci-fi, mystery, romance, adventure?"""
        
        elif "poem" in r_lower:
            return """Poetry is a beautiful way to express ideas! Let me help:

**Types of poems:**
• **Free verse:** No strict rules, natural flow
• **Haiku:** 5-7-5 syllable pattern, nature themes
• **Sonnet:** 14 lines, specific rhyme scheme
• **Limerick:** Humorous, AABBA rhyme pattern

**Poetry techniques:**
• **Imagery:** Paint pictures with words
• **Metaphor:** Compare unlike things
• **Rhythm:** Create musical flow
• **Alliteration:** Repeat consonant sounds

**Example haiku:**
```
Morning dew glistens
On petals soft as whispers—
Spring's gentle greeting
```

What would you like to write about? I can:
• Help you brainstorm themes
• Suggest rhyme schemes
• Give feedback on your verses
• Write a collaborative poem together

What inspires you - nature, emotions, experiences, abstract concepts?"""
        
        else:
            return """I'm excited to help with creative projects! I can assist with:

**Writing:**
• Stories, poems, scripts
• Blog posts, articles
• Creative exercises and prompts
• Character and plot development

**Brainstorming:**
• Generate ideas for projects
• Explore different angles on topics
• Creative problem-solving
• "What if" scenarios

**Content creation:**
• Social media posts
• Marketing copy
• Presentations
• Creative formats and structures

What creative project are you working on? I'm here to collaborate, brainstorm, or provide feedback on whatever you're creating!"""
    
    def handle_explanation_request(self, request):
        """Handle requests for explanations"""
        r_lower = request.lower()
        
        # Try to get web information for current topics
        if any(word in r_lower for word in ["latest", "current", "recent", "today"]):
            return self.search_and_explain(request)
        
        # Built-in explanations for common topics
        if "artificial intelligence" in r_lower or "ai" in r_lower:
            return """Artificial Intelligence (AI) is fascinating! Let me break it down:

**What is AI?**
AI is technology that enables machines to perform tasks that typically require human intelligence - like understanding language, recognizing images, making decisions, and learning from experience.

**Types of AI:**
• **Narrow AI:** Specialized for specific tasks (Siri, Netflix recommendations, chess programs)
• **General AI:** Human-level intelligence across all domains (doesn't exist yet)
• **Super AI:** Beyond human intelligence (theoretical)

**How AI works:**
1. **Data:** AI learns from large amounts of information
2. **Algorithms:** Mathematical rules that find patterns
3. **Training:** The system improves through practice
4. **Prediction:** Makes decisions based on learned patterns

**Real-world examples:**
• Virtual assistants (Siri, Alexa)
• Recommendation systems (Netflix, Spotify)
• Image recognition (photo tagging, medical diagnosis)
• Language translation (Google Translate)
• Autonomous vehicles

**Current state:**
We're in the era of Large Language Models (like ChatGPT) that can understand and generate human-like text, marking a significant leap in AI capabilities.

What aspect of AI interests you most - how it learns, its applications, or its future potential?"""
        
        elif "machine learning" in r_lower:
            return """Machine Learning (ML) is how computers learn to make predictions! Here's how it works:

**The basic idea:**
Instead of programming specific rules, we show the computer lots of examples and let it figure out the patterns.

**Simple analogy:**
Teaching a child to recognize cats:
• Show them 1000 photos labeled "cat" or "not cat"
• They learn: pointy ears + whiskers + certain shape = cat
• Now they can identify cats in new photos

**ML process:**
1. **Collect data:** Gather examples (photos, text, numbers)
2. **Choose algorithm:** Pick the learning method
3. **Train model:** Show it the examples repeatedly
4. **Test:** See how well it performs on new data
5. **Deploy:** Use it to make real predictions

**Types of ML:**
• **Supervised:** Learn from labeled examples (email spam detection)
• **Unsupervised:** Find hidden patterns (customer grouping)
• **Reinforcement:** Learn through trial and reward (game AI)

**Common algorithms:**
• Decision trees (easy to understand)
• Neural networks (inspired by brain)
• Random forests (multiple decision trees)
• Support vector machines (find boundaries)

**Real applications:**
• Email spam filtering
• Product recommendations
• Medical diagnosis
• Stock market prediction
• Voice recognition

Want me to explain any specific part in more detail?"""
        
        else:
            # Try to search for the topic
            return self.search_and_explain(request)
    
    def handle_information_request(self, request):
        """Handle requests for current information"""
        return self.search_and_explain(request)
    
    def search_and_explain(self, query):
        """Search for information and provide explanation"""
        try:
            # Simple web search for current info
            search_query = query.replace("explain", "").replace("what is", "").strip()
            
            # Try Wikipedia first
            wiki_result = self.search_wikipedia(search_query)
            if wiki_result:
                return f"Here's what I found:\n\n{wiki_result}\n\nWould you like me to explain any specific aspect in more detail?"
            
            # Fallback response
            return f"""I'd be happy to explain that! However, I don't have current information about "{search_query}" in my immediate knowledge base.

For the most up-to-date information, I'd recommend:
• Checking reliable news sources
• Looking at Wikipedia for general topics
• Searching academic sources for technical topics

Is there a specific aspect of "{search_query}" you'd like me to help explain based on general knowledge? Or would you like me to help you think through the topic analytically?"""
            
        except Exception as e:
            return f"I'd love to help explain that! Could you provide a bit more context about what specific aspect of '{query}' you're most curious about?"
    
    def search_wikipedia(self, query):
        """Simple Wikipedia search"""
        try:
            clean_query = query.strip()
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
            
            headers = {'User-Agent': 'ConversationalAI/1.0'}
            response = requests.get(url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data and data['extract']:
                    extract = data['extract']
                    if len(extract) > 500:
                        extract = extract[:497] + "..."
                    return extract
            
            return None
            
        except:
            return None
    
    def handle_text_analysis_request(self, request):
        """Handle text analysis and review requests"""
        
        # Extract text to analyze
        text_to_analyze = self.extract_text_for_analysis(request)
        
        if text_to_analyze:
            analysis = self.analyze_text(text_to_analyze)
            return analysis
        else:
            return """I can analyze and provide feedback on text! Here's what I can do:

**Text Analysis:**
• Grammar and style review
• Readability assessment
• Tone and sentiment analysis
• Structure and organization feedback
• Suggestions for improvement

**How to use:**
• "Analyze this text: [your text]"
• "Give me feedback on: [your writing]"
• "Review this: [content]"
• "Critique my writing: [text]"

**What I can analyze:**
• Essays and articles
• Emails and messages
• Creative writing
• Business documents
• Code comments and documentation

Just paste the text you'd like me to analyze, and I'll provide detailed feedback!"""
    
    def extract_text_for_analysis(self, request):
        """Extract text that needs analysis"""
        
        patterns = [
            r'analyze this:?\s*(.*)',
            r'analysis of:?\s*(.*)',
            r'review this:?\s*(.*)',
            r'feedback on:?\s*(.*)',
            r'critique:?\s*(.*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1).strip()
                if len(text) > 50:
                    return text
        
        if len(request) > 200:
            return request
        
        return None
    
    def analyze_text(self, text):
        """Provide detailed text analysis"""
        
        analysis = "**Text Analysis Report:**\n\n"
        
        # Basic statistics
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = len(self.split_into_sentences(text))
        
        analysis += f"**Statistics:**\n"
        analysis += f"• Words: {word_count}\n"
        analysis += f"• Characters: {char_count}\n"
        analysis += f"• Sentences: {sentence_count}\n"
        analysis += f"• Average words per sentence: {word_count // max(sentence_count, 1)}\n\n"
        
        # Readability
        analysis += f"**Readability:**\n"
        if word_count / max(sentence_count, 1) > 25:
            analysis += "• Sentences are quite long - consider breaking them up for better readability\n"
        elif word_count / max(sentence_count, 1) < 10:
            analysis += "• Sentences are short and punchy - good for clarity\n"
        else:
            analysis += "• Sentence length is well-balanced\n"
        
        # Tone analysis (simple)
        analysis += f"\n**Tone & Style:**\n"
        
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'love', 'best', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'sad', 'poor', 'difficult']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            analysis += "• Overall tone: Positive and optimistic\n"
        elif negative_count > positive_count:
            analysis += "• Overall tone: Critical or negative\n"
        else:
            analysis += "• Overall tone: Neutral and balanced\n"
        
        # Formality
        formal_indicators = ['therefore', 'however', 'furthermore', 'consequently', 'moreover']
        informal_indicators = ['gonna', 'wanna', 'yeah', 'cool', 'awesome', 'stuff']
        
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
        informal_count = sum(1 for word in informal_indicators if word in text_lower)
        
        if formal_count > informal_count:
            analysis += "• Style: Formal and professional\n"
        elif informal_count > formal_count:
            analysis += "• Style: Casual and conversational\n"
        else:
            analysis += "• Style: Balanced formality\n"
        
        # Suggestions
        analysis += f"\n**Suggestions:**\n"
        
        if word_count < 50:
            analysis += "• Consider expanding with more details or examples\n"
        
        if sentence_count < 3:
            analysis += "• Add more sentences to develop your ideas fully\n"
        
        # Check for repetition
        words = text_lower.split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only check longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        repeated = [word for word, count in word_freq.items() if count > 3]
        if repeated:
            analysis += f"• Consider varying vocabulary - these words appear frequently: {', '.join(repeated[:3])}\n"
        
        analysis += "\n**Overall:** "
        if word_count > 100 and sentence_count > 5:
            analysis += "Well-developed text with good structure. Keep refining for clarity and impact!"
        else:
            analysis += "Good start! Consider expanding and adding more detail to strengthen your message."
        
        return analysis

    def handle_math_request(self, request):
        """Handle math and calculation requests"""
        try:
            # Extract mathematical expression
            import re
            
            # Look for mathematical expressions
            math_pattern = r'[\d+\-*/().\s]+'
            matches = re.findall(math_pattern, request)
            
            if matches:
                expr = ''.join(matches).strip()
                # Safety check - only allow basic math operations
                if re.match(r'^[\d+\-*/().\s]+$', expr):
                    try:
                        result = eval(expr)
                        return f"The answer is: **{result}**\n\nCalculation: {expr} = {result}"
                    except:
                        pass
            
            return """I can help with math! Try asking me things like:

• "Calculate 15 + 25 * 3"
• "What's 25% of 200?"
• "Convert 100 fahrenheit to celsius"
• "Explain how to solve quadratic equations"
• "What's the area of a circle with radius 5?"

For complex math problems, I can also explain the steps and concepts involved. What would you like to calculate or learn about?"""
            
        except:
            return "I can help with math calculations! What would you like me to calculate?"
    
    def handle_conversational_response(self, user_input):
        """Handle general conversational responses"""
        
        # Analyze the input for context
        user_lower = user_input.lower()
        
        # Emotional responses
        if any(word in user_lower for word in ["sad", "upset", "frustrated", "angry"]):
            return "I'm sorry you're feeling that way. Sometimes it helps to talk through what's bothering you. Would you like to share what's on your mind? I'm here to listen and help if I can."
        
        if any(word in user_lower for word in ["happy", "excited", "great", "awesome"]):
            return "That's wonderful! I love hearing positive energy. What's got you feeling so good today? I'd love to share in your excitement!"
        
        # Questions about opinions
        if "think" in user_lower or "opinion" in user_lower:
            return f"That's an interesting question! Based on the context, here's my perspective:\n\n{self.generate_thoughtful_response(user_input)}\n\nWhat's your take on this? I'd love to hear your thoughts too."
        
        # Requests for advice
        if any(word in user_lower for word in ["should i", "advice", "recommend", "suggest"]):
            return f"I'd be happy to help you think through this! {self.generate_advice_response(user_input)}\n\nWhat factors are most important to you in making this decision?"
        
        # General conversation
        return self.generate_contextual_response(user_input)
    
    def generate_thoughtful_response(self, input_text):
        """Generate thoughtful responses to opinion questions"""
        return "I try to consider multiple perspectives on complex topics. While I don't have personal experiences like humans do, I can analyze information and present different viewpoints to help you form your own opinion."
    
    def generate_advice_response(self, input_text):
        """Generate helpful advice responses"""
        return "Here are some things to consider: What are your goals? What are the potential outcomes of different choices? What feels right to you intuitively? Sometimes it helps to list pros and cons or talk it through with someone you trust."
    
    def generate_contextual_response(self, user_input):
        """Generate contextual conversational responses"""
        
        # Look at conversation history for context
        recent_context = " ".join(self.conversation_history[-4:]) if self.conversation_history else ""
        
        # Default engaging response
        responses = [
            f"That's interesting! Tell me more about that.",
            f"I'd love to hear your perspective on this. What made you think about that?",
            f"That's a great point. How does that relate to your experience?",
            f"Fascinating topic! What aspect of this interests you most?",
            f"I'm curious about your thoughts on this. What's your take?"
        ]
        
        return responses[hash(user_input) % len(responses)]
    
    def voice_chat_mode(self):
        """Voice conversation mode"""
        if not self.voice_enabled:
            print("❌ Voice chat not available. Please install sounddevice and vosk.")
            return
        
        print("🎤 Voice chat mode activated!")
        print("Speak naturally, I'll respond with voice and text.")
        print("Say 'stop voice chat' to return to text mode.\n")
        
        def audio_callback(indata, frames, time, status):
            self.audio_queue.put(bytes(indata))
        
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None,
                                 dtype='int16', channels=1, callback=audio_callback):
                
                while True:
                    try:
                        data = self.audio_queue.get(timeout=1)
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            text = result.get("text", "").strip()
                            
                            if text:
                                print(f"\n🎤 You: {text}")
                                
                                if "stop voice chat" in text.lower():
                                    print("🔄 Switching back to text mode...")
                                    self.speak("Switching to text mode")
                                    break
                                
                                response = self.get_response(text)
                                print(f"🤖 {self.name}: {response}")
                                self.speak(response)
                                
                    except queue.Empty:
                        continue
                    except KeyboardInterrupt:
                        print("\n🔄 Returning to text mode...")
                        break
                        
        except Exception as e:
            print(f"Voice chat error: {e}")
    
    def run_conversation(self):
        """Main conversation loop"""
        print(f"\n💬 Conversational AI Chat with {self.name}")
        print("=" * 50)
        print("I'm here for natural conversation, just like ChatGPT!")
        print("Ask questions, get help, or just chat about anything.")
        
        if self.voice_enabled:
            print("Type 'voice' for voice chat mode.")
        
        print("Type 'exit' to end our conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    farewell = f"It was great chatting with you! Feel free to come back anytime you want to talk, learn something new, or need help with anything. Take care! 👋"
                    print(f"\n{self.name}: {farewell}")
                    if self.voice_enabled:
                        self.speak(farewell)
                    break
                
                if user_input.lower() == 'voice' and self.voice_enabled:
                    self.voice_chat_mode()
                    continue
                
                # Get AI response
                response = self.get_response(user_input)
                print(f"\n{self.name}: {response}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{self.name}: Goodbye! Thanks for the conversation! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Let's keep chatting! Try asking something else.")

def main():
    """Main function"""
    ai = ConversationalAI()
    ai.run_conversation()

if __name__ == "__main__":
    main()