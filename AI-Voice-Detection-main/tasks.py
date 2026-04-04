# ============================================================
# VOXSENTINEL - CELERY TASKS
# Async audio processing and analysis tasks
# ============================================================

import os
import base64
import uuid
import tempfile
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from celery_config import celery_app
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import providers (same as app.py)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Load API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STT_PROVIDER = os.getenv("STT_PROVIDER", "groq")
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")

# Language codes mapping
LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "en": "en",
    "hi": "hi",
    "ta": "ta"
}


# ============================================================
# TASK 1: AUDIO TRANSCRIPTION (ASYNC)
# ============================================================
@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_audio_task(self, audio_base64: str, language: str, analysis_id: str) -> Dict[str, Any]:
    """
    Async task to process audio and return transcription.
    
    Args:
        audio_base64: Base64 encoded audio data
        language: Language code (English, Hindi, Tamil)
        analysis_id: Unique ID for tracking
        
    Returns:
        Dict with transcript and metadata
    """
    logger.info(f"🎵 [TASK] Starting audio transcription for {analysis_id}")
    
    try:
        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)
        logger.info(f"Decoded {len(audio_bytes)} bytes of audio")
        
        # Save to temp file
        temp_path = None
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        # Get language code
        lang_code = LANGUAGE_CODES.get(language, "en")
        
        # Transcribe based on provider
        transcript = ""
        
        if STT_PROVIDER == "groq" and GROQ_AVAILABLE and GROQ_API_KEY:
            transcript = _transcribe_with_groq(temp_path, lang_code)
        elif STT_PROVIDER == "openai" and OPENAI_AVAILABLE and OPENAI_API_KEY:
            transcript = _transcribe_with_openai(temp_path, lang_code)
        else:
            raise Exception("No STT provider available")
        
        # Clean up
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        
        logger.info(f"✅ [TASK] Transcription complete: {len(transcript)} chars")
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "transcript": transcript,
            "language": language,
            "lang_code": lang_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ [TASK] Transcription failed: {str(e)}")
        # Retry on failure
        raise self.retry(exc=e)


# ============================================================
# TASK 2: AI ANALYSIS (ASYNC)
# ============================================================
@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def analyze_transcript_task(self, transcript: str, language: str, analysis_id: str) -> Dict[str, Any]:
    """
    Async task to analyze transcript with AI.
    
    Args:
        transcript: Text transcript
        language: Language code
        analysis_id: Unique ID for tracking
        
    Returns:
        Dict with full analysis results
    """
    logger.info(f"🧠 [TASK] Starting AI analysis for {analysis_id}")
    
    try:
        # Build analysis prompt (enhanced SOP validation)
        prompt = _build_analysis_prompt(transcript, language)
        
        # Get AI analysis
        if AI_PROVIDER == "groq" and GROQ_AVAILABLE and GROQ_API_KEY:
            result = _analyze_with_groq(prompt)
        elif OPENAI_AVAILABLE and OPENAI_API_KEY:
            result = _analyze_with_openai(prompt)
        else:
            raise Exception("No AI provider available")
        
        logger.info(f"✅ [TASK] AI analysis complete for {analysis_id}")
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ [TASK] AI analysis failed: {str(e)}")
        raise self.retry(exc=e)


# ============================================================
# TASK 3: FULL PIPELINE (ASYNC)
# ============================================================
@celery_app.task(bind=True, max_retries=2)
def full_analysis_pipeline(self, audio_base64: str, language: str) -> Dict[str, Any]:
    """
    Complete async pipeline: Audio → Transcript → Analysis → Save
    
    This is the main task that chains all processing steps.
    """
    analysis_id = str(uuid.uuid4())
    logger.info(f"🚀 [PIPELINE] Starting full analysis: {analysis_id}")
    
    try:
        # Step 1: Transcription
        transcription_result = process_audio_task.apply(
            args=[audio_base64, language, analysis_id]
        ).get()
        
        if not transcription_result.get("success"):
            raise Exception("Transcription failed")
        
        transcript = transcription_result["transcript"]
        
        # Step 2: AI Analysis
        analysis_result = analyze_transcript_task.apply(
            args=[transcript, language, analysis_id]
        ).get()
        
        if not analysis_result.get("success"):
            raise Exception("AI analysis failed")
        
        # Step 3: Build final response
        analysis_data = analysis_result["analysis"]
        
        response = {
            "status": "success",
            "id": analysis_id,
            "language": language,
            "transcript": transcript,
            "summary": analysis_data.get("summary", ""),
            "sop_validation": analysis_data.get("sop_validation", {}),
            "analytics": analysis_data.get("analytics", {}),
            "keywords": analysis_data.get("keywords", []),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"✅ [PIPELINE] Complete for {analysis_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ [PIPELINE] Failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "analysis_id": analysis_id
        }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _transcribe_with_groq(audio_path: str, lang_code: str) -> str:
    """Transcribe audio using Groq Whisper"""
    client = Groq(api_key=GROQ_API_KEY)
    
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), audio_file.read()),
            model="whisper-large-v3",
            language=lang_code if lang_code != "auto" else None,
            response_format="verbose_json",
            temperature=0.0
        )
    
    return transcription.text


