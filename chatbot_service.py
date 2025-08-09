import re
import json
import asyncio
import aiohttp
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from googlesearch import search
import validators
from langdetect import detect
import logging
from chatbot_config import (
    CHATBOT_CONFIG, GUARDRAILS, RESUME_KEYWORDS, SEARCH_TRIGGERS,
    SUPPORTED_LANGUAGES, QUICK_ACTIONS, RESPONSE_TEMPLATES,
    WEB_SCRAPING, RATE_LIMITS
)

logger = logging.getLogger(__name__)

class SmartChatbotService:
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.session_memory = {}
        self.rate_limits = {}
        
        # Load configuration
        self.config = CHATBOT_CONFIG
        self.guardrails = GUARDRAILS
        self.resume_keywords = RESUME_KEYWORDS
        self.search_triggers = SEARCH_TRIGGERS
        self.supported_languages = SUPPORTED_LANGUAGES
        self.response_templates = RESPONSE_TEMPLATES
        self.web_config = WEB_SCRAPING

    async def process_message(self, message: str, context: Dict[str, Any] = None, session_id: str = None) -> Dict[str, Any]:
        """Main method to process user messages with smart routing"""
        try:
            # Initialize session memory
            if session_id and session_id not in self.session_memory:
                self.session_memory[session_id] = []
            

            
            # Detect language
            try:
                detected_lang = detect(message)
            except:
                detected_lang = 'en'
            
            # Apply guardrails (moved after language detection)
            if self._check_guardrails(message):
                response_text = self.response_templates['guardrail'].get(detected_lang, 
                                                                       self.response_templates['guardrail']['en'])
                return {
                    "response": response_text,
                    "type": "guardrail_response",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Determine if web search is needed
            needs_search = self._needs_web_search(message)
            
            # Route to appropriate handler
            if needs_search:
                return await self._handle_web_search_query(message, context, session_id, detected_lang)
            elif self._is_resume_related(message):
                return await self._handle_resume_query(message, context, session_id, detected_lang)
            else:
                return await self._handle_general_query(message, context, session_id, detected_lang)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": "I encountered an error processing your request. Please try rephrasing your question.",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }

    def _check_guardrails(self, message: str) -> bool:
        """Check if message contains restricted content"""
        message_lower = message.lower()
        
        # Check restricted topics
        for topic in self.guardrails['restricted_topics']:
            if topic in message_lower:
                return True
        
        # Check warning keywords
        for keyword in self.guardrails['warning_keywords']:
            if keyword in message_lower:
                return True
                
        return False

    def _needs_web_search(self, message: str) -> bool:
        """Determine if the query needs web search"""
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in self.search_triggers)

    def _is_resume_related(self, message: str) -> bool:
        """Check if message is resume/career related"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.resume_keywords)

    async def _handle_web_search_query(self, message: str, context: Dict[str, Any], session_id: str, lang: str) -> Dict[str, Any]:
        """Handle queries that need web search"""
        try:
            # Extract search query
            search_query = self._extract_search_query(message)
            
            # Perform web search
            search_results = await self._perform_web_search(search_query)
            
            # Generate response with search results
            response = await self._generate_search_response(message, search_results, context, lang)
            
            # Store in session memory
            if session_id:
                self.session_memory[session_id].append({
                    "user": message,
                    "bot": response["response"],
                    "type": "web_search",
                    "timestamp": datetime.now().isoformat()
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in web search query: {str(e)}")
            return await self._handle_general_query(message, context, session_id, lang)

    async def _handle_resume_query(self, message: str, context: Dict[str, Any], session_id: str, lang: str) -> Dict[str, Any]:
        """Handle resume-specific queries"""
        try:
            # Get session context
            session_context = ""
            if session_id and session_id in self.session_memory:
                recent_messages = self.session_memory[session_id][-3:]  # Last 3 exchanges
                session_context = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in recent_messages])
            
            # Prepare context information
            context_info = ""
            if context and context.get("resume_data"):
                resume_data = context["resume_data"]
                context_info = f"""
                Current Resume Context:
                - Name: {resume_data.get('name', 'Not provided')}
                - Role: {resume_data.get('tag', 'Not provided')}
                - Skills: {', '.join(resume_data.get('skills', []))}
                - Experience: {', '.join(resume_data.get('experience', []))}
                - Education: {', '.join(resume_data.get('education', []))}
                """
            
            prompt = f"""You are an expert resume and career advisor. Help the user with their resume-related question.

            {context_info}
            
            Recent conversation context:
            {session_context}
            
            User's question: {message}
            
            Guidelines:
            - Provide specific, actionable advice
            - Use the resume context when relevant
            - Be encouraging and professional
            - If suggesting improvements, be specific
            - Keep responses concise but helpful
            - Respond in {lang} if not English
            """
            
            response = await self.gemini_client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content or "I'm here to help with your resume questions!"
            
            # Store in session memory
            if session_id:
                self.session_memory[session_id].append({
                    "user": message,
                    "bot": bot_response,
                    "type": "resume_advice",
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "response": bot_response,
                "type": "resume_advice",
                "suggestions": self._extract_suggestions(bot_response),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in resume query: {str(e)}")
            return {
                "response": "I'd be happy to help with your resume question. Could you please rephrase it?",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_general_query(self, message: str, context: Dict[str, Any], session_id: str, lang: str) -> Dict[str, Any]:
        """Handle general queries"""
        try:
            session_context = ""
            if session_id and session_id in self.session_memory:
                recent_messages = self.session_memory[session_id][-2:]
                session_context = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in recent_messages])
            
            prompt = f"""You are a helpful AI assistant focused on career and professional development. 
            
            Recent conversation:
            {session_context}
            
            User's question: {message}
            
            Guidelines:
            - Be helpful and informative
            - If the question is not career-related, gently guide back to resume/career topics
            - Provide practical advice when possible
            - Keep responses concise
            - Respond in {lang} if not English
            """
            
            response = await self.gemini_client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content or "I'm here to help! How can I assist you today?"
            
            # Store in session memory
            if session_id:
                self.session_memory[session_id].append({
                    "user": message,
                    "bot": bot_response,
                    "type": "general",
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "response": bot_response,
                "type": "general",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in general query: {str(e)}")
            return {
                "response": "I'm here to help! How can I assist you with your resume or career questions?",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }

    def _extract_search_query(self, message: str) -> str:
        """Extract search query from user message"""
        # Remove common search triggers and clean up
        query = message.lower()
        for trigger in self.search_triggers:
            query = query.replace(trigger, "").strip()
        
        # Remove question words
        question_words = ['what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'the']
        words = query.split()
        filtered_words = [word for word in words if word not in question_words]
        
        return " ".join(filtered_words).strip() or message

    async def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search and extract content"""
        try:
            search_results = []
            
            # Use Google search
            max_results = self.config['max_search_results']
            urls = list(search(query, num_results=max_results))
            
            # Extract content from URLs
            for url in urls[:max_results]:
                try:
                    content = await self._extract_web_content(url)
                    if content:
                        search_results.append({
                            "url": url,
                            "title": content.get("title", ""),
                            "content": content.get("content", "")[:500],  # Limit content
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.warning(f"Failed to extract content from {url}: {str(e)}")
                    continue
            
            return search_results
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return []

    async def _extract_web_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract content from a web page"""
        try:
            if not validators.url(url):
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get title
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else ""
                        
                        # Get main content
                        content = soup.get_text()
                        lines = (line.strip() for line in content.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        content_text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        return {
                            "title": title_text,
                            "content": content_text[:1000]  # Limit content
                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {str(e)}")
            return None

    async def _generate_search_response(self, original_query: str, search_results: List[Dict[str, Any]], context: Dict[str, Any], lang: str) -> Dict[str, Any]:
        """Generate response based on search results"""
        try:
            if not search_results:
                return {
                    "response": "I couldn't find current information on that topic. Let me help you with resume-related questions instead!",
                    "type": "search_failed",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare search context
            search_context = ""
            links = []
            for result in search_results:
                search_context += f"Source: {result['title']}\nContent: {result['content']}\n\n"
                links.append({"title": result['title'], "url": result['url']})
            
            prompt = f"""Based on the following search results, answer the user's question comprehensively.

            User's question: {original_query}
            
            Search results:
            {search_context}
            
            Guidelines:
            - Provide a comprehensive answer based on the search results
            - Be factual and cite information appropriately
            - If the information relates to careers/resumes, provide actionable advice
            - Keep the response informative but concise
            - Respond in {lang} if not English
            - Don't mention that you searched the web, just provide the information naturally
            """
            
            response = await self.gemini_client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.6
            )
            
            bot_response = response.choices[0].message.content or "Here's what I found based on current information..."
            
            return {
                "response": bot_response,
                "type": "web_search_response",
                "sources": links,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating search response: {str(e)}")
            return {
                "response": "I found some information but had trouble processing it. Could you try rephrasing your question?",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }

    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract actionable suggestions from bot response"""
        suggestions = []
        
        # Look for bullet points or numbered lists
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                suggestion = re.sub(r'^[•\-\*\d\.]\s*', '', line).strip()
                if suggestion and len(suggestion) > 10:
                    suggestions.append(suggestion)
        
        # If no structured suggestions found, look for sentences with action words
        if not suggestions:
            action_words = ['should', 'could', 'try', 'consider', 'add', 'include', 'improve', 'update']
            sentences = response.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(word in sentence.lower() for word in action_words) and len(sentence) > 20:
                    suggestions.append(sentence + '.')
        
        return suggestions[:3]  # Return max 3 suggestions

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of session conversation"""
        if session_id not in self.session_memory:
            return {"message": "No conversation history found"}
        
        messages = self.session_memory[session_id]
        return {
            "total_messages": len(messages),
            "conversation_start": messages[0]["timestamp"] if messages else None,
            "last_activity": messages[-1]["timestamp"] if messages else None,
            "topics_discussed": list(set([msg["type"] for msg in messages])),
            "recent_messages": messages[-5:]  # Last 5 exchanges
        }

    def clear_session(self, session_id: str) -> bool:
        """Clear session memory"""
        if session_id in self.session_memory:
            del self.session_memory[session_id]
            return True
        return False