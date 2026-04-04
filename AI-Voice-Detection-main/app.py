"""
VoxSentinel - Call Center Compliance API
=========================================
AI-Powered Call Compliance Guardian

Features:
- Speech-to-Text (Groq Whisper / OpenAI Whisper / AssemblyAI)
- NLP Analysis (Groq Llama / GPT-4)
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
API_KEY = os.getenv("API_KEY")  # Must be set in environment
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Provider selection
STT_PROVIDER = os.getenv("STT_PROVIDER", "groq").lower()  # groq, openai, assemblyai
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()    # groq, openai

# API Keys for different providers
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")

# Initialize clients based on provider
groq_client = None
openai_client = None

# Initialize Groq client
if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ Groq client initialized")
    except ImportError:
        logger.warning("⚠️ Groq package not installed. Run: pip install groq")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Groq: {e}")

# Initialize OpenAI client (fallback)
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI client initialized (fallback)")
    except Exception as e:
        logger.warning(f"⚠️ OpenAI client initialization failed: {e}")

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

# Demo mode responses (for testing without OpenAI)
DEMO_TRANSCRIPTS = {
    "en": "Hello, this is Sarah from VoxSentinel customer service. Thank you for calling. I understand you're having issues with your recent payment. Let me look into that for you. I can see your account and I'd like to offer you a flexible payment plan. Would that work for you? Great, I'll set that up right away. Is there anything else I can help you with today? Thank you for calling VoxSentinel, have a wonderful day!",
    "hi": "नमस्ते, मैं VoxSentinel ग्राहक सेवा से सारा बोल रही हूं। कॉल करने के लिए धन्यवाद। मैं समझती हूं कि आपको अपने हाल के भुगतान में समस्या हो रही है। मुझे इसे देखने दीजिए। मैं आपके खाते को देख सकती हूं और मैं आपको एक लचीली भुगतान योजना की पेशकश करना चाहूंगी।",
    "ta": "வணக்கம், நான் VoxSentinel வாடிக்கையாளர் சேவையில் இருந்து சாரா பேசுகிறேன். அழைப்புக்கு நன்றி. உங்கள் சமீபத்திய பணம் செலுத்துவதில் சிக்கல் இருப்பதை புரிந்துகொள்கிறேன்.",
}

DEMO_ANALYSIS = {
    "summary": "Customer called regarding payment issues. Agent Sarah greeted properly, identified herself, understood the problem, offered a flexible payment plan as solution, and closed the call professionally. Customer was satisfied with the resolution.",
    "sop_validation": {
        "greeting": True,
        "identification": True,
        "problemStatement": True,
        "solutionOffering": True,
        "closing": True,
        "complianceScore": 0.95,
        "adherenceStatus": "Compliant",
        "explanation": "The agent followed all SOP requirements: proper greeting, clear identification, understood customer's payment issue, offered flexible payment solution, and closed professionally."
    },
    "analytics": {
        "paymentPreference": "Flexible Payment Plan",
        "rejectionReason": "None",
        "sentiment": "Positive"
    },
    "keywords": ["payment", "flexible plan", "customer service", "account", "VoxSentinel"]
}

SUPPORTED_LANGUAGES = ["Tamil", "Hindi", "English", "Spanish", "French", "German"]
LANGUAGE_CODES = {
    "Tamil": "ta", "Hindi": "hi", "English": "en", 
    "Spanish": "es", "French": "fr", "German": "de"
}

# Valid categories
PAYMENT_PREFERENCES = ["EMI", "FULL_PAYMENT", "PARTIAL_PAYMENT", "DOWN_PAYMENT"]
REJECTION_REASONS = ["HIGH_INTEREST", "BUDGET_CONSTRAINTS", "ALREADY_PAID", "NOT_INTERESTED", "NONE"]
SENTIMENTS = ["Positive", "Negative", "Neutral"]

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
    logger.info(f"🎤 Speech-to-Text Provider: {STT_PROVIDER.upper()}")
    logger.info(f"🧠 AI Analysis Provider: {AI_PROVIDER.upper()}")
    logger.info(f"🔑 Groq configured: {bool(GROQ_API_KEY)}")
    logger.info(f"🗄️  Supabase configured: {bool(SUPABASE_URL and SUPABASE_KEY)}")
    if DEMO_MODE:
        logger.info("🎭 DEMO MODE ENABLED - Using mock responses")
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
        "https://*.vercel.app",
        "https://*.netlify.app",
    ],
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
    status: str = "success"
    total_calls: int
    avg_compliance: float
    compliant_calls: int
    non_compliant_calls: int
    partial_calls: int
    sentiment_distribution: dict
    recent_calls: List[dict]
    calls_today: int
    calls_this_week: int
    compliance_trend: List[dict]

# ==========================
# HEALTH CHECK ENDPOINTS
# ==========================
@app.get("/", tags=["Health"])
def health_check():
    """Root health check endpoint"""
    return {
        "status": "success",
        "message": "🛡️ VoxSentinel API is running",
        "version": "2.0.0",
        "providers": {
            "stt": STT_PROVIDER,
            "ai": AI_PROVIDER
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
        "providers": {
            "stt": STT_PROVIDER,
            "ai": AI_PROVIDER
        },
        "services": {
            "groq": "configured" if GROQ_API_KEY else "not_configured",
            "openai": "configured" if OPENAI_API_KEY else "not_configured",
            "assemblyai": "configured" if ASSEMBLYAI_API_KEY else "not_configured",
            "database": "configured" if (SUPABASE_URL and SUPABASE_KEY) else "not_configured"
        }
    }

@app.get("/api/config", tags=["Health"])
def get_config():
    """Get API configuration (public info only)"""
    return {
        "providers": {
            "stt": STT_PROVIDER,
            "ai": AI_PROVIDER
        },
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
    """
    Transcribe audio using the configured provider.
    Supports: Groq (whisper-large-v3), OpenAI (whisper-1), AssemblyAI
    """
    logger.info(f"Transcribing audio: {language} using {STT_PROVIDER.upper()}")
    start_time = time.time()
    
    try:
        # Use Groq (PRIMARY - FREE!)
        if STT_PROVIDER == "groq" and groq_client:
            with open(audio_path, "rb") as audio_file:
                transcript = groq_client.audio.transcriptions.create(
                    file=(audio_path, audio_file.read()),
                    model="whisper-large-v3",
                    language=LANGUAGE_CODES.get(language, "en"),
                    temperature=0,
                    response_format="text"
                )
            result = transcript.strip() if isinstance(transcript, str) else transcript.text.strip()
        
        # Use OpenAI (FALLBACK)
        elif STT_PROVIDER == "openai" and openai_client:
            with open(audio_path, "rb") as audio_file:
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=LANGUAGE_CODES.get(language, "en"),
                    response_format="text"
                )
            result = transcript.strip()
        
        # Use AssemblyAI (ASYNC POLLING)
        elif STT_PROVIDER == "assemblyai" and ASSEMBLYAI_API_KEY:
            result = transcribe_with_assemblyai(audio_path, language)
        
        else:
            # Auto-fallback: try Groq first, then OpenAI
            if groq_client:
                logger.info("Auto-fallback to Groq for transcription")
                with open(audio_path, "rb") as audio_file:
                    transcript = groq_client.audio.transcriptions.create(
                        file=(audio_path, audio_file.read()),
                        model="whisper-large-v3",
                        language=LANGUAGE_CODES.get(language, "en"),
                        temperature=0,
                        response_format="text"
                    )
                result = transcript.strip() if isinstance(transcript, str) else transcript.text.strip()
            elif openai_client:
                logger.info("Auto-fallback to OpenAI for transcription")
                with open(audio_path, "rb") as audio_file:
                    transcript = openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=LANGUAGE_CODES.get(language, "en"),
                        response_format="text"
                    )
                result = transcript.strip()
            else:
                raise HTTPException(status_code=503, detail="No transcription provider configured")
        
        duration = round(time.time() - start_time, 2)
        logger.info(f"Transcription completed in {duration}s, {len(result)} chars")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


def transcribe_with_assemblyai(audio_path: str, language: str) -> str:
    """Transcribe using AssemblyAI (async polling)"""
    import requests
    
    base_url = "https://api.assemblyai.com"
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    
    # Upload the audio file
    logger.info("Uploading audio to AssemblyAI...")
    with open(audio_path, "rb") as f:
        response = requests.post(f"{base_url}/v2/upload", headers=headers, data=f)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"AssemblyAI upload failed: {response.text}")
    
    audio_url = response.json()["upload_url"]
    
    # Start transcription
    data = {
        "audio_url": audio_url,
        "language_detection": True,
        "speech_models": ["universal-3-pro", "universal-2"]
    }
    response = requests.post(f"{base_url}/v2/transcript", json=data, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"AssemblyAI transcription start failed: {response.text}")
    
    transcript_id = response.json()['id']
    polling_endpoint = f"{base_url}/v2/transcript/{transcript_id}"
    
    # Poll for completion (max 5 minutes)
    logger.info(f"Polling AssemblyAI for transcription {transcript_id}...")
    max_polls = 100
    for i in range(max_polls):
        result = requests.get(polling_endpoint, headers=headers).json()
        
        if result['status'] == 'completed':
            return result['text']
        elif result['status'] == 'error':
            raise HTTPException(status_code=500, detail=f"AssemblyAI transcription failed: {result.get('error', 'Unknown error')}")
        
        time.sleep(3)
    
    raise HTTPException(status_code=500, detail="AssemblyAI transcription timeout")


# ==========================
# AI ANALYSIS (GROQ / GPT-4)
# ==========================
def analyze_transcript(transcript: str, language: str) -> dict:
    """
    Analyze transcript using the configured AI provider.
    Supports: Groq (llama-3.3-70b-versatile), OpenAI (GPT-4)
    
    Enhanced SOP validation for Hindi (Hinglish) and Tamil (Tanglish) calls.
    """
    logger.info(f"Analyzing transcript: {len(transcript)} chars using {AI_PROVIDER.upper()}")
    start_time = time.time()
    
    analysis_prompt = f"""You are an expert call center compliance analyst specializing in Indian language calls (Hindi/Hinglish, Tamil/Tanglish). Analyze this call transcript with strict SOP validation.

