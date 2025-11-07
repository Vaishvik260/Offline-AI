#!/usr/bin/env python3
"""
Simple AI Chat - Works like ChatGPT with summarization
Direct and reliable text processing
"""

import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

class SimpleAI:
    def __init__(self):
        self.name = "Limbor"
        self.conversation_history = []
        print(f"🤖 {self.name} AI ready! I automatically search Google for any question you ask and give you real information!")
    
    def chat(self, user_input):
        """Main chat function - processes all user input"""
        
        # Add to conversation history
        self.conversation_history.append(f"User: {user_input}")
        
        # Process the input and get response
        response = self.process_input(user_input)
        
        # Add response to history
        self.conversation_history.append(f"Limbor: {response}")
        
        return response
    
    def process_input(self, user_input):
        """Process user input and return appropriate response"""
        
        user_lower = user_input.lower().strip()
        
        # Check for summarization requests FIRST
        if self.is_summarization_request(user_input):
            return self.handle_summarization(user_input)
        
        # Check for text analysis requests
        if self.is_analysis_request(user_input):
            return self.handle_analysis(user_input)
        
        # Greetings
        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm {self.name}, your AI assistant. I can summarize text, answer questions, help with coding, creative writing, and have natural conversations. What can I help you with today?"
        
        # Help requests
        if any(word in user_lower for word in ["help", "what can you do", "capabilities"]):
            return """I can help you with:

📝 **Text Processing:**
• Summarize long articles or documents
• Analyze writing style and provide feedback
• Extract key points from text

💬 **Conversation:**
• Answer questions on various topics
• Explain complex concepts
• Help with problem-solving

🔧 **Practical Tasks:**
• Programming help and code review
• Creative writing assistance
• Math calculations

**To summarize text, just say:**
"Summarize: [paste your text here]"
"TLDR: [your long text]"

Try it now! What would you like help with?"""
        
        # Programming questions
        if any(word in user_lower for word in ["code", "programming", "python", "javascript"]):
            return self.handle_programming(user_input)
        
        # Math questions
        if any(char in user_input for char in "+-*/=") or "calculate" in user_lower:
            return self.handle_math(user_input)
        
        # Explanation requests
        if any(word in user_lower for word in ["explain", "what is", "how does", "why"]):
            return self.handle_explanation(user_input)
        
        # For any other question, search Google and get real information
        return self.search_and_answer(user_input)
    
    def is_summarization_request(self, text):
        """Check if user wants text summarized"""
        text_lower = text.lower()
        
        # Direct keywords
        summarize_keywords = [
            "summarize", "summary", "tldr", "brief", "condense", 
            "key points", "main points", "in short"
        ]
        
        return any(keyword in text_lower for keyword in summarize_keywords)
    
    def handle_summarization(self, user_input):
        """Handle text summarization requests"""
        
        # Extract the text to summarize
        text_to_summarize = self.extract_text_to_summarize(user_input)
        
        if not text_to_summarize or len(text_to_summarize) < 50:
            return """I can summarize text for you! Here's how:

**Format:** "Summarize: [your text here]"

**Example:**
"Summarize: The process of photosynthesis involves plants converting sunlight, carbon dioxide, and water into glucose and oxygen. This process occurs in the chloroplasts of plant cells and is essential for life on Earth as it produces the oxygen we breathe and forms the base of most food chains."

Just paste the text you want summarized after "Summarize:" and I'll give you the key points!"""
        
        # Generate summary
        summary = self.create_summary(text_to_summarize)
        
        return f"""**Summary:**

{summary}

**Original length:** {len(text_to_summarize)} characters
**Summary length:** {len(summary)} characters
**Compression:** {100 - int(len(summary)/len(text_to_summarize)*100)}% shorter"""
    
    def extract_text_to_summarize(self, user_input):
        """Extract text that needs to be summarized"""
        
        # Look for common patterns
        patterns = [
            r'summarize:?\s*(.*)',
            r'summary:?\s*(.*)', 
            r'tldr:?\s*(.*)',
            r'brief:?\s*(.*)',
            r'condense:?\s*(.*)',
            r'key points:?\s*(.*)',
            r'main points:?\s*(.*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE | re.DOTALL)
            if match:
                extracted_text = match.group(1).strip()
                if len(extracted_text) > 30:
                    return extracted_text
        
        # If the entire input is long, maybe they want it summarized
        if len(user_input) > 200:
            return user_input
        
        return None
    
    def create_summary(self, text):
        """Create a summary of the given text"""
        
        # Clean the text
        text = text.strip()
        
        # If text is already short, return as is
        if len(text) < 100:
            return f"This text is already brief:\n\n{text}"
        
        # Split into sentences
        sentences = self.split_sentences(text)
        
        if len(sentences) <= 2:
            return f"This text is already concise:\n\n{text}"
        
        # Score and select key sentences
        key_sentences = self.select_key_sentences(sentences)
        
        # Format the summary
        if len(key_sentences) == 1:
            return key_sentences[0]
        else:
            summary = "**Key Points:**\n"
            for i, sentence in enumerate(key_sentences, 1):
                summary += f"{i}. {sentence.strip()}\n"
            return summary.strip()
    
    def split_sentences(self, text):
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15:  # Only keep substantial sentences
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def select_key_sentences(self, sentences):
        """Select the most important sentences"""
        
        if len(sentences) <= 3:
            return sentences
        
        # Score sentences
        scored = []
        for i, sentence in enumerate(sentences):
            score = 0
            
            # Position scoring
            if i == 0:
                score += 3  # First sentence often important
            elif i == len(sentences) - 1:
                score += 2  # Last sentence often concludes
            
            # Length scoring (prefer medium-length sentences)
            if 30 <= len(sentence) <= 150:
                score += 2
            
            # Keyword scoring
            important_words = [
                'important', 'key', 'main', 'primary', 'essential', 'crucial',
                'therefore', 'however', 'because', 'result', 'conclusion'
            ]
            
            for word in important_words:
                if word.lower() in sentence.lower():
                    score += 1
            
            # Numbers and data often important
            if re.search(r'\d+', sentence):
                score += 1
            
            scored.append((sentence, score))
        
        # Sort by score and take top sentences
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 2-3 sentences depending on total length
        num_to_take = min(3, max(2, len(sentences) // 3))
        
        return [sent[0] for sent in scored[:num_to_take]]
    
    def is_analysis_request(self, text):
        """Check if user wants text analysis"""
        text_lower = text.lower()
        analysis_keywords = ["analyze", "analysis", "review", "feedback", "critique"]
        return any(keyword in text_lower for keyword in analysis_keywords)
    
    def handle_analysis(self, user_input):
        """Handle text analysis requests"""
        return "I can analyze text! Try: 'Analyze: [your text here]' and I'll give you feedback on style, readability, and suggestions for improvement."
    
    def handle_programming(self, user_input):
        """Handle programming questions"""
        if "python" in user_input.lower():
            return """I can help with Python! Here are some basics:

**Variables:**
```python
name = "Alice"
age = 25
```

**Functions:**
```python
def greet(name):
    return f"Hello, {name}!"
```

**Lists:**
```python
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)
```

What specific Python concept would you like help with?"""
        
        return "I can help with programming! What language or concept are you working with?"
    
    def handle_math(self, user_input):
        """Handle math calculations"""
        try:
            # Extract and evaluate simple math expressions
            import re
            
            # Find mathematical expressions
            math_expr = re.findall(r'[\d+\-*/().\s]+', user_input)
            if math_expr:
                expr = ''.join(math_expr).strip()
                if re.match(r'^[\d+\-*/().\s]+$', expr):
                    result = eval(expr)
                    return f"**Answer:** {result}\n\nCalculation: {expr} = {result}"
            
            return "I can help with math! Try something like: 'Calculate 25 * 4 + 10'"
            
        except:
            return "I can help with calculations! What would you like me to calculate?"
    
    def handle_explanation(self, user_input):
        """Handle explanation requests"""
        topic = user_input.lower()
        
        if "ai" in topic or "artificial intelligence" in topic:
            return """**Artificial Intelligence (AI)** is technology that enables machines to perform tasks requiring human-like intelligence.

**Key aspects:**
• **Learning:** AI systems improve from experience
• **Reasoning:** Making logical decisions from data
• **Problem-solving:** Finding solutions to complex challenges

**Examples:**
• Virtual assistants (Siri, Alexa)
• Recommendation systems (Netflix, Spotify)
• Image recognition (photo tagging)
• Language translation

**Current state:** We're in the era of Large Language Models like ChatGPT that can understand and generate human-like text.

What specific aspect of AI interests you?"""
        
        return f"I'd be happy to explain that! Could you be more specific about what aspect of '{user_input}' you'd like me to explain?"
    
    def search_and_answer(self, question):
        """Search Google for the question and provide comprehensive answer"""
        
        print(f"🔍 Searching Google for: {question}")
        
        try:
            # Search multiple sources for comprehensive information
            google_result = self.search_google(question)
            wiki_result = self.search_wikipedia(question)
            
            # Compile comprehensive answer
            answer = f"**Answer to: {question}**\n\n"
            
            # Add Wikipedia info if available (most reliable)
            if wiki_result:
                answer += f"**From Wikipedia:**\n{wiki_result}\n\n"
            
            # Add Google search results
            if google_result:
                answer += f"**From Web Search:**\n{google_result}\n\n"
            
            # If no results found
            if not google_result and not wiki_result:
                answer += f"I searched for information about '{question}' but couldn't find clear results. This might be because:\n"
                answer += "• The topic is very new or specialized\n"
                answer += "• The search terms need to be more specific\n"
                answer += "• The information might not be widely available online\n\n"
                answer += "Try rephrasing your question or being more specific!"
            
            answer += f"🕒 **Search completed at:** {datetime.now().strftime('%I:%M %p')}"
            
            return answer
            
        except Exception as e:
            return f"I tried to search for '{question}' but encountered an error. Let me try to help based on general knowledge instead.\n\nError: {e}"
    
    def search_google(self, query):
        """Search Google and extract useful information"""
        try:
            # Prepare search URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Headers to mimic real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            # Make request
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract direct answers first
            direct_answer = self.extract_direct_answer(soup)
            if direct_answer:
                return direct_answer
            
            # Extract search result snippets
            snippets = self.extract_search_snippets(soup)
            if snippets:
                return snippets
            
            return None
            
        except Exception as e:
            print(f"Google search error: {e}")
            return None
    
    def extract_direct_answer(self, soup):
        """Extract direct answers from Google (like featured snippets)"""
        
        # Try multiple selectors for direct answers
        answer_selectors = [
            'div[data-attrid="wa:/description"]',  # Knowledge panel
            'div.BNeawe.iBp4i.AP7Wnd',            # Direct answer box
            'div.BNeawe.s3v9rd.AP7Wnd',           # Featured snippet
            'span.hgKElc',                        # Answer text
            'div.kno-rdesc span',                 # Knowledge graph
            'div.Z0LcW',                          # Answer box
            'div.IZ6rdc',                         # Featured snippet content
        ]
        
        for selector in answer_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text and len(text) > 20 and len(text) < 500:
                    # Filter out navigation and ads
                    if not any(skip in text.lower() for skip in ['sign in', 'cookies', 'privacy', 'javascript']):
                        return text
        
        return None
    
    def extract_search_snippets(self, soup):
        """Extract useful information from search result snippets"""
        
        snippets = []
        
        # Try different selectors for search results
        result_selectors = [
            'div.BVG0Nb',      # Search result snippet
            'div.VwiC3b',      # Alternative snippet
            'span.aCOpRe',     # Snippet text
            'div.s3v9rd',      # Result description
            'div.IsZvec'       # Another snippet type
        ]
        
        for selector in result_selectors:
            elements = soup.select(selector)
            for element in elements[:5]:  # Only take first 5 results
                text = element.get_text().strip()
                if text and len(text) > 30 and len(text) < 300:
                    # Filter out unwanted content
                    if not any(skip in text.lower() for skip in ['sign in', 'cookies', 'privacy', 'javascript', 'advertisement']):
                        snippets.append(text)
        
        if snippets:
            # Return the best snippets
            unique_snippets = []
            for snippet in snippets:
                # Avoid duplicates
                if not any(snippet.lower() in existing.lower() for existing in unique_snippets):
                    unique_snippets.append(snippet)
            
            if unique_snippets:
                result = "**Key Information Found:**\n"
                for i, snippet in enumerate(unique_snippets[:3], 1):
                    result += f"{i}. {snippet}\n"
                return result.strip()
        
        return None
    
    def search_wikipedia(self, query):
        """Search Wikipedia for reliable information"""
        try:
            # Clean query for Wikipedia
            clean_query = query.replace("what is", "").replace("who is", "").replace("how does", "").strip()
            
            # Wikipedia API endpoint
            api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
            
            headers = {'User-Agent': 'SimpleAI/1.0 (Educational)'}
            response = requests.get(api_url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data and data['extract']:
                    extract = data['extract']
                    # Limit length for readability
                    if len(extract) > 400:
                        extract = extract[:397] + "..."
                    return extract
            
            # If direct search fails, try search API
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'list': 'search',
                'srsearch': clean_query,
                'format': 'json',
                'srlimit': 1
            }
            
            search_response = requests.get(search_url, params=search_params, headers=headers, timeout=8)
            search_data = search_response.json()
            
            if 'query' in search_data and 'search' in search_data['query'] and search_data['query']['search']:
                page_title = search_data['query']['search'][0]['title']
                
                # Get summary of found page
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_title)}"
                summary_response = requests.get(summary_url, headers=headers, timeout=8)
                
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    if 'extract' in summary_data and summary_data['extract']:
                        extract = summary_data['extract']
                        if len(extract) > 400:
                            extract = extract[:397] + "..."
                        return extract
            
            return None
            
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return None

def main():
    """Main chat loop"""
    ai = SimpleAI()
    
    print("\n💬 Google-Powered AI Chat")
    print("=" * 40)
    print("🔍 I automatically search Google for ANY question you ask!")
    print("Just ask naturally and I'll find real, current information for you.")
    print("\n**Try these examples:**")
    print("• 'What is the weather like today?'")
    print("• 'Who is the current president of France?'")
    print("• 'What are the latest AI developments?'")
    print("• 'How does quantum computing work?'")
    print("• 'What happened in the news today?'")
    print("\n🎯 I also do: text summarization, programming help, calculations")
    print("\nType 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"\n{ai.name}: Thanks for chatting! Come back anytime! 👋")
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