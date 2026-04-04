# 🧪 VoxSentinel API Testing Guide

## Quick Start - Frontend Configuration

Your frontend is already configured! Just verify these settings:

**File:** `frontend/voxsentinel-connect-main/.env`
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=sk_track3_987654321
```

---

## 📡 API Endpoints for Testing

### Base URL
```
http://localhost:8000
```

### API Key (for authentication)
```
sk_track3_987654321
```

---

## 🔥 Test with cURL (Command Line)

### 1. Health Check
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "🛡️ VoxSentinel API is running",
  "version": "2.0.0",
  "providers": {
    "stt": "groq",
    "ai": "groq"
  }
}
```

---

### 2. Get Statistics
```bash
curl http://localhost:8000/api/stats
```

**Expected Response:**
```json
{
  "total_calls": 3,
  "avg_compliance_score": 0.53,
  "sentiment_distribution": {
    "Positive": 2,
    "Neutral": 1
  },
  "payment_distribution": {
    "Credit Card": 1,
    "EMI": 0
  },
  "compliance_trend": [...]
}
```

---

### 3. Get Call History
```bash
curl "http://localhost:8000/api/history?limit=10&page=1"
```

**Expected Response:**
```json
{
  "status": "success",
  "total": 3,
  "page": 1,
  "per_page": 10,
  "calls": [
    {
      "id": "uuid",
      "transcript": "Full call text...",
      "compliance_score": 1.0,
      "sentiment": "Positive",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 4. Analyze Audio (Main Endpoint)

**Using PowerShell:**
```powershell
# Convert audio to base64
$audioBytes = [System.IO.File]::ReadAllBytes("test_file_final.mp3")
$audioBase64 = [Convert]::ToBase64String($audioBytes)

# Create JSON payload
$body = @{
    audio = $audioBase64
    language = "English"
} | ConvertTo-Json

# Send request
Invoke-RestMethod -Uri "http://localhost:8000/api/call-analytics" `
    -Method Post `
    -Headers @{"X-API-Key"="sk_track3_987654321"; "Content-Type"="application/json"} `
    -Body $body
```

**Using Python:**
```python
import requests
import base64

# Read and encode audio
with open("test_file_final.mp3", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode()

# Send request
response = requests.post(
    "http://localhost:8000/api/call-analytics",
    json={
        "audio": audio_base64,
        "language": "English"
    },
    headers={
        "X-API-Key": "sk_track3_987654321",
        "Content-Type": "application/json"
    }
)

print(response.json())
```

**Expected Response:**
```json
{
  "status": "success",
  "analysis_id": "9c17179d-aa9d-4359-84f5-17aa195318e4",
  "language": "English",
  "transcript": "Hello, this is customer service...",
  "summary": "Customer called about payment issues. Agent offered solution.",
  "sop_validation": {
    "greeting": true,
    "identification": true,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 1.0,
    "adherenceStatus": "FOLLOWED",
    "explanation": "All SOP stages were followed correctly"
  },
  "analytics": {
    "sentiment": "Positive",
    "paymentPreference": "EMI",
    "rejectionReason": "NONE"
  },
  "keywords": [
    "payment",
    "customer service",
    "EMI",
    "flexible plan"
  ]
}
```

---

## 🌐 Test with Frontend Website

### Step 1: Start Backend
```bash
cd d:\AI-Voice-Detection-main\AI-Voice-Detection-main
uvicorn app:app --reload --port 8000
```

### Step 2: Start Frontend
```bash
cd d:\AI-Voice-Detection-main\frontend\voxsentinel-connect-main
npm run dev
```

### Step 3: Open Browser
```
http://localhost:5173
```

### Step 4: Test Features

1. **Dashboard Page** (`/`)
   - Should show statistics from `/api/stats`
   - Charts with compliance scores
   - Sentiment distribution
   - Payment preferences