TRANSCRIPT (Language: {language} - contains Hindi/English or Tamil/English mixed language):
\"\"\"
{transcript}
\"\"\"

Analyze and return a JSON object with EXACTLY this structure:

{{
    "summary": "A concise 2-3 sentence summary of the conversation covering key points discussed, customer intent, and resolution",
    "sop_validation": {{
        "greeting": true/false,
        "identification": true/false,
        "problemStatement": true/false,
        "solutionOffering": true/false,
        "closing": true/false,
        "complianceScore": 0.0-1.0,
        "adherenceStatus": "FOLLOWED" or "NOT_FOLLOWED",
        "explanation": "Detailed explanation of what was present/missing in each SOP stage"
    }},
    "analytics": {{
        "paymentPreference": "EMI" or "FULL_PAYMENT" or "PARTIAL_PAYMENT" or "DOWN_PAYMENT" or "NONE",
        "rejectionReason": "HIGH_PRICE" or "NO_NEED" or "COMPETITOR" or "TIMING" or "BUDGET_CONSTRAINTS" or "NOT_INTERESTED" or "OTHER" or "NONE",
        "sentiment": "Positive" or "Negative" or "Neutral"
    }},
    "keywords": ["keyword1", "keyword2", ...up to 15 keywords]
}}

=== STRICT SOP VALIDATION CRITERIA (Be very precise) ===

