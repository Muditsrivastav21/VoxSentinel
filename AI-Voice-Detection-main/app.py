"""
VoxSentinel - Call Center Compliance API
=========================================
AI-Powered Call Compliance Guardian

Features:
- Speech-to-Text (OpenAI Whisper)
- NLP Analysis (GPT-4)
- SOP Validation (5-stage compliance)
- Business Analytics
- Keyword Extraction
- Database Integration (Supabase)
- Rate Limiting & Security
- Structured Logging
"""

from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import base64
import tempfile
import os
import json
import warnings
import logging
import time
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
warnings.filterwarnings("ignore")

# ==========================
# LOGGING SETUP
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("voxsentinel")

# ==========================
# CONFIG
# ==========================
API_KEY = os.getenv("API_KEY", "sk_track3_987654321")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
STT_PROVIDER = os.getenv("STT_PROVIDER", "groq")  # groq, assemblyai, openai
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")    # groq, openai

# Validate API keys
if not GROQ_API_KEY and not OPENAI_API_KEY:
    logger.warning("Neither GROQ_API_KEY nor OPENAI_API_KEY found - API will not function properly")

# Initialize Groq client (for both STT and LLM)
groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
) if GROQ_API_KEY else None

# Initialize OpenAI client (legacy fallback)
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Database client (lazy initialization)
supabase = None

