# Alternative API Providers Configuration

## Quick Setup with Groq (RECOMMENDED - FREE & FAST!)

### Step 1: Get Groq API Key
1. Go to: https://console.groq.com/
2. Sign up (free)
3. Go to API Keys section
4. Create new key
5. Copy the key

### Step 2: Update .env
```env
# Choose your provider: openai, groq, claude, gemini
AI_PROVIDER=groq

# Groq API Key (FREE!)
GROQ_API_KEY=gsk_your_groq_key_here

# For Speech-to-Text, choose: openai, assemblyai, deepgram
STT_PROVIDER=assemblyai

# AssemblyAI Key (5 hours/month free)
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
```

### Step 3: Install Required Packages
```bash
# For Groq
pip install groq

# For AssemblyAI
pip install assemblyai

# For Anthropic Claude
pip install anthropic

# For Google Gemini
pip install google-generativeai
```

---

## Complete Provider Comparison

### Speech-to-Text Providers

| Provider | Free Tier | Cost After | Quality | Speed | Setup |
|----------|-----------|------------|---------|-------|-------|
| **AssemblyAI** | 5 hrs/month | $0.65/hr | ⭐⭐⭐⭐⭐ | Fast | Easy |
| **Deepgram** | $200 credits | $0.0043/min | ⭐⭐⭐⭐⭐ | Very Fast | Easy |
| **OpenAI Whisper** | No free tier | $0.006/min | ⭐⭐⭐⭐⭐ | Medium | Easy |
| **Google STT** | 60 min/month | $0.024/min | ⭐⭐⭐⭐ | Fast | Medium |
| **Azure Speech** | 5 hrs/month | $1/hr | ⭐⭐⭐⭐ | Fast | Medium |

### Text Analysis Providers

| Provider | Free Tier | Cost After | Quality | Speed | Setup |
|----------|-----------|------------|---------|-------|-------|
| **Groq** | 14,400 req/day | Free! | ⭐⭐⭐⭐ | FASTEST | Easy |
| **Google Gemini** | 60 req/min | Free! | ⭐⭐⭐⭐⭐ | Fast | Easy |
| **Anthropic Claude** | $5 credits | $3/$15 per 1M tokens | ⭐⭐⭐⭐⭐ | Medium | Easy |
| **OpenAI GPT** | No free tier | $10 per 1M tokens | ⭐⭐⭐⭐⭐ | Medium | Easy |
| **Together AI** | $25 credits | $0.20 per 1M tokens | ⭐⭐⭐⭐ | Fast | Easy |

---

## Recommended Combinations

### Option 1: FREE & FAST (BEST FOR YOU!)
```
Speech: AssemblyAI (5 hrs/month free)
Analysis: Groq (14,400 requests/day free)
Monthly Cost: $0 for moderate usage
```

### Option 2: ALL FREE
```
Speech: Deepgram ($200 credits = ~777 hours)
Analysis: Google Gemini (60 req/min free)
Monthly Cost: $0 for several months
```

### Option 3: PREMIUM QUALITY
```
Speech: Deepgram
Analysis: Anthropic Claude
Monthly Cost: ~$5-10 depending on usage
```

---

## How to Get Each API Key

### Groq (AI Analysis)
1. Visit: https://console.groq.com/
2. Click "Sign In" → Sign up with Google/GitHub
3. Go to "API Keys" in left sidebar
4. Click "Create API Key"
5. Copy key (starts with `gsk_`)

### AssemblyAI (Speech-to-Text)
1. Visit: https://www.assemblyai.com/
2. Click "Get API Key" → Sign up
3. Dashboard will show your API key
4. Copy key

### Google Gemini (AI Analysis)
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key (starts with `AIzaSy`)

### Deepgram (Speech-to-Text)
1. Visit: https://console.deepgram.com/signup
2. Sign up (gets $200 credits)
3. Go to "API Keys"
4. Copy your key

### Anthropic Claude (AI Analysis)
1. Visit: https://console.anthropic.com/
2. Sign up
3. Gets $5 free credits
4. Go to "API Keys"
5. Create and copy key

---

## Code Integration Example

I can modify your `app.py` to support multiple providers with a simple config change:

```python
# .env
AI_PROVIDER=groq
STT_PROVIDER=assemblyai

# app.py will automatically use the configured provider
# No need to change multiple files!
```

Would you like me to:
1. ✅ Add multi-provider support to your code?
2. ✅ Create setup instructions for Groq + AssemblyAI?
3. ✅ Update the .env file with new options?

**Just let me know which provider you want to use and I'll integrate it!**

---

## Quick Comparison for Your Use Case

For your VoxSentinel project analyzing call recordings:

**Best Choice: Groq + AssemblyAI**
- ✅ Both FREE for your usage volume
- ✅ AssemblyAI: 5 hours/month = ~150 calls
- ✅ Groq: 14,400 requests/day = unlimited for you
- ✅ Fast performance
- ✅ Good quality
- ✅ Easy to integrate

**Alternative: Gemini + Deepgram**
- ✅ Also FREE
- ✅ Even more generous limits
- ✅ Excellent quality

---

## Want me to set it up?

I can quickly integrate **Groq + AssemblyAI** into your project right now. It will:
- ✅ Work exactly like OpenAI (same API structure)
- ✅ Be FREE for your usage
- ✅ Be 10x faster
- ✅ Support same features (transcription + analysis)

Just say "integrate groq" and I'll do it! 🚀
