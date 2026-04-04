# Call Center Compliance API - VoxSentinel

> **Live URL:** https://voxsentinel.onrender.com  
> **API Key:** `sk_track3_987654321`  
> **Frontend Dashboard:** https://voxsentinelmain.onrender.com

## 📝 Description

An intelligent call center analytics system that processes voice recordings in **Hindi (Hinglish)** and **Tamil (Tanglish)**, extracts text using speech-to-text, validates calls against standard operating procedures (SOP), and categorizes payment preferences.

### Strategy & Approach

The system uses a **multi-stage AI pipeline**:
1. **Audio Ingestion** - Accept base64-encoded MP3/WAV audio via REST API
2. **Speech-to-Text** - Groq Whisper Large v3 for accurate multilingual transcription
3. **Transcript Cleaning** - Remove garbled characters while preserving Tamil/Hindi/English
4. **AI Analysis** - Groq Llama 3.3 70B for structured JSON analysis with SOP validation
5. **Pattern Detection** - Additional regex-based detection for greetings, closings, solutions
6. **Database Storage** - Supabase PostgreSQL for call history and analytics dashboard

## 📋 Features

| Feature | Description | Status |
|---------|-------------|--------|
| Voice-to-Text | Extract text from Hindi & Tamil calls | ✅ |
| Text Summarization | AI-powered summary of call content | ✅ |
| SOP Validation | Validate against 5-step compliance framework | ✅ |
| Payment Categorization | EMI, Full, Partial, Down Payment | ✅ |
| Rejection Analysis | Extract and categorize rejection reasons | ✅ |
| Sentiment Analysis | Positive, Neutral, Negative classification | ✅ |
| Keyword Extraction | Key topics and entities from conversations | ✅ |
| Real-time Dashboard | Visual analytics with call history | ✅ |

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI (Python 3.11) |
| **Speech-to-Text** | Groq Whisper Large v3 (FREE, unlimited) |
| **LLM Analysis** | Groq Llama 3.3 70B Versatile |
| **Database** | Supabase (PostgreSQL) |
| **Async Tasks** | Celery (optional, for batch processing) |
| **Frontend** | React + Vite + TailwindCSS + shadcn/ui |
| **Deployment** | Render.com (Backend + Frontend) |
| **Server** | Uvicorn ASGI |

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd AI-Voice-Detection-main

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your keys:
# GROQ_API_KEY=your_groq_api_key
# API_KEY=your_secure_api_key
```

### 3. Run Locally

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/

# Test with audio file
python test_client.py test.mp3 Tamil
```

## 📡 API Documentation

### Authentication

All requests must include an API key in the header:
```
x-api-key: YOUR_API_KEY
```

### Endpoint

**POST** `/api/call-analytics`

### Request

```bash
curl -X POST https://your-domain.com/api/call-analytics \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "language": "Tamil",
    "audioFormat": "mp3",
    "audioBase64": "SUQzBAAAAAAAI1RTU0UAAAAP..."
  }'
```

### Request Fields

| Field | Type | Description |
|-------|------|-------------|
| `language` | string | "Tamil" (Tanglish) or "Hindi" (Hinglish) |
| `audioFormat` | string | Always "mp3" |
| `audioBase64` | string | Base64-encoded MP3 audio file |

### Response

```json
{
  "status": "success",
  "language": "Tamil",
  "transcript": "Agent: Vanakkam... Customer: Hello...",
  "summary": "Agent discussed EMI options with customer...",
  "sop_validation": {
    "greeting": true,
    "identification": false,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 0.8,
    "adherenceStatus": "FOLLOWED",
    "explanation": "Agent did not verify customer identity."
  },
  "analytics": {
    "paymentPreference": "EMI",
    "rejectionReason": "NONE",
    "sentiment": "Positive"
  },
  "keywords": ["EMI options", "Guvi Institution", "Data Science", "placement support"]
}
```

### Response Fields

| Field | Description |
|-------|-------------|
| `status` | "success" or "error" |
| `transcript` | Full speech-to-text output |
| `summary` | AI-generated conversation summary |
| `sop_validation` | Object containing SOP compliance metrics |
| `analytics` | Payment preference, rejection reason, sentiment |
| `keywords` | Array of important keywords/phrases |

### SOP Validation Fields

