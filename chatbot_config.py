"""
Enhanced Chatbot Configuration
Smart chatbot with web search, guardrails, and multilingual support
"""

# Chatbot Settings
CHATBOT_CONFIG = {
    "max_search_results": 3,
    "max_session_memory": 50,  # Maximum messages to keep in session
    "session_timeout": 3600,   # Session timeout in seconds (1 hour)
    "max_response_tokens": 800,
    "temperature": 0.7,
    "web_search_timeout": 10,  # Timeout for web requests in seconds
}

# Guardrails Configuration
GUARDRAILS = {
    "restricted_topics": [
        "illegal activities", "harmful content", "violence", "hate speech",
        "discrimination", "personal information", "private data", "passwords",
        "financial details", "medical advice", "legal advice", "adult content"
    ],
    
    "warning_keywords": [
        "hack", "crack", "pirate", "steal", "fraud", "scam", "illegal",
        "drugs", "weapons", "violence", "suicide", "self-harm"
    ],
    
    "redirect_message": "I'm designed to help with resume and career-related questions. Let's keep our conversation focused on helping you build a better professional profile!"
}

# Resume Keywords for Context Detection
RESUME_KEYWORDS = [
    "resume", "cv", "curriculum vitae", "job", "career", "skills", "experience",
    "education", "interview", "application", "hiring", "employment", "work",
    "professional", "qualification", "achievement", "accomplishment", "portfolio",
    "linkedin", "networking", "salary", "promotion", "manager", "leadership",
    "teamwork", "project", "certification", "training", "internship"
]

# Web Search Triggers
SEARCH_TRIGGERS = [
    "search for", "find information", "look up", "what is", "who is",
    "latest news", "current", "recent", "trending", "company info",
    "salary", "market rate", "industry trends", "job market", "hiring trends",
    "company culture", "interview questions", "skill requirements",
    "certification requirements", "course recommendations"
]

# Language Support
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ur": "Urdu", 
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ar": "Arabic",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean"
}

# Quick Action Templates
QUICK_ACTIONS = {
    "resume_improvement": [
        "Help me improve my resume summary",
        "What skills should I add to my resume?",
        "How can I make my experience section better?",
        "Review my education section",
        "Suggest improvements for my resume format"
    ],
    
    "job_search": [
        "Search for current salary trends in my field",
        "Find information about company culture",
        "What are the latest hiring trends?",
        "Help me prepare for interviews",
        "Find job requirements for my target role"
    ],
    
    "career_advice": [
        "How to write better job descriptions?",
        "Career transition advice",
        "Professional networking tips",
        "How to negotiate salary?",
        "Building a personal brand"
    ],
    
    "industry_research": [
        "Find information about my industry",
        "Latest technology trends",
        "Skills in demand for my field",
        "Professional development opportunities",
        "Industry certifications worth pursuing"
    ]
}

# Response Templates
RESPONSE_TEMPLATES = {
    "welcome": {
        "en": "Hi! I'm your smart resume assistant. I can help you improve your resume, search for current industry information, and answer career questions. How can I help you today?",
        "ur": "سلام! میں آپ کا ذہین ریزیومے اسسٹنٹ ہوں۔ میں آپ کے ریزیومے کو بہتر بنانے، موجودہ انڈسٹری کی معلومات تلاش کرنے، اور کیریئر کے سوالات کا جواب دینے میں مدد کر سکتا ہوں۔ آج میں آپ کی کیسے مدد کر سکتا ہوں؟"
    },
    
    "guardrail": {
        "en": "I'm designed to help with resume and career-related questions. Let's keep our conversation focused on helping you build a better professional profile!",
        "ur": "میں ریزیومے اور کیریئر سے متعلق سوالات میں مدد کے لیے بنایا گیا ہوں۔ آئیے اپنی گفتگو کو آپ کے بہتر پیشہ ورانہ پروفائل بنانے پر مرکوز رکھتے ہیں!"
    },
    
    "search_failed": {
        "en": "I couldn't find current information on that topic. Let me help you with resume-related questions instead!",
        "ur": "میں اس موضوع پر موجودہ معلومات نہیں مل سکیں۔ اس کے بجائے میں آپ کو ریزیومے سے متعلق سوالات میں مدد کرتا ہوں!"
    },
    
    "error": {
        "en": "I encountered an error processing your request. Please try rephrasing your question.",
        "ur": "آپ کی درخواست پر عمل کرتے وقت مجھے خرابی کا سامنا ہوا۔ براہ کرم اپنا سوال دوبارہ لکھیں۔"
    }
}

# Web Scraping Settings
WEB_SCRAPING = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "timeout": 10,
    "max_content_length": 1000,
    "allowed_domains": [
        "linkedin.com", "indeed.com", "glassdoor.com", "monster.com",
        "careerbuilder.com", "ziprecruiter.com", "stackoverflow.com",
        "github.com", "medium.com", "forbes.com", "harvard.edu",
        "coursera.org", "udemy.com", "edx.org", "wikipedia.org"
    ]
}

# Rate Limiting
RATE_LIMITS = {
    "requests_per_minute": 30,
    "requests_per_hour": 500,
    "web_searches_per_hour": 50
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_conversations": True,
    "log_web_searches": True,
    "log_errors": True,
    "retention_days": 30
}