# Call Center Compliance API - Track 3

## 🎯 Overview

REST API that performs **multi-stage AI analysis** on call center recordings to extract compliance metrics and business intelligence. Supports **Tamil (Tanglish)** and **Hindi (Hinglish)** mixed-language conversations.

## 📋 Features

- ✅ **Speech-to-Text** - Whisper API for accurate Hinglish/Tanglish transcription
- ✅ **AI Summarization** - GPT-4 powered conversation summaries
- ✅ **SOP Validation** - Automated compliance scoring against call center scripts
- ✅ **Payment Classification** - EMI, FULL_PAYMENT, PARTIAL_PAYMENT, DOWN_PAYMENT
- ✅ **Rejection Analysis** - Identifies reasons for incomplete sales
- ✅ **Sentiment Analysis** - Positive, Negative, Neutral classification
- ✅ **Keyword Extraction** - Key topics and entities from conversations
- ✅ **API Key Authentication** - Secure access control

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Speech-to-Text:** OpenAI Whisper API
- **NLP Analysis:** OpenAI GPT-4-turbo
- **Server:** Uvicorn
- **Deployment:** Render.com

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

### Multi-Stage AI Pipeline

1. **Audio Input** → Base64 decode MP3
2. **Transcription** → OpenAI Whisper API (multilingual)
3. **NLP Analysis** → GPT-4-turbo with structured output
4. **SOP Validation** → Rule-based scoring from GPT analysis
5. **Analytics Extraction** → Categorized business intelligence
6. **Response** → Structured JSON output

### Why This Approach?

- **Whisper API** - Best-in-class for code-mixed languages (Hinglish/Tanglish)
- **GPT-4-turbo** - Accurate understanding of context and intent
- **JSON Mode** - Guaranteed structured output for reliable parsing
- **Validation Layer** - Ensures all outputs match required categories

## 📄 License

MIT License
