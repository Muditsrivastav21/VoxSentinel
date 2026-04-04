# 🚀 VoxSentinel Launch Guide

## Current Status

### ✅ Backend - READY
- All Python dependencies installed
- Environment configured (.env with Supabase)
- Tests available

### ⚠️ Frontend - NEEDS SETUP
- Dependencies NOT installed (node_modules missing)
- Needs: `npm install`

### ⚠️ Database - NEEDS SETUP
- Supabase connected
- Schema NOT run yet

---

## Step-by-Step Launch Process

### 📊 Step 1: Set Up Supabase Database (2 minutes)

**Issue in your screenshot:** You tried to run the filename "supabase_schema.sql" instead of the file contents.

**Correct Steps:**

1. **Open the SQL file** in your code editor:
   - File: `d:\AI-Voice-Detection-main\AI-Voice-Detection-main\supabase_setup_simple.sql`

2. **Copy the ENTIRE contents** of the file (Ctrl+A, Ctrl+C)

3. **Go to Supabase SQL Editor:**
   - URL: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/editor
   - Click "New query"

4. **Paste the SQL code** (Ctrl+V)

5. **Click "Run"** or press Ctrl+Enter

6. **Expected result:** "Success. No rows returned" or "3 rows inserted"

✅ **Database is now ready!**

---

### 🐍 Step 2: Launch Backend (1 minute)

Open a terminal in the backend directory:

```bash
cd d:\AI-Voice-Detection-main\AI-Voice-Detection-main
uvicorn app:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
🚀 VoxSentinel API starting up...
📍 Environment: development
🔑 OpenAI configured: True
🗄️  Supabase configured: True
```

**Test it:**
- Open: http://localhost:8000/health
- Should see: `{"status":"healthy","service":"VoxSentinel API",...}`

✅ **Backend is running!**

**Keep this terminal open.**

---

### 🎨 Step 3: Install Frontend Dependencies (3-5 minutes)

Open a **NEW terminal** for frontend:

```bash
cd d:\AI-Voice-Detection-main\frontend\voxsentinel-connect-main
npm install
```

**This will:**
- Download ~65 packages
- Create node_modules folder (~200MB)
- Take 2-5 minutes

**Expected output:**
```
added 847 packages in 3m
```

✅ **Dependencies installed!**

---

### 🌐 Step 4: Launch Frontend (30 seconds)

In the same frontend terminal:

```bash
npm run dev
```

**Expected output:**
```
VITE v5.4.19  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ **Frontend is running!**

**Keep this terminal open too.**

---

## 🧪 Step 5: Test Everything

### Backend Tests
```bash
# In backend terminal (Ctrl+C to stop server first)
cd d:\AI-Voice-Detection-main\AI-Voice-Detection-main
pytest test_unit.py -v
```

Expected: All tests pass ✅

### Frontend Access
1. Open: http://localhost:5173
2. You should see the VoxSentinel dashboard
3. Try navigating:
   - Dashboard (shows stats from Supabase)
   - Analyze Call (upload audio)
   - Call History (shows 3 sample calls)

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🎯 Quick Test - End-to-End

1. **Go to Analyze Call page:** http://localhost:5173/analyze-call

2. **Upload a test audio file:**
   - Use: `d:\AI-Voice-Detection-main\AI-Voice-Detection-main\test.mp3`
   - Or any MP3/WAV file

3. **Wait for analysis** (15-30 seconds)

4. **View results:**
   - Compliance score
   - SOP validation
   - Sentiment
   - Transcript

5. **Check Call History:**
   - Your analysis should now appear in the list
   - Click Dashboard to see updated stats

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** "Port 8000 is already in use"
```bash
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Error:** "OPENAI_API_KEY not found"
- Check `.env` file exists
- Verify key is set correctly

### Frontend won't start

**Error:** "Cannot find module"
```bash
# Delete and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error:** "EADDRINUSE: address already in use :::5173"
```bash
# Use different port
npm run dev -- --port 5174
```

### Database connection fails

**Error:** "Database not configured"
- Check `.env` has SUPABASE_URL and SUPABASE_KEY
- Verify credentials are correct
- Run SQL schema in Supabase

**Error:** "table call_analyses does not exist"
- You forgot to run the SQL schema
- Go back to Step 1

### API calls fail

**Error:** "Invalid API key"
- Frontend `.env` VITE_API_KEY must match backend `.env` API_KEY
- Default: Set via `API_KEY` environment variable

**Error:** "CORS error"
- Backend must be running
- Check backend console for CORS errors
- Verify frontend URL is in allowed origins (app.py)

---

## 📝 Quick Commands Reference

```bash
# Backend
cd d:\AI-Voice-Detection-main\AI-Voice-Detection-main
uvicorn app:app --reload                    # Start server
pytest test_unit.py -v                      # Run tests
python test_client.py test.mp3 Tamil        # Test client

# Frontend
cd d:\AI-Voice-Detection-main\frontend\voxsentinel-connect-main
npm install                                 # Install deps
npm run dev                                 # Start dev server
npm run build                               # Build for production
npm run preview                             # Preview build

# Both (in separate terminals)
# Terminal 1: Backend
cd d:\AI-Voice-Detection-main\AI-Voice-Detection-main && uvicorn app:app --reload

# Terminal 2: Frontend
cd d:\AI-Voice-Detection-main\frontend\voxsentinel-connect-main && npm run dev
```

---

## ✅ Success Checklist

- [ ] Supabase SQL schema executed successfully
- [ ] Backend starts without errors (port 8000)
- [ ] Frontend dependencies installed (node_modules exists)
- [ ] Frontend starts without errors (port 5173)
- [ ] Can access http://localhost:8000/health
- [ ] Can access http://localhost:5173
- [ ] Can upload and analyze a call
- [ ] Results appear in Call History
- [ ] Dashboard shows statistics

---

## 🎉 You're Live!

Once all steps are complete:

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173

**Remember:** Keep both terminals running!

---

## 📱 Production Deployment (Future)

When ready to deploy:

1. **Backend:** Deploy to Render/Railway/Vercel
2. **Frontend:** Deploy to Vercel/Netlify
3. Update frontend `.env` with production API URL
4. Ensure environment variables are set in hosting platforms
5. Enable HTTPS
6. Update CORS settings

---

**Need help?** Check `SECURITY.md` and `SETUP_COMPLETE.md` for more details.
