# HG Resume Craft Backend

> This is important!


AI-powered resume builder backend with Gemini integration.

## Features

- 🤖 AI-powered resume parsing and generation
- 📄 PDF and DOCX file support
- 🎯 Job-specific resume optimization
- 🔧 Skills suggestion engine
- 📊 ATS-friendly content generation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the server:
```bash
# Using the startup script (recommended)
python start.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /api/resume/summary` - Generate resume summary
- `POST /api/resume/extract` - Extract data from resume file
- `POST /api/resume/optimize` - Optimize resume for job description
- `POST /api/resume/edit` - Edit resume data
- `POST /api/resume/skills/suggest` - Suggest relevant skills

## Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.
