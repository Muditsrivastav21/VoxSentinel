# ⚡ QUICK START - Deploy in 10 Minutes

Call Center Compliance API - Track 3

---

## 🚀 Steps

### Step 1: Install Dependencies (2 mins)

```bash
cd AI-Voice-Detection-main

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

### Step 2: Set Up Environment Variables (1 min)

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys:
# GROQ_API_KEY=your_groq_api_key
# API_KEY=your_secure_api_key
```

**⚠️ IMPORTANT:** The `.env` file is in `.gitignore` and will NOT be pushed to git.

---

### Step 3: Run Locally (1 min)

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Health Check:** Open http://localhost:8000/ in browser

Should see:
```json
{
  "status": "success",
  "message": "Call Center Compliance API is running",
  "version": "1.0.0",
  "supported_languages": ["Tamil", "Hindi"]
}
```

---

### Step 4: Test the API (2 mins)

```bash
# Test with sample audio
python test_client.py test.mp3 Tamil
```

**Expected Output:**
```
✅ ANALYSIS COMPLETE
📋 STATUS: success
🌐 LANGUAGE: Tamil
📝 TRANSCRIPT: Agent: Vanakkam...
📊 SUMMARY: Agent discussed payment options...
✅ SOP VALIDATION:
  Greeting: ✅
  Identification: ❌
  ...
📈 ANALYTICS:
  Payment Preference: EMI
  Rejection Reason: NONE
  Sentiment: Positive
🔑 KEYWORDS: EMI options, course fee, placement...
```

---

### Step 5: Deploy to Render (5 mins)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Track 3: Call Center Compliance API"
   git push origin main
   ```

2. **Go to Render.com** → Create New Web Service

3. **Connect your GitHub repo**

4. **⚠️ IMPORTANT: Add Environment Variables in Render Dashboard:**
   - `GROQ_API_KEY` = your Groq API key
   - `API_KEY` = your_secure_api_key

5. **Deploy!**

---

## 📋 Test cURL Command

```bash
curl -X POST https://your-app.onrender.com/api/call-analytics \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "language": "Tamil",
    "audioFormat": "mp3",
    "audioBase64": "'$(base64 -w 0 test.mp3)'"
  }'
```

---

## 🎯 API Response Format

```json
{
  "status": "success",
  "language": "Tamil",
  "transcript": "Full conversation text...",
  "summary": "AI-generated summary...",
  "sop_validation": {
    "greeting": true,
    "identification": false,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 0.8,
    "adherenceStatus": "FOLLOWED",
    "explanation": "..."
  },
  "analytics": {
    "paymentPreference": "EMI",
    "rejectionReason": "NONE",
    "sentiment": "Positive"
  },
  "keywords": ["keyword1", "keyword2", ...]
}
```

---

## ⚠️ Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure `.env` file exists with your OpenAI key
- Or set environment variable: `export OPENAI_API_KEY=sk-...`

### "Invalid API key" (401 error)
- Check `x-api-key` header matches `API_KEY` in `.env`

### Render deployment fails
- Make sure `OPENAI_API_KEY` is set in Render dashboard
- Check Render logs for specific error

---

**You're ready! 🚀**
