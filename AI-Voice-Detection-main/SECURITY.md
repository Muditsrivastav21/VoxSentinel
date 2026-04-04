# 🔒 Security Guidelines for VoxSentinel

## Environment Variables

### ⚠️ CRITICAL: Never Commit These Files
The following files contain sensitive credentials and **MUST NEVER** be committed to Git:

- `AI-Voice-Detection-main/.env` - Backend credentials
- `frontend/voxsentinel-connect-main/.env` - Frontend API keys

Both files are already in `.gitignore`, but always verify before committing.

### Current Credentials (Encrypted in .env files only)

**Backend (.env):**
- `OPENAI_API_KEY` - OpenAI API key for Whisper + GPT-4
- `API_KEY` - Authentication key for your API clients
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anonymous/public key

**Frontend (.env):**
- `VITE_API_URL` - Backend API endpoint
- `VITE_API_KEY` - Must match backend `API_KEY`

### Setup Instructions

1. **Backend Setup:**
   ```bash
   cd AI-Voice-Detection-main
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend/voxsentinel-connect-main
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

## Git Safety Checklist

Before committing, always verify:

```bash
# Check what will be committed
git status

# Verify .env is NOT listed
git ls-files | grep .env

# If .env appears, it's NOT in .gitignore - DON'T COMMIT!
```

## Emergency: If Credentials Were Committed

If you accidentally committed credentials:

1. **Immediately rotate all keys:**
   - OpenAI: Generate new API key at https://platform.openai.com/api-keys
   - Supabase: Reset keys at https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api
   - API_KEY: Generate new random key

2. **Remove from Git history:**
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

3. **Use BFG Repo-Cleaner (recommended):**
   ```bash
   java -jar bfg.jar --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

## Production Deployment

### Environment Variable Management

**DO NOT** hardcode credentials in production. Use secure methods:

1. **Vercel:**
   - Settings > Environment Variables
   - Add all VITE_* variables

2. **Render.com:**
   - Environment > Environment Variables
   - Add all variables from .env

3. **Docker:**
   ```bash
   docker run -e OPENAI_API_KEY=xxx -e SUPABASE_URL=xxx ...
   ```

4. **Kubernetes:**
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: voxsentinel-secrets
   data:
     openai-key: <base64-encoded>
   ```

## API Key Rotation Schedule

Rotate keys regularly for security:

- **OpenAI API Key**: Every 90 days
- **Supabase Keys**: Every 90 days  
- **API_KEY**: Every 30 days or after any security incident

## Access Control

### Supabase Row Level Security (RLS)

Enable RLS for multi-user environments:

```sql
ALTER TABLE call_analyses ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own calls
CREATE POLICY "Users can view own calls"
  ON call_analyses FOR SELECT
  USING (auth.uid() = user_id);
```

### Rate Limiting

Current limits (configurable in .env):
- Default: 10 requests per 60 seconds
- Production recommendation: Use Redis for distributed rate limiting

## Monitoring

Watch for suspicious activity:

1. **Supabase Dashboard:**
   - Monitor API usage
   - Check for unusual patterns

2. **OpenAI Usage:**
   - Track token consumption
   - Set spending limits

3. **Application Logs:**
   - Review failed authentication attempts
   - Monitor rate limit violations

## Security Best Practices

1. ✅ Use strong, unique API keys
2. ✅ Keep dependencies updated
3. ✅ Enable HTTPS in production
4. ✅ Implement proper CORS policies
5. ✅ Use environment-specific keys
6. ✅ Regular security audits
7. ✅ Monitor API usage patterns
8. ✅ Implement request logging
9. ✅ Set up alerting for anomalies
10. ✅ Regular key rotation

## Contact

For security issues, DO NOT create public GitHub issues.
Contact the team directly.

---

**Last Updated:** 2026-04-03
**Security Level:** Production-Ready