2. **Analyze Call Page** (`/analyze`)
   - Upload `test_file_final.mp3`
   - Select language: English
   - Click "Analyze Call"
   - Wait 10-30 seconds for results
   - Should display:
     - Full transcript
     - Summary
     - SOP validation (✓/✗ for each stage)
     - Compliance score
     - Sentiment
     - Keywords

3. **Call History Page** (`/history`)
   - Shows all analyzed calls
   - Pagination
   - Filter by date/compliance

---

## 🧪 Automated Testing

### Run Full Test Suite
```bash
cd d:\AI-Voice-Detection-main\AI-Voice-Detection-main
python test_api_live.py
```

This will test:
- ✅ Health check
- ✅ API documentation
- ✅ Provider configuration
- ✅ Statistics endpoint
- ✅ Call history endpoint
- ✅ **Full audio analysis** with real Groq API

---

## 🔍 Verify Providers

### Check Current Providers
```bash
curl http://localhost:8000/health
```

**Should show:**
```json
{
  "status": "ok",
  "providers": {
    "stt": "groq",
    "ai": "groq"
  },
  "services": {
    "groq": "configured",
    "openai": "configured",
    "assemblyai": "configured",
    "database": "configured"
  }
}
```

---

## 📝 Sample Test Data

### Sample Audio Files
- `test_file_final.mp3` - Primary test file (included)

### Sample Languages
- English
- Hindi
- Tamil
- Spanish
- French
- German

### Expected SOP Validation
A compliant call should have:
- ✅ Greeting: "Hello, welcome to..."
- ✅ Identification: "May I have your name/ID?"
- ✅ Problem Statement: "How can I help you today?"
- ✅ Solution Offering: "I can offer you..."
- ✅ Closing: "Thank you for calling"

**Compliance Score:** 5/5 = 1.0 (100%)
**Adherence Status:** FOLLOWED

---

## 🐛 Troubleshooting

### Backend Not Starting?
```bash
# Install dependencies
pip install -r requirements.txt

# Check if port 8000 is free
netstat -ano | findstr :8000
```

### Frontend Not Connecting?
1. Check `.env` file has correct `VITE_API_URL`
2. Verify backend is running on port 8000
3. Check browser console for CORS errors

### Groq API Errors?
1. Verify `GROQ_API_KEY` in `.env`
2. Check API quota at https://console.groq.com
3. Try switching to AssemblyAI:
   ```env
   STT_PROVIDER=assemblyai
   AI_PROVIDER=groq
   ```

### Database Errors?
1. Verify Supabase credentials in `.env`
2. Check if SQL schema was run
3. Test with: `curl http://localhost:8000/api/stats`

---

## 🎯 Success Criteria

Your API is working correctly if:
- ✅ Health check returns 200 OK
- ✅ Stats endpoint returns call data
- ✅ Audio analysis completes in <30 seconds
- ✅ Transcript is accurate
- ✅ SOP validation has all 5 stages
- ✅ Compliance score is 0.0-1.0
- ✅ Data is saved to Supabase
- ✅ Frontend can upload and display results

---

## 📊 Performance Benchmarks

| Endpoint | Expected Time | Status Code |
|----------|---------------|-------------|
| `GET /` | <100ms | 200 |
| `GET /api/stats` | <2s | 200 |
| `GET /api/history` | <2s | 200 |
| `POST /api/call-analytics` | 10-30s | 200 |

---

## 🔐 Security Note

**NEVER commit these to GitHub:**
- `GROQ_API_KEY`
- `ASSEMBLYAI_API_KEY`
- `OPENAI_API_KEY`
- `SUPABASE_KEY`

All keys are in `.env` files which are in `.gitignore` ✅

---

## 📞 Support

If tests fail, check:
1. Backend logs in terminal
2. Frontend console (F12 in browser)
3. `.env` configuration
4. API provider status (Groq/AssemblyAI)

Happy Testing! 🚀
