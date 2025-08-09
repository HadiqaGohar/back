import os
import re
import io
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
import pdfplumber
from openai import AsyncOpenAI
import mammoth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="HG Resume Craft API",
    description="AI-powered resume builder backend with Gemini integration",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://your-vercel-app.vercel.app",
        "https://hg-resume-craft.vercel.app",
        "https://ehmt8mro7sonvp9cs5oblz.streamlit.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

# Initialize Gemini client
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Pydantic Models
class ResumeInput(BaseModel):
    education: List[str] = Field(..., description="List of education entries")
    skills: List[str] = Field(..., description="List of skills")
    
    @validator('education', 'skills')
    def validate_non_empty_lists(cls, v):
        if not v or all(not item.strip() for item in v):
            raise ValueError("List cannot be empty or contain only empty strings")
        return [item.strip() for item in v if item.strip()]

class ResumeData(BaseModel):
    name: Optional[str] = None
    tag: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    number: Optional[str] = None
    summary: Optional[str] = None
    websites: List[str] = []
    skills: List[str] = []
    education: List[str] = []
    experience: List[str] = []
    student: List[str] = []
    courses: List[str] = []
    internships: List[str] = []
    extracurriculars: List[str] = []
    hobbies: List[str] = []
    references: List[str] = []
    languages: List[str] = []

class JobDescriptionInput(BaseModel):
    job_description: str = Field(..., description="Job description text")
    resume_data: ResumeData = Field(..., description="Current resume data")

class OptimizationResponse(BaseModel):
    optimized_summary: str
    suggested_skills: List[str]
    keyword_matches: List[str]
    improvement_suggestions: List[str]

# Utility Functions
def clean_ai_response(response: str) -> str:
    """Clean AI response to ensure valid JSON"""
    response = response.strip()
    
    # Remove markdown code blocks
    if response.startswith("```json") and response.endswith("```"):
        response = response[7:-3].strip()
    elif response.startswith("```") and response.endswith("```"):
        response = response[3:-3].strip()
    
    # Ensure proper JSON structure
    if not response.startswith("{"):
        response = "{" + response
    if not response.endswith("}"):
        response = response + "}"
    
    return response

def validate_and_normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize extracted resume data"""
    required_fields = {
        "name": "",
        "tag": "",
        "email": "",
        "location": "",
        "number": "",
        "summary": "",
        "websites": [],
        "skills": [],
        "education": [],
        "experience": [],
        "student": [],
        "courses": [],
        "internships": [],
        "extracurriculars": [],
        "hobbies": [],
        "references": [],
        "languages": []
    }
    
    for field, default_value in required_fields.items():
        if field not in data:
            data[field] = default_value
        elif isinstance(default_value, list):
            if isinstance(data[field], str):
                # Split comma-separated values
                data[field] = [
                    item.strip() for item in data[field].split(",") 
                    if item.strip()
                ]
            elif not isinstance(data[field], list):
                data[field] = []
        elif isinstance(default_value, str) and not isinstance(data[field], str):
            data[field] = str(data[field]) if data[field] is not None else ""
    
    return data

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "HG Resume Craft API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Gemini connection
        test_response = await external_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        gemini_status = "connected"
    except Exception as e:
        logger.error(f"Gemini connection failed: {e}")
        gemini_status = "disconnected"
    
    return {
        "api_status": "healthy",
        "gemini_status": gemini_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/resume/summary")
async def generate_resume_summary(input_data: ResumeInput):
    """Generate AI-powered resume summary"""
    try:
        education_str = ", ".join(input_data.education)
        skills_str = ", ".join(input_data.skills)
        
        response = await external_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate a professional resume summary for a candidate with:
                    Education: {education_str}
                    Skills: {skills_str}
                    
                    Requirements:
                    - Keep it concise and professional (3-4 sentences)
                    - Make it ATS-friendly with relevant keywords
                    - Focus on value proposition and career highlights
                    - Use action-oriented language
                    
                    Return only the summary text without any formatting or extra text."""
                }
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content or ""
        logger.info(f"Generated summary for user with {len(input_data.skills)} skills")
        
        return {"summary": summary.strip()}
        
    except Exception as e:
        logger.error(f"Error generating resume summary: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate summary: {str(e)}"
        )