1. GREETING (set true ONLY if):
   - Agent uses welcome phrase: "Hello", "Welcome", "Good morning/afternoon", "Namaste", "Namaskar", "Vanakkam"
   - OR mentions company/brand name
   - OR introduces themselves by name
   Hindi examples: "नमस्ते", "स्वागत है", "मैं [name] बोल रहा/रही हूं"
   Tamil examples: "வணக்கம்", "நான் [name] பேசுகிறேன்"

2. IDENTIFICATION (set true ONLY if):
   - Agent asks for OR verifies customer's name
   - OR asks for account number/phone number/email/ID
   - OR confirms customer identity in any way
   Hindi examples: "आपका नाम क्या है", "क्या मैं [name] जी से बात कर रहा हूं", "अकाउंट नंबर"
   Tamil examples: "உங்கள் பெயர் என்ன", "கணக்கு எண்"

3. PROBLEM STATEMENT (set true ONLY if):
   - Customer's issue/query is clearly stated or acknowledged
   - OR agent paraphrases the problem
   - OR there's a clear "reason for call" mentioned
   Hindi examples: "आपको क्या समस्या है", "मैं समझ गया", "आपका मुद्दा है"
   Tamil examples: "என்ன பிரச்சினை", "புரிந்துகொண்டேன்"

