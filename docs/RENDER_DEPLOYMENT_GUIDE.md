# 🚀 VoxSentinel - Easy Render Deployment Guide

## ✅ CODE CHANGES ALREADY DONE FOR YOU:
1. ✔️ Backend CORS updated to allow Render domains
2. ✔️ Frontend already uses environment variables
3. ✔️ render.yaml configured for both services

---

## 🔑 WHERE TO GET YOUR API KEYS

| Key | Where to Get |
|-----|-------------|
| **GROQ_API_KEY** | https://console.groq.com/keys → Create API Key (FREE) |
| **SUPABASE_URL** | https://supabase.com → Your Project → Settings → API → Project URL |
| **SUPABASE_KEY** | https://supabase.com → Your Project → Settings → API → anon public key |
| **API_KEY** | Create any secure string (e.g., `sk_voxsentinel_abc123xyz`) |

---

## 🚀 DEPLOYMENT STEPS (Manual Method - Easier!)

### STEP 1: Push to GitHub (2 min)

```bash
cd D:\AI-Voice-Detection-main
git add .
git commit -m "Ready for Render"
git push
```

---

### STEP 2: Deploy Backend (5 min)

1. Go to **https://dashboard.render.com**
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Fill in:

| Field | Value |
|-------|-------|
| Name | `voxsentinel-api` |
| Root Directory | `AI-Voice-Detection-main` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| Instance Type | `Free` |

5. Click **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | *(paste from Groq console)* |
| `API_KEY` | `sk_voxsentinel_your_secret_key` |
| `SUPABASE_URL` | *(paste from Supabase)* |
| `SUPABASE_KEY` | *(paste from Supabase)* |
| `STT_PROVIDER` | `groq` |
| `AI_PROVIDER` | `groq` |
| `ENVIRONMENT` | `production` |
| `DEMO_MODE` | `false` |

6. Click **"Create Web Service"**
7. Wait 3-5 min → **Copy your URL** (e.g., `https://voxsentinel-api.onrender.com`)

---

### STEP 3: Deploy Frontend (5 min)

1. Click **"New +"** → **"Static Site"**
2. Connect **same repo**
3. Fill in:

| Field | Value |
|-------|-------|
| Name | `voxsentinel-frontend` |
| Root Directory | `frontend/voxsentinel-connect-main` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `dist` |

4. Add **Environment Variables**:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://voxsentinel-api.onrender.com` *(your backend URL from Step 2)* |
| `VITE_API_KEY` | *(same as API_KEY from Step 2)* |

5. Click **"Create Static Site"**
6. Wait 3-5 min → Done! 🎉

---

## ✅ TEST YOUR DEPLOYMENT

**Backend:** Open `https://voxsentinel-api.onrender.com/` → Should see `{"status":"healthy"}`

**Frontend:** Open `https://voxsentinel-frontend.onrender.com/` → Should load your app

**API Docs:** `https://voxsentinel-api.onrender.com/docs`

---

## 🔄 MAKING UPDATES

After deployment, to update your app:

```bash
# 1. Make changes
# 2. Commit
git add .
git commit -m "Your changes"

# 3. Push - auto-deploys in 2-5 min!
git push
```

---

## 🎯 YOUR LIVE URLS

```
Frontend: https://voxsentinel-frontend.onrender.com
Backend:  https://voxsentinel-api.onrender.com
API Docs: https://voxsentinel-api.onrender.com/docs
```

---

## ❓ COMMON ISSUES

| Problem | Solution |
|---------|----------|
| Build failed | Check Render logs → Dashboard → Logs |
| Frontend can't connect | Verify `VITE_API_URL` is correct (no trailing `/`) |
| 30s delay first load | Free tier sleeps - normal, will wake up |
| CORS error | Already fixed! Redeploy backend |

