#!/usr/bin/env python3
"""
Intelligent Limbor AI - Comprehensive Research Assistant
Provides detailed answers with sources, all in the terminal
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import time
from datetime import datetime
import re

class IntelligentLimbor:
    def __init__(self):
        self.name = "Limbor"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def get_comprehensive_answer(self, query):
        """Get comprehensive answer with multiple sources"""
        print(f"🔍 Researching: {query}")
        print("📚 Gathering information from multiple sources...")
        
        # Collect information from multiple sources
        sources = []
        
        # 1. Built-in knowledge
        built_in = self.get_built_in_knowledge(query)
        if built_in:
            sources.append(("Built-in Knowledge", built_in))
        
        # 2. Wikipedia (most reliable)
        wiki_info = self.search_wikipedia_detailed(query)
        if wiki_info:
            sources.append(("Wikipedia", wiki_info))
        
        # 3. Multiple web sources
        web_results = self.search_multiple_sources(query)
        sources.extend(web_results)
        
        # 4. Compile comprehensive answer
        return self.compile_comprehensive_response(query, sources)
    
    def get_built_in_knowledge(self, query):
        """Comprehensive built-in knowledge base"""
        q = query.lower()
        
        # Technology terms
        if "npu" in q:
            return {
                "definition": "Neural Processing Unit (NPU) is a specialized microprocessor designed to accelerate artificial intelligence and machine learning computations.",
                "details": "NPUs are optimized for neural network operations like matrix multiplications, convolutions, and other AI workloads. They're found in modern smartphones (Apple A17 Pro, Qualcomm Snapdragon), laptops (Apple M-series, Intel Core Ultra), and dedicated AI chips.",
                "applications": "Used for on-device AI tasks like image recognition, natural language processing, voice assistants, camera enhancements, and real-time translation.",
                "advantages": "More energy-efficient than CPUs/GPUs for AI tasks, enables privacy-preserving on-device AI, reduces latency by avoiding cloud processing."
            }
        
        if "artificial intelligence" in q or "ai" in q:
            return {
                "definition": "Artificial Intelligence (AI) is the simulation of human intelligence in machines programmed to think and learn like humans.",
                "types": "Narrow AI (specific tasks like Siri), General AI (human-level intelligence, not yet achieved), Super AI (beyond human intelligence, theoretical)",
                "applications": "Virtual assistants, recommendation systems, autonomous vehicles, medical diagnosis, fraud detection, language translation, image recognition",
                "technologies": "Machine Learning, Deep Learning, Neural Networks, Natural Language Processing, Computer Vision",
                "current_state": "We're in the era of Narrow AI with rapid advances in Large Language Models (ChatGPT, GPT-4) and multimodal AI systems."
            }
        
        if "python" in q and ("programming" in q or "language" in q):
            return {
                "definition": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
                "features": "Easy syntax, extensive libraries, cross-platform, object-oriented and functional programming support",
                "uses": "Web development (Django, Flask), Data Science (Pandas, NumPy), AI/ML (TensorFlow, PyTorch), Automation, Scientific computing",
                "advantages": "Beginner-friendly, large community, extensive documentation, rapid development",
                "learning_path": "Start with basics → Learn data structures → Practice projects → Explore libraries → Build real applications"
            }
        
        if "machine learning" in q or "ml" in q:
            return {
                "definition": "Machine Learning is a subset of AI that enables computers to learn and improve from data without explicit programming.",
                "types": "Supervised Learning (labeled data), Unsupervised Learning (pattern finding), Reinforcement Learning (reward-based)",
                "algorithms": "Linear Regression, Decision Trees, Random Forest, Neural Networks, Support Vector Machines, K-means Clustering",
                "applications": "Recommendation systems, Image recognition, Natural language processing, Predictive analytics, Autonomous systems",
                "process": "Data Collection → Data Preprocessing → Model Selection → Training → Evaluation → Deployment → Monitoring"
            }
        
        return None
    
    def search_wikipedia_detailed(self, query):
        """Get detailed Wikipedia information"""
        try:
            # Clean query for Wikipedia
            clean_query = re.sub(r'\b(what is|who is|tell me about|explain)\b', '', query, flags=re.IGNORECASE).strip()
            
            # Search for pages
            search_url = f"https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'list': 'search',
                'srsearch': clean_query,
                'format': 'json',
                'srlimit': 3
            }
            
            search_response = self.session.get(search_url, params=search_params, timeout=10)
            search_data = search_response.json()
            
            if 'query' in search_data and 'search' in search_data['query']:
                results = search_data['query']['search']
                
                for result in results:
                    page_title = result['title']
                    
                    # Get page content
                    content_params = {
                        'action': 'query',
                        'format': 'json',
                        'titles': page_title,
                        'prop': 'extracts|info',
                        'exintro': True,
                        'explaintext': True,
                        'exsectionformat': 'plain',
                        'inprop': 'url'
                    }
                    
                    content_response = self.session.get(search_url, params=content_params, timeout=10)
                    content_data = content_response.json()
                    
                    if 'query' in content_data and 'pages' in content_data['query']:
                        pages = content_data['query']['pages']
                        for page_id, page_info in pages.items():
                            if 'extract' in page_info and page_info['extract']:
                                extract = page_info['extract']
                                url = page_info.get('fullurl', f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page_title)}")
                                
                                return {
                                    'title': page_title,
                                    'content': extract[:800] + "..." if len(extract) > 800 else extract,
                                    'url': url
                                }
            
            return None
            
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return None
    
    def search_multiple_sources(self, query):
        """Search multiple web sources"""
        sources = []
        
        # Try DuckDuckGo
        ddg_result = self.search_duckduckgo_detailed(query)
        if ddg_result:
            sources.append(("DuckDuckGo Search", ddg_result))
        
        # Try to get news if it's a current topic
        if any(word in query.lower() for word in ['news', 'latest', 'current', 'today', 'recent']):
            news_result = self.search_news(query)
            if news_result:
                sources.append(("News Sources", news_result))
        
        return sources
    
    def search_duckduckgo_detailed(self, query):
        """Detailed DuckDuckGo search"""
        try:
            url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Find search results
            result_elements = soup.find_all('div', class_='result')
            
            for element in result_elements[:3]:
                title_elem = element.find('a', class_='result__a')
                snippet_elem = element.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    snippet = snippet_elem.get_text().strip()
                    link = title_elem.get('href', '')
                    
                    if snippet and len(snippet) > 30:
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'url': link
                        })
            
            return results if results else None
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return None
    
    def search_news(self, query):
        """Search for news (simplified)"""
        try:
            # Use DuckDuckGo news search
            news_query = f"{query} news"
            url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(news_query)}&iar=news"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for news results
            news_results = []
            result_elements = soup.find_all('div', class_='result')
            
            for element in result_elements[:2]:
                title_elem = element.find('a')
                if title_elem:
                    title = title_elem.get_text().strip()
                    if any(news_word in title.lower() for news_word in ['news', 'report', 'update', 'announce']):
                        news_results.append(title)
            
            return news_results if news_results else None
            
        except Exception as e:
            print(f"News search error: {e}")
            return None
    
    def compile_comprehensive_response(self, query, sources):
        """Compile all sources into a comprehensive response"""
        if not sources:
            return f"❌ I couldn't find comprehensive information about '{query}'. Try rephrasing your question or being more specific."
        
        response = f"\n🤖 {self.name}'s Research Report: {query}\n"
        response += "=" * 60 + "\n\n"
        
        # Main answer from the best source
        main_source = sources[0]
        response += f"📋 SUMMARY:\n"
        
        if isinstance(main_source[1], dict):
            # Structured data (built-in knowledge)
            data = main_source[1]
            if 'definition' in data:
                response += f"{data['definition']}\n\n"
            
            for key, value in data.items():
                if key != 'definition':
                    response += f"• {key.replace('_', ' ').title()}: {value}\n"
        else:
            # Simple text
            response += f"{main_source[1]}\n"
        
        response += "\n" + "─" * 60 + "\n\n"
        
        # Additional sources
        if len(sources) > 1:
            response += "📚 ADDITIONAL SOURCES:\n\n"
            
            for i, (source_name, source_data) in enumerate(sources[1:], 1):
                response += f"{i}. {source_name}:\n"
                
                if isinstance(source_data, dict):
                    if 'title' in source_data:
                        response += f"   Title: {source_data['title']}\n"
                    if 'content' in source_data:
                        response += f"   Content: {source_data['content']}\n"
                    if 'url' in source_data:
                        response += f"   Source: {source_data['url']}\n"
                elif isinstance(source_data, list):
                    for item in source_data[:3]:
                        if isinstance(item, dict):
                            response += f"   • {item.get('title', 'No title')}\n"
                            response += f"     {item.get('snippet', 'No description')[:100]}...\n"
                        else:
                            response += f"   • {str(item)[:100]}...\n"
                else:
                    response += f"   {str(source_data)[:200]}...\n"
                
                response += "\n"
        
        response += "─" * 60 + "\n"
        response += f"🕒 Research completed at {datetime.now().strftime('%I:%M %p on %B %d, %Y')}\n"
        response += f"📊 Sources consulted: {len(sources)}\n"
        
        return response

def main():
    """Main interactive loop"""
    limbor = IntelligentLimbor()
    
    print("🤖 Intelligent Limbor AI - Comprehensive Research Assistant")
    print("=" * 60)
    print("Ask me anything and I'll provide detailed research with sources!")
    print("Type 'exit' to quit\n")
    
    # Sample questions
    samples = [
        "What is NPU?",
        "Explain artificial intelligence",
        "How does machine learning work?",
        "What is quantum computing?",
        "Tell me about Python programming",
        "Latest news about AI"
    ]
    
    print("💡 Try these sample questions:")
    for i, sample in enumerate(samples, 1):
        print(f"   {i}. {sample}")
    print()
    
    while True:
        try:
            question = input("🔍 Ask Limbor: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['exit', 'quit', 'bye', 'stop']:
                print(f"\n👋 {limbor.name} signing off! Thanks for using the research assistant!")
                break
            
            # Get comprehensive answer
            answer = limbor.get_comprehensive_answer(question)
            print(answer)
            print("\n" + "=" * 60 + "\n")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 {limbor.name} signing off!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with a different question.\n")

if __name__ == "__main__":
    main()