4. SOLUTION OFFERING (set true ONLY if):
   - Agent proposes at least one solution or option
   - OR offers alternatives/plans
   - OR explains next steps to resolve issue
   - OR provides information requested
   Hindi examples: "आप ये कर सकते हैं", "मैं आपको बताता/बताती हूं", "हमारे पास ये option है"
   Tamil examples: "இந்த வழி", "உங்களுக்கு இந்த option கொடுக்க முடியும்"

5. CLOSING (set true ONLY if):
   - Agent thanks the customer
   - OR asks if anything else is needed
   - OR gives professional goodbye
   - OR summarizes what was discussed/resolved
   Hindi examples: "धन्यवाद", "और कोई मदद", "शुभ दिन", "कोई और सवाल"
   Tamil examples: "நன்றி", "வேறு எதாவது உதவி", "நல்ல நாள்"

=== CALCULATION RULES ===
- complianceScore = (count of true values) / 5
- adherenceStatus = "FOLLOWED" if complianceScore >= 0.8, else "NOT_FOLLOWED"

=== PAYMENT PREFERENCE (detect from conversation) ===
- EMI: Installments, monthly payments, "EMI", "किस्त", "தவணை"
- FULL_PAYMENT: One-time, full amount, "पूरा भुगतान", "முழு பணம்"
- PARTIAL_PAYMENT: Part payment, "आंशिक भुगतान", "பகுதி பணம்"
- DOWN_PAYMENT: Initial/advance payment, "अग्रिम भुगतान", "முன்பணம்"
- NONE: No payment discussed

=== REJECTION REASON (if customer rejected/refused) ===
- HIGH_PRICE: Too expensive, costly
- NO_NEED: Not interested, don't need
- COMPETITOR: Using another service
- TIMING: Bad timing, will consider later
- BUDGET_CONSTRAINTS: Financial constraints
- NOT_INTERESTED: General disinterest
- OTHER: Other reasons
- NONE: No rejection in call

=== KEYWORDS ===
Extract 5-15 important keywords/phrases from the actual transcript:
- Include product/service names
- Include company/brand names
- Include payment amounts/plans discussed
- Include key topics and concerns