def get_supabase():
    """Lazy initialization of Supabase client"""
    global supabase
    if supabase is None and SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Supabase client initialized")
        except ImportError:
            logger.warning("Supabase package not installed - database features disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
    return supabase

SUPPORTED_LANGUAGES = ["Tamil", "Hindi", "English", "Spanish", "French", "German"]
LANGUAGE_CODES = {
    "Tamil": "ta", "Hindi": "hi", "English": "en", 
    "Spanish": "es", "French": "fr", "German": "de"
}

# Valid categories
PAYMENT_PREFERENCES = ["EMI", "FULL_PAYMENT", "PARTIAL_PAYMENT", "DOWN_PAYMENT"]
REJECTION_REASONS = ["HIGH_INTEREST", "BUDGET_CONSTRAINTS", "ALREADY_PAID", "NOT_INTERESTED", "NONE"]
SENTIMENTS = ["Positive", "Negative", "Neutral"]

# ==========================
# TRANSCRIPT CLEANING
# ==========================
import re
import unicodedata

def clean_transcript(text: str, language: str = "English") -> str:
    """
    Clean garbled/corrupted characters from transcript while preserving
    valid Tamil, Hindi, and English text.
    """
    if not text:
        return ""
    
    # Define valid Unicode ranges for supported languages
    # Tamil: \u0B80-\u0BFF
    # Hindi/Devanagari: \u0900-\u097F
    # English/Latin: \u0000-\u007F (basic) + \u00A0-\u00FF (extended)
    # Common punctuation and numbers
    
    # Pattern to match valid characters based on language
    valid_patterns = {
        "Tamil": r'[\u0B80-\u0BFF\u0020-\u007E\u00A0-\u00FF0-9\s.,!?:;\'\"\-\(\)\[\]@#$%&*+=<>/\\]',
        "Hindi": r'[\u0900-\u097F\u0020-\u007E\u00A0-\u00FF0-9\s.,!?:;\'\"\-\(\)\[\]@#$%&*+=<>/\\]',
        "English": r'[\u0020-\u007E\u00A0-\u00FF0-9\s.,!?:;\'\"\-\(\)\[\]@#$%&*+=<>/\\]',
    }
    
    # For mixed language (Tanglish/Hinglish), allow both native script and English
    if language == "Tamil":
        # Allow Tamil + English
        pattern = r'[\u0B80-\u0BFF\u0020-\u007E\u00A0-\u00FF0-9\s]'
    elif language == "Hindi":
        # Allow Hindi + English
        pattern = r'[\u0900-\u097F\u0020-\u007E\u00A0-\u00FF0-9\s]'
    else:
        # Default: allow common Latin characters
        pattern = r'[\u0020-\u007E\u00A0-\u00FF0-9\s]'
    
    # Remove characters that don't match the pattern
    cleaned_chars = []
    for char in text:
        if re.match(pattern, char):
            cleaned_chars.append(char)
        elif char in '.,!?:;\'"()-\n\t ':
            cleaned_chars.append(char)
    
    cleaned = ''.join(cleaned_chars)
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove gibberish patterns (random short character sequences)
    # Remove sequences of non-word characters
    cleaned = re.sub(r'[^\w\s.,!?:;\'\"\-\(\)]{3,}', ' ', cleaned)
    
    # Remove orphan single characters (except 'a', 'I', common single words)
    cleaned = re.sub(r'\s[^aAiI\s]\s', ' ', cleaned)
    
    # Fix multiple spaces
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    
    return cleaned.strip()

def format_transcript_with_speakers(transcript: str) -> str:
    """
    Attempt to format transcript with Agent/Customer labels
    based on conversation patterns.
    """
    if not transcript:
        return ""
    
    # If already formatted with Agent/Customer, return as-is
    if "Agent:" in transcript or "Customer:" in transcript:
        return transcript
    
    # Simple heuristic: Split by sentence-ending punctuation and alternate
    # This is a basic approach - the LLM analysis will do better formatting
    sentences = re.split(r'(?<=[.!?])\s+', transcript)
    
    if len(sentences) <= 2:
        return transcript
    
    # Don't auto-format if we can't reliably detect speakers
    return transcript

# ==========================
# IMPROVED SOP DETECTION
# ==========================
def detect_closing_patterns(transcript: str, summary: str = "") -> bool:
    """
    Detect if conversation has proper closing based on common patterns.
    """
    text = (transcript + " " + summary).lower()
    
    closing_patterns = [
        # English closing phrases
        r'\b(thank you|thanks|thank)\s*(so much|very much)?',
        r'\b(okay|ok)\s*(fine|sure|thanks|thank)',
        r'\b(have a (good|nice|great) day)',
        r'\b(goodbye|bye|bye bye|good bye)',
        r'\b(take care)',
        r'\b(will (call|contact|get back|reach|connect))',
        r'\b(we.ll (call|contact|get back))',
        r'\b(i.ll (send|share|forward|whatsapp))',
        r'\b(sure|okay|ok),?\s*(sir|ma.am|madam)?\.?\s*$',
        
        # Hindi closing phrases
        r'\b(dhanyavaad|dhanyawad|shukriya)',
        r'\b(acha|accha|achha)\s*(ji|theek|thik|ok)',
        r'\b(namaste)',
        
        # Tamil closing phrases
        r'\b(nandri|nanri)',
        r'\b(sari|saringa|saringala)',
        r'\b(poidtu varein|poi varein)',
        
        # Common call center closings
        r'(anything else|any (other|more) (questions?|queries?|help))',
        r'(is there anything|can i help)',
        r'(resume|cv|document).*(send|share|whatsapp|mail)',
    ]
    
    for pattern in closing_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

def detect_greeting_patterns(transcript: str) -> bool:
    """Detect greeting patterns in transcript"""
    text = transcript.lower()[:500]  # Check beginning of transcript
    
    greeting_patterns = [
        r'\b(hello|hi|hey|good (morning|afternoon|evening))',
        r'\b(vanakkam|namaste|namaskar)',
        r'\b(welcome to)',
        r'\b(speaking|this is)',
    ]
    
    for pattern in greeting_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def detect_solution_patterns(transcript: str, summary: str = "") -> bool:
    """Detect if solutions were offered"""
    text = (transcript + " " + summary).lower()
    
    solution_patterns = [
        r'\b(we (offer|provide|have|can))',
        r'\b(you can|you (could|should|might))',
        r'\b(option|options|choices?|plan)',
        r'\b(emi|installment|payment)',
        r'\b(course|training|program|certification)',
        r'\b(placement|job|career)',
        r'\b(support|help|assist)',
        r'\b(fee|price|cost|amount|rupees?|rs\.?)',
    ]
    
    for pattern in solution_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Rate limiting config
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# In-memory rate limiter (use Redis in production)
rate_limit_store = {}

# ==========================
# LIFESPAN (Startup/Shutdown)
# ==========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 VoxSentinel API starting up...")
    logger.info(f"📍 Environment: {ENVIRONMENT}")
    logger.info(f"🔑 OpenAI configured: {bool(OPENAI_API_KEY)}")
    logger.info(f"🗄️  Supabase configured: {bool(SUPABASE_URL and SUPABASE_KEY)}")
    yield
    # Shutdown
    logger.info("👋 VoxSentinel API shutting down...")

# ==========================
# APP INITIALIZATION
# ==========================
app = FastAPI(
    title="VoxSentinel API",
    description="""
## 🛡️ VoxSentinel - AI-Powered Call Compliance Guardian

Analyze call center recordings for compliance, sentiment, and business intelligence.

### Features
- **Speech-to-Text**: OpenAI Whisper for Hinglish/Tanglish transcription
- **SOP Validation**: 5-stage compliance scoring
- **Sentiment Analysis**: Positive, Negative, Neutral classification
- **Payment Classification**: EMI, Full Payment, Partial, Down Payment
- **Keyword Extraction**: Important topics from conversations

### Authentication
All endpoints require `x-api-key` header.
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Analysis", "description": "Call analysis endpoints"},
        {"name": "History", "description": "Call history endpoints"},
        {"name": "Stats", "description": "Statistics endpoints"},
    ]
)

# ==========================
# CORS MIDDLEWARE
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://voxsentinelmain.onrender.com",  # Frontend deployment
        "https://voxsentinel-frontend.onrender.com",  # Alternative frontend URL
    ],
    allow_origin_regex=r"https://.*\.(vercel|netlify|onrender)\.app",  # Wildcard support
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# RATE LIMITING
# ==========================
def check_rate_limit(client_id: str, max_requests: int = None, window_seconds: int = None) -> bool:
    """
    Simple in-memory rate limiter
    
    Args:
        client_id: Unique identifier for the client (e.g., API key)
        max_requests: Maximum requests allowed in window (default: RATE_LIMIT_REQUESTS)
        window_seconds: Time window in seconds (default: RATE_LIMIT_WINDOW)
    
    Returns:
        True if request is allowed, False if rate limited
    """
    max_req = max_requests or RATE_LIMIT_REQUESTS
    window = window_seconds or RATE_LIMIT_WINDOW
    now = time.time()
    window_start = now - window
    
    # Clean old entries and initialize if needed
    if client_id in rate_limit_store:
        if "count" in rate_limit_store[client_id]:
            # Legacy format - convert
            rate_limit_store[client_id] = []
    else:
        rate_limit_store[client_id] = {"timestamps": [], "count": 0}
    
    # Handle both list and dict formats
    if isinstance(rate_limit_store[client_id], list):
        rate_limit_store[client_id] = {"timestamps": rate_limit_store[client_id], "count": len(rate_limit_store[client_id])}
    
    # Clean old timestamps
    rate_limit_store[client_id]["timestamps"] = [
        t for t in rate_limit_store[client_id]["timestamps"] if t > window_start
    ]
    rate_limit_store[client_id]["count"] = len(rate_limit_store[client_id]["timestamps"])
    
    # Check limit
    if rate_limit_store[client_id]["count"] >= max_req:
        return False
    
    # Add current request
    rate_limit_store[client_id]["timestamps"].append(now)
    rate_limit_store[client_id]["count"] += 1
    return True

# ==========================
# CUSTOM ERROR HANDLER
# ==========================
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)} | Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ==========================
# REQUEST LOGGING MIDDLEWARE
# ==========================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log request
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(f"[{request_id}] Completed {response.status_code} in {duration}ms")
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response

# ==========================
# REQUEST/RESPONSE SCHEMAS
# ==========================
class CallAnalyticsRequest(BaseModel):
    """Request body for call analysis"""
    language: str = Field(default="en", description="Language code: 'en', 'hi', 'ta', etc.", example="en")
    audioFormat: Optional[str] = Field(default="mp3", description="Audio format", example="mp3")
    audioBase64: Optional[str] = Field(default=None, description="Base64-encoded audio file (camelCase)", min_length=100)
    audio_base64: Optional[str] = Field(default=None, description="Base64-encoded audio file (snake_case)", min_length=100)
    
    @validator('language')
    def validate_language(cls, v):
        # Map short codes to full names for backward compatibility
        language_map = {
            "en": "English", "hi": "Hindi", "ta": "Tamil", 
            "es": "Spanish", "fr": "French", "de": "German"
        }
        if v in language_map:
            return language_map[v]
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES)} or codes: en, hi, ta, es, fr, de")
        return v
    
    @validator('audioFormat', pre=True, always=True)
    def validate_format(cls, v):
        if v is None:
            return "mp3"
        return v.lower()
    
    @validator('audio_base64', pre=True, always=True)
    def normalize_audio_base64(cls, v, values):
        # If audio_base64 (snake_case) is provided, use it
        # This handles the frontend sending snake_case
        return v
    
    def get_audio_base64(self) -> str:
        """Get the audio base64 data from either field"""
        return self.audioBase64 or self.audio_base64 or ""
    
    @property
    def resolved_audio(self) -> str:
        """Resolve which audio field to use"""
        return self.audioBase64 or self.audio_base64 or ""

    class Config:
        json_schema_extra = {
            "example": {
                "language": "Tamil",
                "audioFormat": "mp3",
                "audioBase64": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAACQA..."
            }
        }

class SOPValidation(BaseModel):
    """SOP validation results"""
    greeting: bool = Field(..., description="Did agent greet properly?")
    identification: bool = Field(..., description="Did agent verify customer?")
    problemStatement: bool = Field(..., description="Was problem clearly stated?")
    solutionOffering: bool = Field(..., description="Were solutions offered?")
    closing: bool = Field(..., description="Was there proper closing?")
    complianceScore: float = Field(..., ge=0, le=1, description="Score from 0.0 to 1.0")
    adherenceStatus: str = Field(..., description="FOLLOWED or NOT_FOLLOWED")
    explanation: str = Field(..., description="Explanation of compliance")

class Analytics(BaseModel):
    """Business analytics results"""
    paymentPreference: str = Field(..., description="EMI, FULL_PAYMENT, PARTIAL_PAYMENT, or DOWN_PAYMENT")
    rejectionReason: str = Field(..., description="Reason for rejection or NONE")
    sentiment: str = Field(..., description="Positive, Negative, or Neutral")

class CallAnalyticsResponse(BaseModel):
    """Response from call analysis"""
    status: str = Field(..., description="success or error")
    id: Optional[str] = Field(None, description="Unique analysis ID")
    language: str
    transcript: str
    summary: str
    sop_validation: SOPValidation
    analytics: Analytics
    keywords: List[str]
    timestamp: Optional[str] = Field(None, description="ISO timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "language": "Tamil",
                "transcript": "Agent: Vanakkam, welcome to Guvi...",
                "summary": "Agent discussed Data Science course with customer.",
                "sop_validation": {
                    "greeting": True,
                    "identification": False,
                    "problemStatement": True,
                    "solutionOffering": True,
                    "closing": True,
                    "complianceScore": 0.8,
                    "adherenceStatus": "FOLLOWED",
                    "explanation": "Agent did not verify customer identity."
                },
                "analytics": {
                    "paymentPreference": "EMI",
                    "rejectionReason": "NONE",
                    "sentiment": "Positive"
                },
                "keywords": ["Data Science", "EMI options", "placement support"],
                "timestamp": "2024-01-15T14:32:00Z"
            }
        }

class CallHistoryItem(BaseModel):
    """Single call history item"""
    id: str
    language: str
    compliance_score: float
    adherence_status: str
    sentiment: str
    payment_preference: Optional[str] = "EMI"
    created_at: str

class CallHistoryResponse(BaseModel):
    """Response for call history"""
    status: str
    total: int
    page: int
    per_page: int
    calls: List[CallHistoryItem]

class StatsResponse(BaseModel):
    """Dashboard statistics"""
    status: str
    total_calls: int
    avg_compliance: float
    compliant_calls: int
    non_compliant_calls: int
    partial_calls: int
    sentiment_distribution: dict
    recent_calls: List[dict]
    calls_today: int
    calls_this_week: int

# ==========================
# HEALTH CHECK ENDPOINTS
# ==========================
@app.get("/", tags=["Health"])
def health_check():
    """Root health check endpoint"""
    return {
        "status": "success",
        "message": f"🛡️ VoxSentinel API is running (Groq-powered)",
        "version": "2.0.0",
        "providers": {
            "transcription": STT_PROVIDER,
            "ai_analysis": AI_PROVIDER
        },
        "supported_languages": SUPPORTED_LANGUAGES,
        "features": [
            f"Speech-to-Text ({STT_PROVIDER.upper()})",
            f"NLP Analysis ({AI_PROVIDER.upper()})",
            "SOP Validation",
            "Payment Classification",
            "Sentiment Analysis",
            "Keyword Extraction"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"])
def health():
    """Simple health check for load balancers"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "stt_provider": STT_PROVIDER,
            "ai_provider": AI_PROVIDER,
            "groq": "configured" if GROQ_API_KEY else "not_configured",
            "assemblyai": "configured" if ASSEMBLYAI_API_KEY else "not_configured",
            "openai": "configured" if OPENAI_API_KEY else "not_configured",
            "database": "configured" if (SUPABASE_URL and SUPABASE_KEY) else "not_configured"
        }
    }

