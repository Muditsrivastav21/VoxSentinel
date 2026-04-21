# VoxSentinel - AI-Powered Call Center Compliance

> **🚀 Live URL:** https://voxsentinel.onrender.com  
> **🔑 API Key:** `sk_track3_987654321`  
> **🖥️ Dashboard:** https://voxsentinelmain.onrender.com

---

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

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI (Python 3.11) |
| **Speech-to-Text** | Groq Whisper Large v3 (FREE) |
| **LLM Analysis** | Groq Llama 3.3 70B Versatile |
| **Database** | Supabase (PostgreSQL) |
| **Async Tasks** | Celery (optional) |
| **Frontend** | React + Vite + TailwindCSS + shadcn/ui |
| **Deployment** | Render.com |

---

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

---

## 📁 Project Structure

```
VoxSentinel/
├── AI-Voice-Detection-main/     # Backend API (FastAPI)
│   ├── app.py                   # Main application
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example            # Environment template
│   ├── render.yaml             # Render deployment config
│   └── tasks.py                # Celery tasks
│
├── frontend/                    # Frontend Dashboard (React)
│   └── voxsentinel-connect-main/
│       ├── src/                # React source code
│       ├── package.json        # Node dependencies
│       └── vite.config.ts      # Vite configuration
│
└── README.md                   # This filE
```

---

## 🚀 Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/Muditsrivastav21/VoxSentinel.git
cd VoxSentinel
```

### 2. Backend Setup

```bash
cd AI-Voice-Detection-main

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Set Environment Variables

```bash
# .env file
GROQ_API_KEY=your_groq_api_key
API_KEY=sk_track3_987654321
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 4. Run Application

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/

# Or use the test client
python test_client.py test.mp3 Tamil
```

---

## 📡 API Documentation

### Authentication

All requests must include an API key:
```
x-api-key: sk_track3_987654321
```

### Endpoint

**POST** `/api/call-analytics`

### Request

```bash
curl -X POST https://voxsentinel.onrender.com/api/call-analytics \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_track3_987654321" \
  -d '{
    "language": "Tamil",
    "audioBase64": "BASE64_ENCODED_AUDIO"
  }'
```

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
  "keywords": ["EMI", "Data Science", "placement", "course"]
}
```

---

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
7. **Database Storage** - Supabase PostgreSQL stores all results

---

## 🤖 AI Tools Used

> **Disclosure:** The following AI tools were used in development:

| Tool | Purpose | Usage |
|------|---------|-------|
| **Groq Whisper Large v3** | Speech-to-Text | Production - transcribes audio files |
| **Groq Llama 3.3 70B** | NLP Analysis | Production - SOP validation, summarization |
| **GitHub Copilot** | Code Assistance | Development - code suggestions |
| **Claude (Anthropic)** | Architecture Design | Development - API design and optimization |

---

## ⚠️ Known Limitations

1. **Mixed-Language Transcription** - Tamil/Hindi with heavy English may produce some artifacts
2. **Cold Start** - Render free tier sleeps after 15 min inactivity (30-60s wake time)
3. **Audio Quality** - Best results with clear audio, minimal background noise
4. **Rate Limits** - Groq free tier: ~30 requests/minute

---

## 🔗 Links

- **Live API:** https://voxsentinel.onrender.com
- **Dashboard:** https://voxsentinelmain.onrender.com
- **API Docs:** https://voxsentinel.onrender.com/docs

---

## 📄 License

MIT License

---

**Built for GUVI AI Challenge - Track 3: Call Center Compliance**