Return ONLY the JSON object, no additional text."""

    try:
        # Use Groq (PRIMARY - FREE!)
        if AI_PROVIDER == "groq" and groq_client:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
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
        
        # Use OpenAI (FALLBACK)
        elif AI_PROVIDER == "openai" and openai_client:
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
        
        else:
            # Auto-fallback
            if groq_client:
                logger.info("Auto-fallback to Groq for analysis")
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a call center compliance analyst. Always respond with valid JSON only."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                result_text = response.choices[0].message.content.strip()
            elif openai_client:
                logger.info("Auto-fallback to OpenAI for analysis")
                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a call center compliance analyst. Always respond with valid JSON only."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                result_text = response.choices[0].message.content.strip()
            else:
                raise HTTPException(status_code=503, detail="No AI analysis provider configured")
        
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
                raise ValueError("Could not parse JSON from AI response")
        
        # Validate and fix the response
        analysis = validate_and_fix_analysis(analysis)
        
        duration = round(time.time() - start_time, 2)
        logger.info(f"Analysis completed in {duration}s")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

def validate_and_fix_analysis(analysis: dict) -> dict:
    """Validate and fix the GPT analysis to ensure correct format"""
    
    # Ensure all required fields exist with defaults
    if "summary" not in analysis:
        analysis["summary"] = "Unable to generate summary"
    
    # Fix SOP validation
    if "sop_validation" not in analysis:
        analysis["sop_validation"] = {}
    
    sop = analysis["sop_validation"]
    sop_fields = ["greeting", "identification", "problemStatement", "solutionOffering", "closing"]
    
    for field in sop_fields:
        if field not in sop:
            sop[field] = False
        sop[field] = bool(sop[field])
    
    # Recalculate compliance score
    true_count = sum(1 for field in sop_fields if sop.get(field, False))
    sop["complianceScore"] = round(true_count / 5, 1)
    
    # Fix adherence status
    sop["adherenceStatus"] = "FOLLOWED" if sop["complianceScore"] >= 0.8 else "NOT_FOLLOWED"
    
    if "explanation" not in sop:
        missing = [f for f in sop_fields if not sop.get(f, False)]
        if missing:
            sop["explanation"] = f"Missing SOP stages: {', '.join(missing)}"
        else:
            sop["explanation"] = "All SOP stages were followed correctly"
    
    # Fix analytics
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
    if analytics.get("sentiment") not in SENTIMENTS:
        analytics["sentiment"] = "Neutral"
    
    # Fix keywords
    if "keywords" not in analysis or not isinstance(analysis["keywords"], list):
        analysis["keywords"] = []
    
    # Ensure keywords is a list of strings
    analysis["keywords"] = [str(k) for k in analysis["keywords"] if k][:15]
    
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
        # Convert adherence status to database format
        adherence = analysis_data["sop_validation"]["adherenceStatus"]
        if adherence == "FOLLOWED":
            db_adherence = "Compliant"
        elif adherence == "NOT_FOLLOWED":
            db_adherence = "Non-Compliant"
        else:
            db_adherence = "Partial"
        
        compliance_score = analysis_data["sop_validation"]["complianceScore"]
        if compliance_score >= 0.8:
            db_adherence = "Compliant"
        elif compliance_score >= 0.5:
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
        
        # Get paginated results with all needed fields
        result = db.table("call_analyses")\
            .select("id, language, compliance_score, adherence_status, sentiment, payment_preference, summary, created_at")\
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
    """Get dashboard statistics for frontend dashboard"""
    db = get_supabase()
    
    # Default empty response
    empty_response = {
        "total_calls": 0,
        "avg_compliance": 0.0,
        "compliant_calls": 0,
        "non_compliant_calls": 0,
        "partial_calls": 0,
        "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
        "recent_calls": [],
        "calls_today": 0,
        "calls_this_week": 0,
        "compliance_trend": []
    }
    
    if not db:
        return empty_response
    
    try:
        # Get all analyses for stats
        result = db.table("call_analyses")\
            .select("id, language, compliance_score, adherence_status, sentiment, payment_preference, created_at, summary")\
            .order("created_at", desc=True)\
            .limit(1000)\
            .execute()
        
        data = result.data or []
        
        if not data:
            return empty_response
        
        # Calculate stats
        total = len(data)
        avg_score = sum(float(d.get("compliance_score", 0) or 0) for d in data) / total if total > 0 else 0
        
        # Count by adherence status
        compliant = sum(1 for d in data if d.get("adherence_status") == "Compliant")
        non_compliant = sum(1 for d in data if d.get("adherence_status") == "Non-Compliant")
        partial = sum(1 for d in data if d.get("adherence_status") == "Partial")
        
        # Sentiment distribution (as percentages)
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for d in data:
            s = d.get("sentiment", "Neutral")
            if s in sentiment_counts:
                sentiment_counts[s] += 1
        
        sentiment_pct = {
            "positive": round((sentiment_counts["Positive"] / total) * 100) if total > 0 else 0,
            "neutral": round((sentiment_counts["Neutral"] / total) * 100) if total > 0 else 0,
            "negative": round((sentiment_counts["Negative"] / total) * 100) if total > 0 else 0
        }
        
        # Calls today and this week
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        
        calls_today = sum(1 for d in data if d.get("created_at") and 
                         datetime.fromisoformat(d["created_at"].replace("Z", "+00:00")).replace(tzinfo=None) >= today_start)
        calls_this_week = sum(1 for d in data if d.get("created_at") and 
                             datetime.fromisoformat(d["created_at"].replace("Z", "+00:00")).replace(tzinfo=None) >= week_start)
        
        # Recent calls for the table (top 10)
        recent_calls = []
        for d in data[:10]:
            recent_calls.append({
                "id": d.get("id", ""),
                "language": d.get("language", "en"),
                "compliance_score": float(d.get("compliance_score", 0) or 0),
                "adherence_status": d.get("adherence_status", "Non-Compliant"),
                "sentiment": d.get("sentiment", "Neutral"),
                "created_at": d.get("created_at", ""),
                "summary": d.get("summary", "")
            })
        
        return {
            "total_calls": total,
            "avg_compliance": round(avg_score, 2),
            "compliant_calls": compliant,
            "non_compliant_calls": non_compliant,
            "partial_calls": partial,
            "sentiment_distribution": sentiment_pct,
            "recent_calls": recent_calls,
            "calls_today": calls_today,
            "calls_this_week": calls_this_week,
            "compliance_trend": []
        }
    except Exception as e:
        logger.error(f"Stats query error: {str(e)}")
        return empty_response

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
        # 🎭 DEMO MODE - Return mock data without calling OpenAI
        if DEMO_MODE:
            logger.info(f"📍 DEMO MODE: Returning simulated analysis for {analysis_id}")
            import random
            import time
            
            # Simulate processing time
            time.sleep(2)
            
            # Get demo transcript based on language
            lang_code = LANGUAGE_CODES.get(request.language, "en")
            transcript = DEMO_TRANSCRIPTS.get(lang_code, DEMO_TRANSCRIPTS["en"])
            
            # Add some variation to demo responses
            compliance_variation = random.uniform(0.85, 1.0)
            
            response = {
                "status": "success",
                "id": analysis_id,
                "language": request.language,
                "transcript": transcript,
                "summary": DEMO_ANALYSIS["summary"],
                "sop_validation": {
                    **DEMO_ANALYSIS["sop_validation"],
                    "complianceScore": round(compliance_variation, 2)
                },
                "analytics": DEMO_ANALYSIS["analytics"],
                "keywords": DEMO_ANALYSIS["keywords"],
                "timestamp": datetime.utcnow().isoformat(),
                "demo_mode": True
            }
            
            # Save to database
            db_id = save_analysis_to_db(response)
            if db_id:
                response["id"] = db_id
            
            logger.info(f"Demo analysis {analysis_id} completed successfully")
            return response
        
        # 🎤 REAL MODE - Use OpenAI
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(audio_bytes)
            temp_path = tmp.name
        
        # 🎤 STEP 1: TRANSCRIPTION
        transcript = transcribe_audio(temp_path, request.language)
        
        if not transcript or len(transcript.strip()) == 0:
            raise HTTPException(status_code=400, detail="Could not transcribe audio. Please ensure audio is clear and contains speech.")
        
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
    x_api_key: Optional[str] = Header(None, description="API key (optional for read)")
):
    """
    📋 Get paginated call history
    
    Returns list of analyzed calls with basic info.
    Public endpoint - API key optional for read-only access.
    Use GET /api/history/{id} for full details.
    """
    result = get_call_history(page, per_page)
    
    # Normalize the call data to ensure no None values for required fields
    normalized_calls = []
    for call in result.get("calls", []):
        normalized_call = {
            "id": call.get("id", ""),
            "language": call.get("language", "Unknown"),
            "compliance_score": float(call.get("compliance_score", 0) or 0),
            "adherence_status": call.get("adherence_status", "Non-Compliant"),
            "sentiment": call.get("sentiment", "Neutral"),
            "payment_preference": call.get("payment_preference") or "EMI",
            "created_at": call.get("created_at", ""),
            "summary": call.get("summary", "")
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
    x_api_key: Optional[str] = Header(None, description="API key (optional for read)")
):
    """
    📄 Get single call analysis by ID
    
    Returns full analysis details including transcript.
    Public endpoint - API key optional for read-only access.
    """
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
# ASYNC ANALYSIS ENDPOINT (CELERY)
# ==========================
class AsyncAnalysisRequest(BaseModel):
    """Request for async analysis"""
    audioBase64: Optional[str] = Field(None, alias="audio_base64")
    audio_base64: Optional[str] = Field(None)
    language: str = "English"
    
    @property
    def resolved_audio(self) -> Optional[str]:
        return self.audioBase64 or self.audio_base64

class AsyncAnalysisResponse(BaseModel):
    """Response for async analysis submission"""
    status: str
    task_id: str
    message: str

class TaskStatusResponse(BaseModel):
    """Response for task status check"""
    status: str
    task_id: str
    task_status: str
    result: Optional[dict] = None

@app.post("/api/call-analytics/async", response_model=AsyncAnalysisResponse, tags=["Analysis"])
def analyze_call_async(
    request: AsyncAnalysisRequest,
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    🚀 Async endpoint for call center compliance analysis using Celery.
    
    This endpoint submits the analysis task to a Celery worker queue and
    returns immediately with a task_id. Use GET /api/tasks/{task_id} to
    check status and retrieve results.
    
    **For large audio files or batch processing.**
    """
    # Validate API key
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Rate limiting
    if not check_rate_limit(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Validate audio
    audio_data = request.resolved_audio
    if not audio_data:
        raise HTTPException(status_code=400, detail="No audio data provided")
    
    try:
        # Try to import Celery tasks
        try:
            from tasks import full_analysis_pipeline
            
            # Submit task to Celery
            task = full_analysis_pipeline.delay(audio_data, request.language)
            
            logger.info(f"Submitted async task: {task.id}")
            
            return {
                "status": "submitted",
                "task_id": task.id,
                "message": "Task submitted to processing queue. Use GET /api/tasks/{task_id} to check status."
            }
        except ImportError:
            # Celery not configured - fall back to synchronous processing
            logger.warning("Celery not available, falling back to sync processing")
            
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            return {
                "status": "processing",
                "task_id": task_id,
                "message": "Celery not configured. Use POST /api/call-analytics for synchronous processing."
            }
            
    except Exception as e:
        logger.error(f"Async submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")


@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse, tags=["Analysis"])
def get_task_status(
    task_id: str,
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    📋 Check status of an async analysis task.
    
    Returns task status and results when complete.
    """
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        from celery.result import AsyncResult
        from celery_config import celery_app
        
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready():
            result = task_result.result
            return {
                "status": "success",
                "task_id": task_id,
                "task_status": "completed",
                "result": result
            }
        else:
            return {
                "status": "success",
                "task_id": task_id,
                "task_status": task_result.status,
                "result": None
            }
    except ImportError:
        raise HTTPException(status_code=503, detail="Celery not configured")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking task: {str(e)}")


# ==========================
# PAYMENT STATISTICS ENDPOINT
# ==========================
class PaymentStatsResponse(BaseModel):
    """Payment statistics response"""
    status: str
    emi_count: int
    full_payment_count: int
    partial_payment_count: int
    down_payment_count: int
    none_count: int
    total: int

@app.get("/api/stats/payments", response_model=PaymentStatsResponse, tags=["Stats"])
def get_payment_stats(
    x_api_key: Optional[str] = Header(None, description="API key (optional for read)")
):
    """
    💰 Get payment preference statistics.
    
    Returns count of each payment preference type across all analyzed calls:
    - EMI (installments)
    - FULL_PAYMENT (one-time payment)
    - PARTIAL_PAYMENT (partial amount)
    - DOWN_PAYMENT (initial payment)
    - NONE (no payment discussed)
    """
    db = get_supabase()
    
    if not db:
        # Return empty stats if no database
        return {
            "status": "success",
            "emi_count": 0,
            "full_payment_count": 0,
            "partial_payment_count": 0,
            "down_payment_count": 0,
            "none_count": 0,
            "total": 0
        }
    
    try:
        # Get all payment preferences
        result = db.table("call_analyses").select("payment_preference").execute()
        
        # Count each type
        counts = {
            "emi": 0,
            "full_payment": 0,
            "partial_payment": 0,
            "down_payment": 0,
            "none": 0
        }
        
        for row in result.data or []:
            pref = (row.get("payment_preference") or "").upper()
            if "EMI" in pref:
                counts["emi"] += 1
            elif "FULL" in pref:
                counts["full_payment"] += 1
            elif "PARTIAL" in pref:
                counts["partial_payment"] += 1
            elif "DOWN" in pref:
                counts["down_payment"] += 1
            else:
                counts["none"] += 1
        
        total = sum(counts.values())
        
        return {
            "status": "success",
            "emi_count": counts["emi"],
            "full_payment_count": counts["full_payment"],
            "partial_payment_count": counts["partial_payment"],
            "down_payment_count": counts["down_payment"],
            "none_count": counts["none"],
            "total": total
        }
        
    except Exception as e:
        logger.error(f"Payment stats error: {str(e)}")
        return {
            "status": "success",
            "emi_count": 0,
            "full_payment_count": 0,
            "partial_payment_count": 0,
            "down_payment_count": 0,
            "none_count": 0,
            "total": 0
        }


# ==========================
# REJECTION STATISTICS ENDPOINT
# ==========================
class RejectionStatsResponse(BaseModel):
    """Rejection reason statistics response"""
    status: str
    high_price: int
    no_need: int
    competitor: int
    timing: int
    budget_constraints: int
    not_interested: int
    other: int
    none: int
    total: int

@app.get("/api/stats/rejections", response_model=RejectionStatsResponse, tags=["Stats"])
def get_rejection_stats(
    x_api_key: Optional[str] = Header(None, description="API key (optional for read)")
):
    """
    📊 Get rejection reason statistics.
    
    Returns count of each rejection reason across all analyzed calls.
    """
    db = get_supabase()
    
    if not db:
        return {
            "status": "success",
            "high_price": 0, "no_need": 0, "competitor": 0, "timing": 0,
            "budget_constraints": 0, "not_interested": 0, "other": 0, "none": 0,
            "total": 0
        }
    
    try:
        result = db.table("call_analyses").select("rejection_reason").execute()
        
        counts = {
            "high_price": 0, "no_need": 0, "competitor": 0, "timing": 0,
            "budget_constraints": 0, "not_interested": 0, "other": 0, "none": 0
        }
        
        for row in result.data or []:
            reason = (row.get("rejection_reason") or "NONE").upper()
            if "HIGH" in reason or "PRICE" in reason:
                counts["high_price"] += 1
            elif "NO_NEED" in reason or "NEED" in reason:
                counts["no_need"] += 1
            elif "COMPET" in reason:
                counts["competitor"] += 1
            elif "TIME" in reason or "LATER" in reason:
                counts["timing"] += 1
            elif "BUDGET" in reason:
                counts["budget_constraints"] += 1
            elif "NOT_INTERESTED" in reason or "INTEREST" in reason:
                counts["not_interested"] += 1
            elif reason == "NONE" or not reason:
                counts["none"] += 1
            else:
                counts["other"] += 1
        
        return {
            "status": "success",
            **counts,
            "total": sum(counts.values())
        }
        
    except Exception as e:
        logger.error(f"Rejection stats error: {str(e)}")
        return {
            "status": "success",
            "high_price": 0, "no_need": 0, "competitor": 0, "timing": 0,
            "budget_constraints": 0, "not_interested": 0, "other": 0, "none": 0,
            "total": 0
        }


# ==========================
# STATS ENDPOINTS
# ==========================
@app.get("/api/stats", response_model=StatsResponse, tags=["Stats"])
def get_stats(
    x_api_key: Optional[str] = Header(None, description="API key for authentication (optional for read)")
):
    """
    📊 Get dashboard statistics
    
    Returns aggregated metrics for the dashboard.
    Public endpoint - API key optional for read-only stats.
    """
    stats = get_dashboard_stats()
    
    return {
        "status": "success",
        **stats
    }

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
