# 🎯 VoxSentinel - Quick Test Reference

## 📋 API Credentials for Frontend Testing

### Backend API Configuration
```
Base URL:  http://localhost:8000
API Key:   sk_track3_987654321
```

### Frontend Configuration
File: `frontend/voxsentinel-connect-main/.env`
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=sk_track3_987654321
```

---

## 🚀 Quick Start

### 1. Start Backend (Terminal 1)
```bash
cd d:\AI-Voice-Detection-main\AI-Voice-Detection-main
pip install groq
uvicorn app:app --reload --port 8000
```

### 2. Start Frontend (Terminal 2)
```bash
cd d:\AI-Voice-Detection-main\frontend\voxsentinel-connect-main
npm run dev
```

### 3. Open Browser
```
Frontend: http://localhost:5173
Backend API Docs: http://localhost:8000/docs
HTML Tester: Open test_api.html in browser
```

---

## 🧪 Testing Options

### Option 1: HTML Tester (Easiest)
1. Open `test_api.html` in your browser
2. Click "Health Check" to verify backend
3. Upload audio file and click "Analyze Call"

### Option 2: Frontend Website
1. Go to http://localhost:5173
2. Navigate to "Analyze Call" page
3. Upload `test_file_final.mp3`
4. Select language and analyze

### Option 3: Python Test Script
```bash
python test_api_live.py
```

### Option 4: Postman
1. Import `VoxSentinel_API_Collection.postman.json`
2. Run tests from collection

---

## 📡 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/docs` | GET | Interactive API docs (Swagger) |
| `/api/stats` | GET | Dashboard statistics |
| `/api/history` | GET | Call history with pagination |
| `/api/call-analytics` | POST | Analyze audio (main feature) |

---

## 🎤 Test Audio Analysis

**POST** `http://localhost:8000/api/call-analytics`

**Headers:**
```
X-API-Key: sk_track3_987654321
Content-Type: application/json
```

**Body:**
```json
{
  "audio": "<base64-encoded-audio>",
  "language": "English"
}
```

**Response (Expected):**
```json
{
  "status": "success",
  "analysis_id": "uuid",
  "transcript": "Full transcription...",
  "summary": "2-3 sentence summary",
  "sop_validation": {
    "greeting": true,
    "identification": true,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 1.0,
    "adherenceStatus": "FOLLOWED"
  },
  "analytics": {
    "sentiment": "Positive",
    "paymentPreference": "EMI",
    "rejectionReason": "NONE"
  },
  "keywords": ["payment", "customer service", ...]
}
```

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] Health check returns `"status": "success"`
- [ ] Providers show `"stt": "groq"` and `"ai": "groq"`
- [ ] Stats endpoint returns data
- [ ] Audio analysis completes successfully
- [ ] Results saved to Supabase
- [ ] Frontend connects to backend
- [ ] Dashboard displays statistics
- [ ] File upload works in frontend

---

## 🔧 Current Configuration

**Providers (FREE!):**
- Speech-to-Text: Groq (whisper-large-v3)
- AI Analysis: Groq (llama-3.3-70b-versatile)
- Database: Supabase (PostgreSQL)

**Supported Languages:**
- English, Hindi, Tamil, Spanish, French, German

**Features:**
- ✅ Multi-provider support (Groq, OpenAI, AssemblyAI)
- ✅ Real-time transcription
- ✅ SOP compliance validation (5 stages)
- ✅ Sentiment analysis
- ✅ Payment preference detection
- ✅ Keyword extraction
- ✅ Database persistence
- ✅ RESTful API with Swagger docs
- ✅ CORS enabled for frontend
- ✅ Rate limiting (10 req/min)
- ✅ Structured logging

---

## 📞 Need Help?

1. **Backend not starting?**
   - Check if port 8000 is available
   - Verify `.env` file exists
   - Run `pip install -r requirements.txt`

2. **Frontend not connecting?**
   - Verify backend is running
   - Check `.env` has correct `VITE_API_URL`
   - Clear browser cache

3. **API errors?**
   - Check backend terminal logs
   - Verify Groq API key in `.env`
   - Test with: `curl http://localhost:8000/`

---

## 🎉 Success!

If you can:
1. ✅ Upload an audio file
2. ✅ See the full transcript
3. ✅ View SOP validation results
4. ✅ See compliance score
5. ✅ Data appears in call history

**Your VoxSentinel API is fully functional!** 🚀

---

Made with ❤️ by VoxSentinel Team
