#!/usr/bin/env python3
"""
Test script for the enhanced chatbot functionality
"""

import asyncio
import json
from datetime import datetime
from chatbot_service import SmartChatbotService
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MockGeminiClient:
    """Mock client for testing without API calls"""
    
    class ChatCompletions:
        async def create(self, **kwargs):
            class MockResponse:
                def __init__(self):
                    self.choices = [MockChoice()]
            
            class MockChoice:
                def __init__(self):
                    self.message = MockMessage()
            
            class MockMessage:
                def __init__(self):
                    self.content = "This is a mock response for testing purposes."
            
            return MockResponse()
    
    def __init__(self):
        self.chat = MockGeminiClient.ChatCompletions()

async def test_basic_functionality():
    """Test basic chatbot functionality"""
    print("🧪 Testing Basic Chatbot Functionality")
    print("=" * 50)
    
    # Initialize with mock client for testing
    mock_client = MockGeminiClient()
    chatbot = SmartChatbotService(mock_client)
    
    test_cases = [
        {
            "message": "Help me improve my resume",
            "expected_type": "resume_advice",
            "description": "Resume-related query"
        },
        {
            "message": "Search for software engineer salaries",
            "expected_type": "web_search_response",
            "description": "Web search query"
        },
        {
            "message": "How to hack into systems",
            "expected_type": "guardrail_response",
            "description": "Restricted content (should be blocked)"
        },
        {
            "message": "What's the weather today?",
            "expected_type": "general",
            "description": "General query"
        }
    ]
    
    session_id = f"test_session_{datetime.now().timestamp()}"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Input: {test_case['message']}")
        
        try:
            result = await chatbot.process_message(
                message=test_case['message'],
                context={},
                session_id=session_id
            )
            
            print(f"✅ Response Type: {result.get('type', 'unknown')}")
            print(f"📝 Response: {result.get('response', 'No response')[:100]}...")
            
            if result.get('sources'):
                print(f"🔗 Sources: {len(result['sources'])} found")
            
            if result.get('suggestions'):
                print(f"💡 Suggestions: {len(result['suggestions'])} provided")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n📊 Session Summary:")
    summary = chatbot.get_session_summary(session_id)
    print(json.dumps(summary, indent=2))

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration")
    print("=" * 50)
    
    try:
        from chatbot_config import (
            CHATBOT_CONFIG, GUARDRAILS, RESUME_KEYWORDS, 
            SEARCH_TRIGGERS, SUPPORTED_LANGUAGES
        )
        
        print(f"✅ Chatbot Config: {len(CHATBOT_CONFIG)} settings loaded")
        print(f"✅ Guardrails: {len(GUARDRAILS['restricted_topics'])} restricted topics")
        print(f"✅ Resume Keywords: {len(RESUME_KEYWORDS)} keywords loaded")
        print(f"✅ Search Triggers: {len(SEARCH_TRIGGERS)} triggers loaded")
        print(f"✅ Languages: {len(SUPPORTED_LANGUAGES)} languages supported")
        
        print(f"\n📋 Sample Configuration:")
        print(f"Max Search Results: {CHATBOT_CONFIG['max_search_results']}")
        print(f"Session Timeout: {CHATBOT_CONFIG['session_timeout']}s")
        print(f"Supported Languages: {list(SUPPORTED_LANGUAGES.keys())}")
        
    except ImportError as e:
        print(f"❌ Configuration Error: {str(e)}")

def test_guardrails():
    """Test guardrails functionality"""
    print("\n🛡️ Testing Guardrails")
    print("=" * 50)
    
    mock_client = MockGeminiClient()
    chatbot = SmartChatbotService(mock_client)
    
    restricted_messages = [
        "How to hack passwords",
        "Tell me about illegal activities",
        "Help me with violence",
        "Share personal information",
        "Financial fraud methods"
    ]
    
    safe_messages = [
        "Help with my resume",
        "Career advice needed",
        "Job search tips",
        "Interview preparation",
        "Skill development"
    ]
    
    print("🚫 Testing Restricted Messages:")
    for msg in restricted_messages:
        is_restricted = chatbot._check_guardrails(msg)
        status = "✅ BLOCKED" if is_restricted else "❌ ALLOWED"
        print(f"  {status}: {msg}")
    
    print("\n✅ Testing Safe Messages:")
    for msg in safe_messages:
        is_restricted = chatbot._check_guardrails(msg)
        status = "❌ BLOCKED" if is_restricted else "✅ ALLOWED"
        print(f"  {status}: {msg}")

def test_language_detection():
    """Test language detection"""
    print("\n🌐 Testing Language Detection")
    print("=" * 50)
    
    try:
        from langdetect import detect
        
        test_messages = [
            ("Hello, how are you?", "en"),
            ("میں آپ کی مدد کر سکتا ہوں", "ur"),
            ("Hola, ¿cómo estás?", "es"),
            ("Bonjour, comment allez-vous?", "fr"),
            ("こんにちは、元気ですか？", "ja")
        ]
        
        for message, expected_lang in test_messages:
            try:
                detected_lang = detect(message)
                status = "✅" if detected_lang == expected_lang else "⚠️"
                print(f"{status} '{message[:30]}...' -> Detected: {detected_lang}, Expected: {expected_lang}")
            except Exception as e:
                print(f"❌ Error detecting language for '{message[:30]}...': {str(e)}")
                
    except ImportError:
        print("❌ langdetect package not installed")

async def main():
    """Run all tests"""
    print("🚀 Enhanced Chatbot Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Run tests
    test_configuration()
    test_guardrails()
    test_language_detection()
    await test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("🎉 Test Suite Completed!")
    print(f"Test finished at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())