@app.get("/api/config", tags=["Health"])
def get_config():
    """Get API configuration (public info only)"""
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "payment_types": PAYMENT_PREFERENCES,
        "rejection_reasons": REJECTION_REASONS,
        "sentiments": SENTIMENTS,
        "max_file_size_mb": 50,
        "rate_limit": {
            "requests": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW
        }
    }

# ==========================
# TRANSCRIPTION (WHISPER)
# ==========================
def transcribe_audio(audio_path: str, language: str) -> str:
    """Transcribe audio using Groq Whisper API (free) or AssemblyAI as fallback"""
    logger.info(f"Transcribing audio with {STT_PROVIDER}: {language}")
    start_time = time.time()
    
    # Try Groq first (FREE Whisper Large v3)
    if STT_PROVIDER == "groq" and groq_client:
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = groq_client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    language=LANGUAGE_CODES.get(language, "en"),
                    response_format="text"
                )
            
            duration = round(time.time() - start_time, 2)
            logger.info(f"Groq transcription completed in {duration}s, {len(transcript)} chars")
            return transcript.strip()
        except Exception as e:
            logger.error(f"Groq transcription error: {str(e)}")
            # Fall through to next provider
    
    # Try AssemblyAI
    if STT_PROVIDER == "assemblyai" and ASSEMBLYAI_API_KEY:
        try:
            import requests
            
            # Upload file
            headers = {"authorization": ASSEMBLYAI_API_KEY}
            with open(audio_path, "rb") as f:
                upload_response = requests.post(
                    "https://api.assemblyai.com/v2/upload",
                    headers=headers,
                    files={"file": f}
                )
            audio_url = upload_response.json()["upload_url"]
            
            # Request transcription
            transcript_response = requests.post(
                "https://api.assemblyai.com/v2/transcript",
                headers=headers,
                json={
                    "audio_url": audio_url,
                    "language_code": LANGUAGE_CODES.get(language, "en")
                }
            )
            transcript_id = transcript_response.json()["id"]
            
            # Poll for completion
            while True:
                result = requests.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers=headers
                ).json()
                
                if result["status"] == "completed":
                    duration = round(time.time() - start_time, 2)
                    logger.info(f"AssemblyAI transcription completed in {duration}s")
                    return result["text"]
                elif result["status"] == "error":
                    raise Exception(f"AssemblyAI error: {result.get('error')}")
                
                time.sleep(1)
        except Exception as e:
            logger.error(f"AssemblyAI transcription error: {str(e)}")
            # Fall through to OpenAI
    
    # Fallback to OpenAI (if available)
    if openai_client:
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=LANGUAGE_CODES.get(language, "en"),
                    response_format="text"
                )
            
            duration = round(time.time() - start_time, 2)
            logger.info(f"OpenAI transcription completed in {duration}s")
            return transcript.strip()
        except Exception as e:
            logger.error(f"OpenAI transcription error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    
    raise HTTPException(status_code=503, detail="No transcription service available")

# ==========================
# GPT ANALYSIS
# ==========================
def analyze_transcript(transcript: str, language: str) -> dict:
    """Analyze transcript using Groq (free LLM) or OpenAI GPT-4 as fallback"""
    logger.info(f"Analyzing transcript with {AI_PROVIDER}: {len(transcript)} chars")
    start_time = time.time()
    
    analysis_prompt = f"""You are an expert call center compliance analyst. Analyze this call transcript and provide a structured analysis.

TRANSCRIPT (Language: {language} - may contain Hinglish/Tanglish mixed language):
\"\"\"
{transcript}
\"\"\"

Analyze and return a JSON object with EXACTLY this structure:

{{
    "summary": "A concise 2-3 sentence summary of the conversation covering key points discussed",
    "sop_validation": {{
        "greeting": true/false (Did the agent greet the customer properly? Look for: Hello, Hi, Good morning/afternoon, Welcome, Namaste, Vanakkam),
        "identification": true/false (Did the agent identify/verify the customer by name or other details?),
        "problemStatement": true/false (Was the problem/purpose of call clearly stated or discussed?),
        "solutionOffering": true/false (Did the agent offer solutions, options, courses, services, or next steps?),
        "closing": true/false (Was there a proper closing? Look for: Thank you, Thanks, Bye, Will call/contact you, Send resume/details, Okay fine, Sure, Take care, or any polite ending),
        "complianceScore": 0.0-1.0 (Calculate as: number of true values / 5),
        "adherenceStatus": "FOLLOWED" or "NOT_FOLLOWED" (FOLLOWED if complianceScore >= 0.8, else NOT_FOLLOWED),
        "explanation": "Brief explanation of what was present/missing in the SOP"
    }},
    "analytics": {{
        "paymentPreference": "EMI" or "FULL_PAYMENT" or "PARTIAL_PAYMENT" or "DOWN_PAYMENT" (based on customer's payment intent, use most relevant),
        "rejectionReason": "HIGH_INTEREST" or "BUDGET_CONSTRAINTS" or "ALREADY_PAID" or "NOT_INTERESTED" or "NONE" (reason if sale/payment not completed),
        "sentiment": "Positive" or "Negative" or "Neutral" (overall customer sentiment - Positive if they agree to proceed, show interest, or conversation ends well)
    }},
    "keywords": ["keyword1", "keyword2", ...] (Extract 5-15 important keywords/phrases from the conversation - include product names, company names, amounts, key topics discussed)
}}

IMPORTANT RULES FOR CLOSING DETECTION:
- "Okay", "Okay sure", "Okay fine", "Thank you", "Thanks", "Sure" at the end of conversation = closing: true
- Customer agreeing to send resume/documents = closing: true  
- Agent saying they'll call back/WhatsApp = closing: true
- Any polite wrap-up of conversation = closing: true

IMPORTANT RULES FOR SENTIMENT:
- Customer agreeing to proceed, showing interest, or saying "okay sure" = Positive
- Customer expressing concerns but still engaged = Neutral
- Customer rejecting or expressing strong dissatisfaction = Negative

OTHER RULES:
1. complianceScore = (count of true values in greeting, identification, problemStatement, solutionOffering, closing) / 5
2. adherenceStatus is "FOLLOWED" only if complianceScore >= 0.8
3. If EMI options are discussed or mentioned, paymentPreference should be "EMI"
4. Keywords should be actual words/phrases from the transcript, not generic terms

Return ONLY the JSON object, no additional text."""

    # Try Groq first (FREE)
    if AI_PROVIDER == "groq" and groq_client:
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast and free!
                messages=[
                    {
                        "role": "system",
                        "content": "You are a call center compliance analyst. Always respond with valid JSON only. No markdown, no explanation, just the JSON object."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            analysis = json.loads(result_text)
            analysis = validate_and_fix_analysis(analysis, transcript)
            
            duration = round(time.time() - start_time, 2)
            logger.info(f"Groq analysis completed in {duration}s")
            return analysis
        except Exception as e:
            logger.error(f"Groq analysis error: {str(e)}")
            # Fall through to OpenAI
    
    # Fallback to OpenAI
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a call center compliance analyst. Always respond with valid JSON only. No markdown, no explanation, just the JSON object."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                analysis = json.loads(result_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from GPT response")
            
            # Validate and fix the response
            analysis = validate_and_fix_analysis(analysis, transcript)
            
            duration = round(time.time() - start_time, 2)
            logger.info(f"OpenAI analysis completed in {duration}s")
            
            return analysis
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
    
    raise HTTPException(status_code=503, detail="No AI analysis service available")

def validate_and_fix_analysis(analysis: dict, transcript: str = "") -> dict:
    """
    Validate and fix the GPT analysis to ensure correct format.
    Uses additional pattern detection to improve SOP validation accuracy.
    """
    
    # Ensure all required fields exist with defaults
    if "summary" not in analysis:
        analysis["summary"] = "Unable to generate summary"
    
    summary = analysis.get("summary", "")
    
    # Fix SOP validation
    if "sop_validation" not in analysis:
        analysis["sop_validation"] = {}
    
    sop = analysis["sop_validation"]
    sop_fields = ["greeting", "identification", "problemStatement", "solutionOffering", "closing"]
    
    for field in sop_fields:
        if field not in sop:
            sop[field] = False
        sop[field] = bool(sop[field])
    
    # ==========================
    # IMPROVED SOP DETECTION
    # ==========================
    
    # Use pattern detection to improve/override GPT's SOP detection
    if transcript:
        # Check for greeting - pattern overrides GPT
        greeting_detected = detect_greeting_patterns(transcript)
        if greeting_detected and not sop.get("greeting"):
            sop["greeting"] = True
            logger.debug("Pattern detection: Found greeting")
        
        # Check for closing - ALWAYS check patterns (common GPT miss)
        closing_detected = detect_closing_patterns(transcript, summary)
        if closing_detected:
            if not sop.get("closing"):
                sop["closing"] = True
                logger.debug("Pattern detection: Found closing")
        else:
            # If no patterns found, trust GPT (might have semantic closing)
            pass
        
        # Check for solution offering
        if not sop.get("solutionOffering"):
            if detect_solution_patterns(transcript, summary):
                sop["solutionOffering"] = True
                logger.debug("Pattern detection: Found solution offering")
    
    # ==========================
    # RECALCULATE COMPLIANCE SCORE
    # ==========================
    true_count = sum(1 for field in sop_fields if sop.get(field, False))
    
    # Calculate score: each stage is worth 0.2 (1/5)
    # Use proper decimal calculation
    sop["complianceScore"] = round(true_count * 0.2, 1)
    
    # If complianceScore is 0.99... due to floating point, round to 1.0
    if sop["complianceScore"] > 0.95:
        sop["complianceScore"] = 1.0
    
    # ==========================
    # FIX ADHERENCE STATUS
    # ==========================
    # FOLLOWED if 4 or 5 stages are true (80%+)
    sop["adherenceStatus"] = "FOLLOWED" if sop["complianceScore"] >= 0.8 else "NOT_FOLLOWED"
    
    # ==========================
    # GENERATE EXPLANATION
    # ==========================
    if "explanation" not in sop or not sop["explanation"]:
        missing = [f for f in sop_fields if not sop.get(f, False)]
        present = [f for f in sop_fields if sop.get(f, False)]
        
        if not missing:
            sop["explanation"] = "All SOP stages were followed correctly."
        elif len(missing) == 1:
            sop["explanation"] = f"The agent did not {missing[0].lower().replace('problemstatement', 'state the problem').replace('solutionoffering', 'offer solutions')}. All other stages were present."
        else:
            sop["explanation"] = f"Missing SOP stages: {', '.join(missing)}. Present stages: {', '.join(present)}."
    
    # ==========================
    # FIX ANALYTICS
    # ==========================
    if "analytics" not in analysis:
        analysis["analytics"] = {}
    
    analytics = analysis["analytics"]
    
    # Validate payment preference
    if analytics.get("paymentPreference") not in PAYMENT_PREFERENCES:
        analytics["paymentPreference"] = "EMI"  # Default
    
    # Validate rejection reason
    if analytics.get("rejectionReason") not in REJECTION_REASONS:
        analytics["rejectionReason"] = "NONE"
    
    # Validate sentiment
    valid_sentiment = analytics.get("sentiment", "").capitalize()
    if valid_sentiment not in SENTIMENTS:
        analytics["sentiment"] = "Neutral"
    else:
        analytics["sentiment"] = valid_sentiment
    
    # ==========================
    # FIX KEYWORDS
    # ==========================
    if "keywords" not in analysis or not isinstance(analysis["keywords"], list):
        analysis["keywords"] = []
    
    # Ensure keywords is a list of clean strings
    clean_keywords = []
    for k in analysis["keywords"]:
        if k and isinstance(k, str):
            # Clean the keyword
            clean_k = str(k).strip()
            if len(clean_k) > 1 and clean_k not in clean_keywords:
                clean_keywords.append(clean_k)
    
    analysis["keywords"] = clean_keywords[:15]
    
    return analysis

# ==========================
# DATABASE OPERATIONS
# ==========================
def save_analysis_to_db(analysis_data: dict) -> Optional[str]:
    """Save analysis results to Supabase database"""
    db = get_supabase()
    if not db:
        logger.debug("Database not configured, skipping save")
        return None
    
    try:
        # Map adherenceStatus to database-compatible values
        adherence = analysis_data["sop_validation"]["adherenceStatus"]
        compliance_score = analysis_data["sop_validation"]["complianceScore"]
        
        # Convert FOLLOWED/NOT_FOLLOWED to Compliant/Non-Compliant/Partial
        if adherence == "FOLLOWED" or compliance_score >= 0.8:
            db_adherence = "Compliant"
        elif compliance_score >= 0.6:
            db_adherence = "Partial"
        else:
            db_adherence = "Non-Compliant"
        
        record = {
            "language": analysis_data.get("language"),
            "transcript": analysis_data.get("transcript"),
            "summary": analysis_data.get("summary"),
            "sop_greeting": analysis_data["sop_validation"]["greeting"],
            "sop_identification": analysis_data["sop_validation"]["identification"],
            "sop_problem_statement": analysis_data["sop_validation"]["problemStatement"],
            "sop_solution_offering": analysis_data["sop_validation"]["solutionOffering"],
            "sop_closing": analysis_data["sop_validation"]["closing"],
            "compliance_score": compliance_score,
            "adherence_status": db_adherence,
            "sop_explanation": analysis_data["sop_validation"]["explanation"],
            "payment_preference": analysis_data["analytics"]["paymentPreference"],
            "rejection_reason": analysis_data["analytics"]["rejectionReason"],
            "sentiment": analysis_data["analytics"]["sentiment"],
            "keywords": analysis_data.get("keywords", []),
        }
        
        result = db.table("call_analyses").insert(record).execute()
        
        if result.data and len(result.data) > 0:
            record_id = result.data[0].get("id")
            logger.info(f"Saved analysis to database: {record_id}")
            return record_id
        logger.warning("Database insert returned no data")
        return None
    except Exception as e:
        logger.error(f"Database save error: {str(e)}")
        return None

def get_call_history(page: int = 1, per_page: int = 20) -> dict:
    """Get paginated call history from database"""
    db = get_supabase()
    if not db:
        return {"calls": [], "total": 0}
    
    try:
        offset = (page - 1) * per_page
        
        # Get total count
        count_result = db.table("call_analyses").select("id", count="exact").execute()
        total = count_result.count or 0
        
        # Get paginated results with adherence_status
        result = db.table("call_analyses")\
            .select("id, language, compliance_score, sentiment, payment_preference, adherence_status, created_at")\
            .order("created_at", desc=True)\
            .range(offset, offset + per_page - 1)\
            .execute()
        
        return {
            "calls": result.data or [],
            "total": total
        }
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        return {"calls": [], "total": 0}

def get_call_by_id(call_id: str) -> Optional[dict]:
    """Get single call analysis by ID"""
    db = get_supabase()
    if not db:
        return None
    
    try:
        result = db.table("call_analyses")\
            .select("*")\
            .eq("id", call_id)\
            .single()\
            .execute()
        return result.data
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        return None

def get_dashboard_stats() -> dict:
    """Get dashboard statistics with comprehensive metrics"""
    db = get_supabase()
    if not db:
        return {
            "total_calls": 0,
            "avg_compliance": 0.0,
            "compliant_calls": 0,
            "non_compliant_calls": 0,
            "partial_calls": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            "recent_calls": [],
            "calls_today": 0,
            "calls_this_week": 0
        }
    
    try:
        # Get all recent analyses
        result = db.table("call_analyses")\
            .select("id, language, compliance_score, sentiment, adherence_status, payment_preference, created_at")\
            .order("created_at", desc=True)\
            .limit(1000)\
            .execute()
        
        data = result.data or []
        
        if not data:
            return {
                "total_calls": 0,
                "avg_compliance": 0.0,
                "compliant_calls": 0,
                "non_compliant_calls": 0,
                "partial_calls": 0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "recent_calls": [],
                "calls_today": 0,
                "calls_this_week": 0
            }
        
        # Calculate stats
        total = len(data)
        avg_score = sum(d.get("compliance_score", 0) for d in data) / total if total > 0 else 0
        
        # Count by compliance status
        compliant = sum(1 for d in data if d.get("adherence_status") == "FOLLOWED")
        non_compliant = sum(1 for d in data if d.get("adherence_status") == "NOT_FOLLOWED")
        partial = total - compliant - non_compliant
        
        # Sentiment distribution (normalize keys to lowercase)
        sentiment_dist = {"positive": 0, "neutral": 0, "negative": 0}
        for d in data:
            s = str(d.get("sentiment", "Neutral")).lower()
            if s in sentiment_dist:
                sentiment_dist[s] += 1
        
        # Recent calls (top 5)
        recent_calls = []
        for call in data[:5]:
            recent_calls.append({
                "id": call.get("id", ""),
                "language": call.get("language", "Unknown"),
                "compliance_score": call.get("compliance_score", 0.0),
                "adherence_status": call.get("adherence_status", "UNKNOWN"),
                "sentiment": call.get("sentiment", "Neutral"),
                "created_at": call.get("created_at", "")
            })
        
        # Time-based counts
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        
        calls_today = sum(1 for d in data if d.get("created_at", "") >= today_start.isoformat())
        calls_this_week = sum(1 for d in data if d.get("created_at", "") >= week_start.isoformat())
        
        return {
            "total_calls": total,
            "avg_compliance": round(avg_score * 100, 1),  # Convert to percentage
            "compliant_calls": compliant,
            "non_compliant_calls": non_compliant,
            "partial_calls": partial,
            "sentiment_distribution": sentiment_dist,
            "recent_calls": recent_calls,
            "calls_today": calls_today,
            "calls_this_week": calls_this_week
        }
    except Exception as e:
        logger.error(f"Stats query error: {str(e)}")
        return {
            "total_calls": 0,
            "avg_compliance": 0.0,
            "compliant_calls": 0,
            "non_compliant_calls": 0,
            "partial_calls": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            "recent_calls": [],
            "calls_today": 0,
            "calls_this_week": 0
        }

# ==========================
# MAIN API ENDPOINT
# ==========================
@app.post("/api/call-analytics", response_model=CallAnalyticsResponse, tags=["Analysis"])
def analyze_call(
    request: CallAnalyticsRequest,
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    🎯 Main endpoint for call center compliance analysis.
    
    Performs multi-stage AI analysis:
    1. **Transcription**: Speech-to-Text using OpenAI Whisper
    2. **NLP Analysis**: GPT-4 powered content analysis
    3. **SOP Validation**: 5-stage compliance scoring
    4. **Business Analytics**: Payment preference & sentiment
    5. **Keyword Extraction**: Important topics extraction
    
    **Rate Limit**: 10 requests per minute per API key
    """
    
    # 🔐 API KEY VALIDATION
    if not x_api_key or x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # 🚦 RATE LIMITING
    if not check_rate_limit(x_api_key):
        logger.warning(f"Rate limit exceeded for key: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds"
        )
    
    # Generate unique ID for this analysis
    analysis_id = str(uuid.uuid4())
    logger.info(f"Starting analysis {analysis_id} for language: {request.language}")
    
    # 🔓 BASE64 DECODE - support both field names
    audio_data = request.resolved_audio
    if not audio_data:
        raise HTTPException(status_code=400, detail="No audio data provided. Send either 'audioBase64' or 'audio_base64'")
    
    try:
        audio_bytes = base64.b64decode(audio_data)
        logger.info(f"Decoded audio: {len(audio_bytes)} bytes")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Base64 audio encoding")
    
    # 💾 SAVE TEMP AUDIO FILE
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(audio_bytes)
            temp_path = tmp.name
        
        # 🎤 STEP 1: TRANSCRIPTION
        raw_transcript = transcribe_audio(temp_path, request.language)
        
        if not raw_transcript or len(raw_transcript.strip()) == 0:
            raise HTTPException(status_code=400, detail="Could not transcribe audio. Please ensure audio is clear and contains speech.")
        
        # 🧹 STEP 1.5: CLEAN TRANSCRIPT (remove garbled characters)
        transcript = clean_transcript(raw_transcript, request.language)
        logger.info(f"Transcript cleaned: {len(raw_transcript)} -> {len(transcript)} chars")
        
        # 🧠 STEP 2: GPT ANALYSIS
        analysis = analyze_transcript(transcript, request.language)
        
        # 📤 CONSTRUCT RESPONSE
        response = {
            "status": "success",
            "id": analysis_id,
            "language": request.language,
            "transcript": transcript,
            "summary": analysis.get("summary", ""),
            "sop_validation": {
                "greeting": analysis["sop_validation"]["greeting"],
                "identification": analysis["sop_validation"]["identification"],
                "problemStatement": analysis["sop_validation"]["problemStatement"],
                "solutionOffering": analysis["sop_validation"]["solutionOffering"],
                "closing": analysis["sop_validation"]["closing"],
                "complianceScore": analysis["sop_validation"]["complianceScore"],
                "adherenceStatus": analysis["sop_validation"]["adherenceStatus"],
                "explanation": analysis["sop_validation"]["explanation"]
            },
            "analytics": {
                "paymentPreference": analysis["analytics"]["paymentPreference"],
                "rejectionReason": analysis["analytics"]["rejectionReason"],
                "sentiment": analysis["analytics"]["sentiment"]
            },
            "keywords": analysis.get("keywords", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 💾 SAVE TO DATABASE (async, non-blocking)
        db_id = save_analysis_to_db(response)
        if db_id:
            response["id"] = db_id
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


# ==========================
# LEGACY ENDPOINT
# ==========================
@app.post("/api/voice-detection", tags=["Analysis"], include_in_schema=False)
def legacy_voice_detection(
    request: CallAnalyticsRequest,
    x_api_key: str = Header(None)
):
    """Legacy endpoint - redirects to new call-analytics endpoint"""
    return analyze_call(request, x_api_key)

# ==========================
# HISTORY ENDPOINTS
# ==========================
@app.get("/api/history", response_model=CallHistoryResponse, tags=["History"])
def get_history(
    page: int = 1,
    per_page: int = 20,
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    📋 Get paginated call history
    
    Returns list of analyzed calls with basic info.
    Use GET /api/history/{id} for full details.
    """
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    result = get_call_history(page, per_page)
    
    # Normalize the call data to ensure no None values and map adherence_status correctly
    normalized_calls = []
    for call in result.get("calls", []):
        adherence = call.get("adherence_status", "NOT_FOLLOWED")
        compliance_score = call.get("compliance_score", 0.0)
        
        # Map backend status to frontend status
        # If adherence_status is missing or wrong, infer from compliance_score
        if adherence == "FOLLOWED" or compliance_score >= 0.8:
            status = "Compliant"
        elif adherence == "NOT_FOLLOWED" or compliance_score < 0.6:
            status = "Non-Compliant"
        else:
            status = "Partial"
        
        normalized_call = {
            "id": call.get("id", ""),
            "language": call.get("language", "Unknown").upper(),
            "compliance_score": compliance_score,
            "adherence_status": status,  # Use frontend-compatible status
            "sentiment": call.get("sentiment", "Neutral"),
            "payment_preference": call.get("payment_preference") or "EMI",
            "created_at": call.get("created_at", "")
        }
        normalized_calls.append(normalized_call)
    
    return {
        "status": "success",
        "total": result["total"],
        "page": page,
        "per_page": per_page,
        "calls": normalized_calls
    }

@app.get("/api/history/{call_id}", tags=["History"])
def get_history_item(
    call_id: str,
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    📄 Get single call analysis by ID
    
    Returns full analysis details including transcript.
    """
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    call = get_call_by_id(call_id)
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return {
        "status": "success",
        "call": call
    }

@app.delete("/api/history/{call_id}", tags=["History"])
def delete_history_item(
    call_id: str,
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    🗑️ Delete a call analysis by ID
    """
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    db = get_supabase()
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        db.table("call_analyses").delete().eq("id", call_id).execute()
        logger.info(f"Deleted call analysis: {call_id}")
        return {"status": "success", "message": "Call deleted"}
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete call")

# ==========================
# STATS ENDPOINTS
# ==========================
@app.get("/api/stats", response_model=StatsResponse, tags=["Stats"])
def get_stats(
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    📊 Get dashboard statistics
    
    Returns aggregated metrics for the dashboard.
    """
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    stats = get_dashboard_stats()
    
    return {
        "status": "success",
        **stats
    }

# ==========================
# DEBUG ENDPOINTS
# ==========================
@app.get("/api/debug/db", tags=["Debug"])
def debug_database():
    """
    🔍 Debug endpoint to check database connectivity
    """
    db = get_supabase()
    
    result = {
        "supabase_url_configured": bool(SUPABASE_URL),
        "supabase_key_configured": bool(SUPABASE_KEY),
        "supabase_key_format": "JWT" if SUPABASE_KEY.startswith("eyJ") else "Invalid",
        "client_initialized": db is not None,
        "table_accessible": False,
        "record_count": 0,
        "error": None
    }
    
    if db:
        try:
            # Try to count records
            count_result = db.table("call_analyses").select("id", count="exact").execute()
            result["table_accessible"] = True
            result["record_count"] = count_result.count or 0
        except Exception as e:
            result["error"] = str(e)
    
    return result

# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=ENVIRONMENT == "development"
    )