def _transcribe_with_openai(audio_path: str, lang_code: str) -> str:
    """Transcribe audio using OpenAI Whisper"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=lang_code if lang_code != "auto" else None,
            response_format="text"
        )
    
    return transcription


def _build_analysis_prompt(transcript: str, language: str) -> str:
    """Build enhanced analysis prompt with detailed SOP validation"""
    return f"""You are an expert call center quality analyst. Analyze this {language} call transcript and provide a detailed assessment.

TRANSCRIPT:
{transcript}

ANALYZE AND RESPOND IN JSON FORMAT WITH EXACTLY THIS STRUCTURE:

{{
    "summary": "2-3 sentence summary of the call",
    "sop_validation": {{
        "greeting": true/false,
        "identification": true/false,
        "problemStatement": true/false,
        "solutionOffering": true/false,
        "closing": true/false,
        "complianceScore": 0.0-1.0,
        "adherenceStatus": "FOLLOWED" or "NOT_FOLLOWED",
        "explanation": "Detailed explanation of compliance"
    }},
    "analytics": {{
        "paymentPreference": "EMI" | "FULL_PAYMENT" | "PARTIAL_PAYMENT" | "DOWN_PAYMENT" | "NONE",
        "rejectionReason": "HIGH_PRICE" | "NO_NEED" | "COMPETITOR" | "TIMING" | "OTHER" | "NONE",
        "sentiment": "Positive" | "Negative" | "Neutral"
    }},
    "keywords": ["keyword1", "keyword2", "keyword3", ...]
}}

SOP VALIDATION CRITERIA (Be strict):

1. GREETING (must include):
   - Welcome phrase (Hello, Welcome, Namaste, Vanakkam)
   - Company/brand name mentioned
   - Agent introduces themselves

2. IDENTIFICATION (must include):
   - Asks for customer name
   - Verifies account/phone/email/ID
   - Confirms they're speaking to right person

3. PROBLEM STATEMENT (must include):
   - Customer's issue clearly stated
   - Agent acknowledges the problem
   - Paraphrasing or confirmation of issue

4. SOLUTION OFFERING (must include):
   - At least one solution proposed
   - Options or alternatives given
   - Clear next steps explained

5. CLOSING (must include):
   - Summarizes resolution/action taken
   - Thanks customer for calling
   - Asks if anything else needed
   - Professional goodbye

PAYMENT PREFERENCE:
- EMI: Installments, monthly payments, equated payments
- FULL_PAYMENT: One-time, full amount, complete payment
- PARTIAL_PAYMENT: Part payment, partial amount
- DOWN_PAYMENT: Initial payment, advance, booking amount
- NONE: No payment discussed

REJECTION REASON (if customer rejected/refused):
- HIGH_PRICE: Too expensive, costly, budget issues
- NO_NEED: Not interested, don't need it
- COMPETITOR: Using another service/product
- TIMING: Bad timing, will consider later
- OTHER: Any other reason
- NONE: No rejection in call

Calculate complianceScore as: (number of TRUE fields out of 5) / 5
Set adherenceStatus to "FOLLOWED" if complianceScore >= 0.8, else "NOT_FOLLOWED"

Extract 5-10 relevant keywords from the conversation.

RESPOND ONLY WITH VALID JSON, NO OTHER TEXT."""


def _analyze_with_groq(prompt: str) -> Dict[str, Any]:
    """Analyze using Groq Llama"""
    import json
    
    client = Groq(api_key=GROQ_API_KEY)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a call center analytics AI. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=2000,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


def _analyze_with_openai(prompt: str) -> Dict[str, Any]:
    """Analyze using OpenAI GPT"""
    import json
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a call center analytics AI. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=2000,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