| Field | Description |
|-------|-------------|
| `greeting` | Did agent greet properly? |
| `identification` | Did agent verify customer? |
| `problemStatement` | Was problem/purpose stated? |
| `solutionOffering` | Were solutions offered? |
| `closing` | Was there proper closing? |
| `complianceScore` | 0.0 to 1.0 (true fields / 5) |
| `adherenceStatus` | "FOLLOWED" (≥0.8) or "NOT_FOLLOWED" |
| `explanation` | Brief explanation of compliance |

### Analytics Categories

**Payment Preference:**
- `EMI` - Monthly installments
- `FULL_PAYMENT` - Complete payment at once
- `PARTIAL_PAYMENT` - Partial now, rest later
- `DOWN_PAYMENT` - Initial payment before EMI

**Rejection Reasons:**
- `HIGH_INTEREST` - Interest rate concerns
- `BUDGET_CONSTRAINTS` - Financial limitations
- `ALREADY_PAID` - Payment already made
- `NOT_INTERESTED` - No interest in product
- `NONE` - No rejection (positive outcome)

**Sentiment:**
- `Positive` / `Negative` / `Neutral`

### Error Response

```json
{
  "status": "error",
  "message": "Invalid API key or malformed request"
}
```

## 📁 Project Structure

```
your-repo/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── test_client.py         # Test client script
├── .env                   # Environment variables (DO NOT COMMIT)
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── render.yaml            # Render deployment config
├── README.md              # This file
└── test.mp3               # Sample test audio
```

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key for Whisper & Llama |
| `API_KEY` | API authentication key for clients |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |

## 🚀 Deployment (Render.com)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. **IMPORTANT:** Add environment variables in Render dashboard:
   - `GROQ_API_KEY` = your Groq API key
   - `API_KEY` = your_secure_api_key
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase key
5. Deploy!

## 🧪 Testing

```bash
# Test with default audio
python test_client.py

# Test with custom audio
python test_client.py my_call.mp3 Hindi

# Test with specific language
python test_client.py call_recording.mp3 Tamil
```

## 📊 Approach

### Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Audio Input   │────▶│  Groq Whisper   │────▶│ Transcript      │
│   (Base64 MP3)  │     │  Large v3 STT   │     │ (Cleaned)       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐     ┌────────▼────────┐
│   JSON Response │◀────│  Validation &   │◀────│  Groq Llama 3.3 │
│   + DB Storage  │     │  Pattern Detect │     │  70B Analysis   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Processing Pipeline

1. **Audio Ingestion** - Accept base64-encoded audio via REST API
2. **Speech-to-Text** - Groq Whisper Large v3 transcribes Hindi/Tamil/English
3. **Transcript Cleaning** - Remove garbled characters using Unicode filtering
4. **LLM Analysis** - Groq Llama 3.3 70B extracts structured compliance data
5. **Pattern Detection** - Regex patterns detect greetings, closings, solutions
6. **Score Calculation** - 0.2 per SOP step, FOLLOWED if ≥ 0.8
7. **Database Storage** - Supabase PostgreSQL stores all analysis results

### Why This Approach?

- **Groq Whisper** - FREE, fast, excellent multilingual (Hinglish/Tanglish)
- **Groq Llama 3.3 70B** - FREE, high accuracy, structured JSON output
- **Pattern Detection** - Catches cases LLM might miss (Tamil closing phrases)
- **Validation Layer** - Ensures outputs match required categories exactly

## 🤖 AI Tools Used

> **Disclosure:** The following AI tools were used in development:

| Tool | Purpose | Usage |
|------|---------|-------|
| **Groq Whisper Large v3** | Speech-to-Text | Production - transcribes audio files |
| **Groq Llama 3.3 70B** | NLP Analysis | Production - SOP validation, summarization, analytics |
| **GitHub Copilot** | Code Assistance | Development - code suggestions and debugging |
| **Claude (Anthropic)** | Architecture Design | Development - API design and optimization |

## ⚠️ Known Limitations

1. **Mixed-Language Transcription** - Tamil/Hindi with heavy English mixing may produce some garbled characters
2. **Cold Start** - Render free tier sleeps after 15 min inactivity (30-60s wake time)
3. **Audio Quality** - Best results with clear audio, minimal background noise
4. **Rate Limits** - Groq free tier: ~30 requests/minute

## 📄 License

MIT License

---

**Built for GUVI AI Challenge - Track 3: Call Center Compliance**
