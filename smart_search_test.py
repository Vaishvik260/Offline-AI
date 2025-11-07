#!/usr/bin/env python3
"""
Smart Search Test - Shows how Limbor gets intelligent answers
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import webbrowser
from datetime import datetime

def get_smart_answer(query):
    """Get intelligent answers using multiple methods"""
    
    # Built-in knowledge first (fastest and most reliable)
    built_in = get_built_in_knowledge(query)
    if built_in:
        return f"💡 {built_in}"
    
    # Try Wikipedia (reliable and fast)
    wiki_result = search_wikipedia(query)
    if wiki_result:
        return f"📚 From Wikipedia: {wiki_result}"
    
    # Try DuckDuckGo (privacy-friendly)
    ddg_result = search_duckduckgo(query)
    if ddg_result:
        return f"🔍 From DuckDuckGo: {ddg_result}"
    
    # Fallback: open browser search
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
    return f"🌐 I've opened a browser search for '{query}' - check the results there!"

def get_built_in_knowledge(query):
    """Built-in knowledge base for common questions"""
    q = query.lower()
    
    # Tech terms
    if "npu" in q:
        return "NPU (Neural Processing Unit) is a specialized chip designed for AI and machine learning tasks. It's found in modern phones and computers to handle AI workloads efficiently, like image recognition, voice processing, and neural networks."
    
    if "ai" in q or "artificial intelligence" in q:
        return "Artificial Intelligence (AI) is computer technology that can perform tasks requiring human-like intelligence - learning, reasoning, problem-solving. Examples include virtual assistants, recommendation systems, and autonomous vehicles."
    
    if "python" in q and ("programming" in q or "language" in q):
        return "Python is a popular programming language known for being easy to learn and powerful. It's used for web development, data science, AI/machine learning, automation, and more. Great for beginners!"
    
    if "machine learning" in q or "ml" in q:
        return "Machine Learning is AI that learns patterns from data without explicit programming. It powers recommendation systems (Netflix, Spotify), image recognition, language translation, and predictive analytics."
    
    # Time queries
    if "time" in q:
        return f"Current time: {datetime.now().strftime('%I:%M %p on %A, %B %d, %Y')}"
    
    if "date" in q or "today" in q:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    
    # Weather (mock response since we can't get real weather without API)
    if "weather" in q:
        return "I can't check live weather data, but you can ask Siri, check your weather app, or visit weather.com for current conditions in your area."
    
    # Programming help
    if "how to" in q and "code" in q:
        return "For coding help, I recommend: 1) Start with Python or JavaScript, 2) Use free resources like Codecademy or freeCodeCamp, 3) Practice on coding challenges, 4) Build small projects to learn."
    
    return None

def search_wikipedia(query):
    """Search Wikipedia API"""
    try:
        # Clean the query for Wikipedia
        clean_query = query.replace("what is", "").replace("who is", "").strip()
        
        # Wikipedia API
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
        
        headers = {'User-Agent': 'LimborAI/1.0'}
        response = requests.get(api_url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            if 'extract' in data and data['extract']:
                extract = data['extract']
                # Clean up the extract
                if len(extract) > 300:
                    extract = extract[:297] + "..."
                return extract
        
        return None
        
    except Exception as e:
        print(f"Wikipedia search failed: {e}")
        return None

def search_duckduckgo(query):
    """Search DuckDuckGo"""
    try:
        url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for result snippets
        results = soup.find_all(['div', 'span'], class_=lambda x: x and 'snippet' in x)
        
        for result in results[:3]:
            text = result.get_text().strip()
            if text and len(text) > 30 and len(text) < 400:
                # Filter out navigation text
                if not any(skip in text.lower() for skip in ['cookies', 'privacy', 'javascript', 'sign in']):
                    return text[:300] + "..." if len(text) > 300 else text
        
        return None
        
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
        return None

def interactive_test():
    """Interactive testing mode"""
    print("🤖 Smart Search Test - Ask me anything!")
    print("Type 'exit' to quit\n")
    
    sample_questions = [
        "What is NPU?",
        "What is artificial intelligence?", 
        "How to learn Python programming?",
        "What is machine learning?",
        "What time is it?",
        "Who is Elon Musk?",
        "What is quantum computing?"
    ]
    
    print("💡 Try these sample questions:")
    for i, q in enumerate(sample_questions, 1):
        print(f"   {i}. {q}")
    print()
    
    while True:
        try:
            question = input("Ask me: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            print("🔍 Thinking...")
            answer = get_smart_answer(question)
            print(f"\n🤖 Limbor: {answer}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_sample_tests():
    """Run predefined tests"""
    test_questions = [
        "What is NPU?",
        "What is artificial intelligence?",
        "What time is it?", 
        "What is Python programming?",
        "Who is Steve Jobs?",
        "What is quantum computing?"
    ]
    
    print("🧪 Running Sample Tests")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        answer = get_smart_answer(question)
        print(f"   Answer: {answer}")
        print("-" * 50)

def main():
    """Main function"""
    print("🚀 Limbor Smart Search Test")
    print("Choose an option:")
    print("1. Interactive mode (ask questions)")
    print("2. Run sample tests")
    print("3. Exit")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        interactive_test()
    elif choice == "2":
        run_sample_tests()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()