@app.post("/api/resume/extract")
async def extract_resume_data(file: UploadFile = File(...)):
    """Extract structured data from uploaded resume"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    extracted_text = ""
    
    try:
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith(".pdf"):
            pdf_file = io.BytesIO(content)
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    extracted_text += page_text + "\n"
                    
            if not extracted_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No text extracted from PDF. The file might be image-based or corrupted."
                )
                
        elif file.filename.lower().endswith(".docx"):
            docx_file = io.BytesIO(content)
            result = mammoth.extract_raw_text(docx_file)
            extracted_text = result.value
            
            if not extracted_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No text extracted from DOCX. The file might be empty or corrupted."
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only PDF and DOCX files are supported."
            )
        
        # Use Gemini to parse extracted text
        response = await external_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"""Parse the following resume text into structured JSON data. Extract these fields:

                    Required fields:
                    - name (string): Full name
                    - tag (string): Professional title or role
                    - email (string): Email address
                    - location (string): City, State or full address
                    - number (string): Phone number
                    - summary (string): Professional summary or objective
                    - websites (array): LinkedIn, portfolio, GitHub URLs
                    - skills (array): Technical and soft skills
                    - education (array): Degrees, institutions, graduation years
                    - experience (array): Job titles, companies, descriptions
                    - student (array): Student status like ['Current Student', 'Recent Graduate']
                    - courses (array): Relevant coursework or certifications
                    - internships (array): Internship experiences
                    - extracurriculars (array): Clubs, activities, volunteer work
                    - hobbies (array): Personal interests and hobbies
                    - references (array): Professional references
                    - languages (array): Spoken/written languages

                    Instructions:
                    - Return ONLY valid JSON without markdown formatting
                    - Use empty string "" for missing string fields
                    - Use empty array [] for missing array fields
                    - Split comma-separated values into array items
                    - Clean and normalize all data
                    - Extract email addresses, phone numbers, and URLs accurately

                    Resume text:
                    {extracted_text}
                    """
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        result = response.choices[0].message.content or "{}"
        result = clean_ai_response(result)
        
        try:
            structured_data = json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {result}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse AI response: {str(e)}"
            )
        
        # Validate and normalize data
        structured_data = validate_and_normalize_data(structured_data)
        
        logger.info(f"Successfully extracted data from {file.filename}")
        return structured_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting resume data: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract resume data: {str(e)}"
        )

@app.post("/api/resume/optimize", response_model=OptimizationResponse)
async def optimize_resume_for_job(input_data: JobDescriptionInput):
    """Optimize resume for specific job description"""
    try:
        response = await external_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this job description and current resume data to provide optimization suggestions:

                    Job Description:
                    {input_data.job_description}

                    Current Resume Data:
                    Name: {input_data.resume_data.name}
                    Current Summary: {input_data.resume_data.summary}
                    Skills: {', '.join(input_data.resume_data.skills)}
                    Experience: {', '.join(input_data.resume_data.experience)}

                    Provide optimization suggestions in this JSON format:
                    {{
                        "optimized_summary": "Rewritten summary tailored to the job",
                        "suggested_skills": ["skill1", "skill2", "skill3"],
                        "keyword_matches": ["keyword1", "keyword2"],
                        "improvement_suggestions": ["suggestion1", "suggestion2"]
                    }}

                    Focus on:
                    - ATS optimization with relevant keywords
                    - Highlighting matching skills and experience
                    - Suggesting missing but relevant skills
                    - Improving summary for better job alignment
                    """
                }
            ],
            max_tokens=800,
            temperature=0.5
        )
        
        result = response.choices[0].message.content or "{}"
        result = clean_ai_response(result)
        
        try:
            optimization_data = json.loads(result)
            return OptimizationResponse(**optimization_data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid optimization response: {result}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse optimization suggestions"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize resume: {str(e)}"
        )

