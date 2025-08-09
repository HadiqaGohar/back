# 🤖 Enhanced Smart Chatbot

## Overview
This is a powerful, intelligent chatbot designed specifically for resume and career assistance. It features web search capabilities, multilingual support, smart guardrails, and contextual understanding.

## 🚀 Key Features

### 1. **Smart Web Search**
- Automatically detects when web search is needed
- Searches Google for current information
- Extracts and summarizes content from reliable sources
- Provides clickable source links

### 2. **Resume Intelligence**
- Context-aware resume advice
- Skill suggestions based on industry
- Job description optimization
- Interview preparation help

### 3. **Multilingual Support**
- Detects user language automatically
- Supports 10+ languages including English, Urdu, Hindi, Spanish, French
- Responds in user's preferred language

### 4. **Smart Guardrails**
- Filters inappropriate content
- Redirects off-topic conversations
- Maintains professional focus
- Protects user privacy

### 5. **Session Memory**
- Remembers conversation context
- Provides personalized responses
- Tracks user preferences
- Maintains conversation flow

## 🛠️ Technical Architecture

### Backend Components
```
backend/
├── main.py                 # FastAPI main application
├── chatbot_service.py      # Core chatbot logic
├── chatbot_config.py       # Configuration settings
└── install_dependencies.py # Dependency installer
```

### API Endpoints
- `POST /api/chatbot` - Main chat endpoint
- `POST /api/chatbot/session/summary` - Get session summary
- `POST /api/chatbot/session/clear` - Clear conversation

### Frontend Components
```
hg-resume-craft/src/app/components/
└── Chatbot.tsx            # Enhanced React component
```

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Chatbot Settings (chatbot_config.py)
```python
CHATBOT_CONFIG = {
    "max_search_results": 3,
    "max_session_memory": 50,
    "session_timeout": 3600,
    "max_response_tokens": 800,
    "temperature": 0.7,
    "web_search_timeout": 10,
}
```

## 🚦 Usage Examples

### Basic Resume Help
```
User: "Help me improve my resume summary"
Bot: "I'd be happy to help! Based on your current resume data, here are some suggestions..."
```

### Web Search Queries
```
User: "Search for current salary trends for software engineers"
Bot: "Here's what I found about current software engineer salaries..."
[Provides sources and links]
```

### Multilingual Support
```
User: "میرے ریزیومے کو بہتر بنانے میں مدد کریں"
Bot: "میں آپ کے ریزیومے کو بہتر بنانے میں خوشی سے مدد کروں گا..."
```

## 🛡️ Guardrails & Safety

### Restricted Topics
- Illegal activities
- Harmful content
- Personal information
- Financial details
- Medical/Legal advice

### Automatic Redirects
The chatbot automatically redirects conversations back to resume and career topics when users ask about unrelated subjects.

## 📊 Features Breakdown

### 1. **Context Detection**
- Automatically identifies resume-related queries
- Detects when web search is needed
- Understands user intent and context

### 2. **Smart Responses**
- Provides actionable suggestions
- Includes quick action buttons
- Shows relevant sources and links
- Offers follow-up questions

### 3. **Enhanced UI**
- Modern, responsive design
- Loading indicators
- Message formatting
- Source link integration
- Quick action buttons

### 4. **Session Management**
- Unique session IDs
- Conversation persistence
- Memory cleanup
- Session summaries

## 🔍 Web Search Capabilities

### Supported Search Types
- Company information
- Salary trends
- Industry news
- Skill requirements
- Interview questions
- Career advice

### Source Filtering
- Prioritizes reliable domains
- Filters content quality
- Provides source attribution
- Limits content length

## 🌐 Multilingual Features

### Language Detection
- Automatic language detection
- Fallback to English
- Context-aware responses

### Supported Languages
- English (en)
- Urdu (ur)
- Hindi (hi)
- Spanish (es)
- French (fr)
- German (de)
- Arabic (ar)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
python install_dependencies.py
```

### 2. Set Environment Variables
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 3. Start Backend
```bash
python main.py
```

### 4. Start Frontend
```bash
cd hg-resume-craft
npm run dev
```

## 📈 Performance Features

### Rate Limiting
- 30 requests per minute
- 500 requests per hour
- 50 web searches per hour

### Caching
- Session memory caching
- Response optimization
- Content length limits

### Error Handling
- Graceful error recovery
- Fallback responses
- Connection retry logic

## 🔧 Customization

### Adding New Languages
1. Update `SUPPORTED_LANGUAGES` in config
2. Add response templates
3. Test language detection

### Modifying Guardrails
1. Update `GUARDRAILS` configuration
2. Add new restricted topics
3. Customize redirect messages

### Extending Search Capabilities
1. Add new search triggers
2. Update domain whitelist
3. Modify content extraction

## 🐛 Troubleshooting

### Common Issues
1. **Web search not working**: Check internet connection and Google search limits
2. **Language detection fails**: Ensure langdetect package is installed
3. **Session memory issues**: Check session timeout settings
4. **API rate limits**: Implement proper rate limiting

### Debug Mode
Enable detailed logging by setting log level to DEBUG in main.py

## 📝 API Documentation

### Chat Request Format
```json
{
  "message": "Your question here",
  "context": {
    "resume_data": {...}
  },
  "session_id": "unique_session_id"
}
```

### Chat Response Format
```json
{
  "response": "Bot response text",
  "type": "response_type",
  "sources": [
    {
      "title": "Source title",
      "url": "https://example.com"
    }
  ],
  "suggestions": ["suggestion1", "suggestion2"],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the configuration options
3. Check the API documentation
4. Create an issue on GitHub

---

**Made with ❤️ for better resume building and career development**