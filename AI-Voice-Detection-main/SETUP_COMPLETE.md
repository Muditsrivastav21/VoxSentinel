# 🔐 Supabase Setup Guide

## ✅ Security Setup

Your credentials should be stored in `.env` files which are **in `.gitignore`** and will NOT be committed to GitHub.

### 📍 Credentials Location

**Backend:** `AI-Voice-Detection-main/.env`
```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your_supabase_anon_key
API_KEY=your_secure_api_key
GROQ_API_KEY=your_groq_api_key
```

**Frontend:** `frontend/voxsentinel-connect-main/.env`
```
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your_api_key
```

### 🔒 Security Measures Implemented

1. ✅ `.env` files in `.gitignore`
2. ✅ `.env.example` with placeholder values (safe to commit)
3. ✅ `SECURITY.md` with best practices
4. ✅ No credentials in any committed files

---

## 🚀 Next Steps

### 1. Set Up Supabase Database

Run the SQL schema to create the database tables:

1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/editor
2. Click **"New query"**
3. Copy the entire contents of `supabase_schema.sql`
4. Paste into the SQL editor
5. Click **"Run"** (or press Ctrl+Enter)

This will create:
- `call_analyses` table (main data)
- `api_keys` table (optional, for multi-user)
- `api_usage` table (optional, for tracking)
- Views for dashboard statistics
- Indexes for performance

### 2. Install Backend Dependencies

```bash
cd AI-Voice-Detection-main
pip install -r requirements.txt
```

This will install:
- `supabase` - Database client
- `pytest` - For running tests
- `httpx` - For test client
- All existing dependencies

### 3. Test the Backend

```bash
# Run unit tests
pytest test_unit.py -v

# Start the server
uvicorn app:app --reload --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 4. Install Frontend Dependencies

```bash
cd frontend/voxsentinel-connect-main
npm install
npm run dev
```

The frontend will be available at:
- **Frontend:** http://localhost:5173

---

## 🧪 Testing the Integration

### Test Health Check
```bash
curl http://localhost:8000/health
```

### Test Call Analysis (with real API)
```bash
# Use the test client
python test_client.py test.mp3 Tamil
```

### Test Frontend
1. Open http://localhost:5173
2. Go to **"Analyze Call"** page
3. Upload an audio file (MP3, WAV, M4A)
4. Wait for analysis
5. View results on **Dashboard** and **Call History**

---

## 📊 Database Features

With Supabase connected, you now have:

### ✅ Call History
- All analyzed calls saved to database
- Pagination support (10 calls per page)
- Search and filtering
- Delete functionality

### ✅ Dashboard Stats
- Total calls analyzed
- Average compliance score
- Sentiment distribution
- Calls today/this week
- Recent calls list

### ✅ Persistent Storage
- All analysis results saved
- Query historical data
- Generate reports
- Track trends over time

---

## 🔍 Verifying Security

Before committing to Git, always check:

```bash
# Check git status
git status

# Verify .env is NOT listed
git ls-files | grep .env

# If empty output = GOOD (not tracked)
# If shows .env = BAD (don't commit!)
```

---

## 🌐 Production Deployment

When deploying to production:

### Backend (Render/Vercel/Railway)
Add environment variables in the platform settings:
- `OPENAI_API_KEY`
- `API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `ENVIRONMENT=production`

### Frontend (Vercel/Netlify)
Add environment variables:
- `VITE_API_URL` (your production API URL)
- `VITE_API_KEY` (same as backend API_KEY)

**Never** hardcode credentials in code!

---

## 📚 Documentation

- **API Docs:** http://localhost:8000/docs (when running)
- **Security Guide:** `SECURITY.md`
- **Database Schema:** `supabase_schema.sql`
- **Test Suite:** `test_unit.py`

---

## 🆘 Troubleshooting

### Database Connection Issues

**Error:** "Database not configured"
```bash
# Check .env has correct values
cat .env | grep SUPABASE

# Test connection
python -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); print(create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')))"
```

### Frontend Can't Connect to Backend

**Error:** "Failed to fetch"
```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check CORS settings in app.py allow localhost:5173
# 3. Check frontend .env has correct VITE_API_URL
```

### API Key Issues

**Error:** "Invalid API key"
```bash
# Make sure frontend VITE_API_KEY matches backend API_KEY
# Check both .env files
```

---

## ✅ Checklist

- [x] Supabase credentials added to `.env`
- [x] `.env` in `.gitignore`
- [x] `.env.example` with placeholders
- [x] Security documentation created
- [ ] **TODO:** Run SQL schema in Supabase
- [ ] **TODO:** Install backend dependencies
- [ ] **TODO:** Test the API
- [ ] **TODO:** Install frontend dependencies
- [ ] **TODO:** Test the frontend

---

## 🎉 You're All Set!

Your VoxSentinel project is now:
- ✅ Securely configured
- ✅ Connected to Supabase
- ✅ Ready for development
- ✅ Safe to commit to GitHub

**Remember:** Never commit `.env` files!

---

**Need Help?** Check `SECURITY.md` for security best practices.