@app.post("/api/resume/edit")
async def edit_resume_data(data: ResumeData):
    """Edit and validate resume data"""
    try:
        # Convert to dict and validate
        edited_data = data.dict(exclude_none=False)
        edited_data = validate_and_normalize_data(edited_data)
        
        logger.info("Resume data edited successfully")
        return edited_data
        
    except Exception as e:
        logger.error(f"Error editing resume data: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to edit resume data: {str(e)}"
        )

@app.post("/api/resume/skills/suggest")
async def suggest_skills(input_data: dict):
    """Suggest relevant skills based on profession/industry"""
    try:
        profession = input_data.get("profession", "")
        current_skills = input_data.get("current_skills", [])
        
        response = await external_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"""Suggest 10-15 relevant skills for a {profession} professional.
                    
                    Current skills: {', '.join(current_skills)}
                    
                    Return a JSON array of suggested skills that are:
                    - Industry-relevant and in-demand
                    - Not already in the current skills list
                    - Mix of technical and soft skills
                    - ATS-friendly keywords
                    
                    Format: ["skill1", "skill2", "skill3", ...]
                    """
                }
            ],
            max_tokens=300,
            temperature=0.6
        )
        
        result = response.choices[0].message.content or "[]"
        result = clean_ai_response(result)
        
        try:
            suggested_skills = json.loads(result)
            return {"suggested_skills": suggested_skills}
        except json.JSONDecodeError:
            return {"suggested_skills": []}
            
    except Exception as e:
        logger.error(f"Error suggesting skills: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to suggest skills: {str(e)}"
        )

@app.get("/api/templates")
async def get_templates():
    """Get available resume templates"""
    try:
        templates = [
            {
                "id": "modern",
                "name": "Modern Professional",
                "description": "Clean and modern design perfect for tech and creative industries",
                "preview": "/templates/modern-preview.png",
                "category": "professional"
            },
            {
                "id": "classic",
                "name": "Classic Business",
                "description": "Traditional format ideal for corporate and finance roles",
                "preview": "/templates/classic-preview.png",
                "category": "traditional"
            },
            {
                "id": "creative",
                "name": "Creative Designer",
                "description": "Bold and creative layout for designers and artists",
                "preview": "/templates/creative-preview.png",
                "category": "creative"
            },
            {
                "id": "minimal",
                "name": "Minimal Clean",
                "description": "Simple and elegant design that works for any industry",
                "preview": "/templates/minimal-preview.png",
                "category": "minimal"
            }
        ]
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch templates: {str(e)}"
        )

@app.post("/api/chatbot")
async def chatbot_endpoint(request: dict):
    """Enhanced AI-powered chatbot with web search and smart capabilities"""
    try:
        message = request.get("message", "")
        context = request.get("context", {})
        session_id = request.get("session_id", "default")
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Initialize chatbot service if not exists
        if not hasattr(app.state, "chatbot_service"):
            from chatbot_service import SmartChatbotService
            app.state.chatbot_service = SmartChatbotService(external_client)
        
        # Process message with enhanced chatbot
        result = await app.state.chatbot_service.process_message(
            message=message,
            context=context,
            session_id=session_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced chatbot: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot error: {str(e)}"
        )

@app.post("/api/chatbot/session/summary")
async def get_session_summary(request: dict):
    """Get conversation session summary"""
    try:
        session_id = request.get("session_id", "default")
        
        if not hasattr(app.state, "chatbot_service"):
            raise HTTPException(status_code=400, detail="Chatbot service not initialized")
        
        summary = app.state.chatbot_service.get_session_summary(session_id)
        return summary
        
    except Exception as e:
        logger.error(f"Error getting session summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session summary: {str(e)}"
        )

@app.post("/api/chatbot/session/clear")
async def clear_session(request: dict):
    """Clear conversation session"""
    try:
        session_id = request.get("session_id", "default")
        
        if not hasattr(app.state, "chatbot_service"):
            raise HTTPException(status_code=400, detail="Chatbot service not initialized")
        
        cleared = app.state.chatbot_service.clear_session(session_id)
        return {"cleared": cleared, "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear session: {str(e)}"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
