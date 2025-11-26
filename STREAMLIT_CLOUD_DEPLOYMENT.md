# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites
1. GitHub account with repository: https://github.com/Kaustab2003/FinCA_AI
2. Streamlit Cloud account: https://streamlit.io/cloud
3. Supabase database configured

## Step-by-Step Deployment

### 1️⃣ Prepare Your Repository
```bash
# Ensure all files are committed
git status
git add .
git commit -m "chore: Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2️⃣ Sign Up / Login to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click **"Sign in"** with GitHub
3. Authorize Streamlit to access your repositories

### 3️⃣ Deploy Your App
1. Click **"New app"** button
2. Fill in the form:
   - **Repository**: `Kaustab2003/FinCA_AI`
   - **Branch**: `main`
   - **Main file path**: `src/ui/app_integrated.py`
   - **App URL**: Choose your custom subdomain (e.g., `finca-ai`)

3. Click **"Deploy"**

### 4️⃣ Configure Secrets
1. In your deployed app dashboard, click **⚙️ Settings**
2. Go to **"Secrets"** section
3. Copy the content from `.streamlit/secrets.toml`
4. Replace placeholders with actual values:

```toml
# REQUIRED SECRETS (Minimum to run)
SUPABASE_URL = "https://giqiefidzqjybzqvkfoo.supabase.co"
SUPABASE_ANON_KEY = "your-actual-supabase-anon-key"

# OPTIONAL (for AI features)
OPENAI_API_KEY = "sk-..."
GEMINI_API_KEY = "AIza..."

# Application Settings
APP_ENV = "production"
DEBUG_MODE = false
```

5. Click **"Save"**

### 5️⃣ Get Your Supabase Credentials
1. Go to https://supabase.com/dashboard
2. Select your project: `giqiefidzqjybzqvkfoo`
3. Click **⚙️ Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **Project API Key** (anon, public) → `SUPABASE_ANON_KEY`

### 6️⃣ Verify Deployment
1. Wait for app to build (2-3 minutes)
2. Once deployed, you'll get a URL like: `https://finca-ai.streamlit.app`
3. Test all features:
   - ✅ Dashboard loads
   - ✅ Database connections work
   - ✅ All 5 real-life features accessible
   - ✅ Forms submit successfully

### 7️⃣ Monitor Your App
- **Logs**: Click "Manage app" → "Logs" to see real-time logs
- **Reboot**: If app freezes, click "Reboot app"
- **Update**: Push to `main` branch to auto-deploy updates

## 🔒 Security Checklist

### ✅ Secrets Protected
- [ ] `.streamlit/secrets.toml` is in `.gitignore`
- [ ] No secrets committed to GitHub
- [ ] Secrets configured in Streamlit Cloud dashboard
- [ ] Environment variables not hardcoded in code

### ✅ Database Security
- [ ] Supabase Row Level Security (RLS) enabled
- [ ] RLS policies configured for all tables
- [ ] Service role key NOT used (use anon key only)
- [ ] SSL/TLS enabled for database connections

### ✅ API Keys
- [ ] OpenAI API key has spending limits set
- [ ] Gemini API key has rate limits configured
- [ ] No API keys exposed in client-side code

## 📊 Resource Limits (Free Tier)

Streamlit Cloud Free Tier:
- **Memory**: 1 GB RAM
- **CPU**: Shared
- **Apps**: 1 public app
- **Sleep time**: Apps sleep after 7 days of inactivity
- **Concurrent users**: ~100 (recommended)

**Tips to stay within limits:**
- Use `@st.cache_data` for expensive computations
- Optimize database queries (limit results)
- Use Plotly instead of heavy visualization libraries
- Compress large data files

## 🐛 Troubleshooting

### App Won't Start
```bash
# Check logs in Streamlit Cloud dashboard
# Common issues:
# 1. Missing dependencies in requirements.txt
# 2. Incorrect file path in deployment settings
# 3. Missing secrets
```

### Database Connection Errors
```python
# Verify secrets are set correctly
# Test connection:
import streamlit as st
st.write(st.secrets["SUPABASE_URL"])  # Should NOT be empty
```

### Import Errors
```bash
# Ensure requirements.txt includes:
streamlit
supabase
python-dotenv
plotly
pandas
```

### Memory Errors
```python
# Reduce data loading:
# Instead of: SELECT *
# Use: SELECT * LIMIT 100
```

## 🔄 Continuous Deployment

Your app auto-deploys when you push to `main`:

```bash
# Make changes
git add .
git commit -m "feat: New feature"
git push origin main

# Streamlit Cloud automatically:
# 1. Detects push
# 2. Rebuilds app
# 3. Deploys new version (2-3 min)
```

## 📱 Custom Domain (Pro Feature)

To use your own domain (e.g., `app.finca.ai`):
1. Upgrade to Streamlit Cloud Pro
2. Add CNAME record: `app.finca.ai` → `your-app.streamlit.app`
3. Configure in Streamlit Cloud dashboard

## 🎨 Branding

Update `.streamlit/config.toml` for custom theme:
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## 📞 Support

- **Streamlit Docs**: https://docs.streamlit.io/
- **Community Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: https://github.com/Kaustab2003/FinCA_AI/issues

## ✅ Deployment Checklist

Before going live:
- [ ] All secrets configured in Streamlit Cloud
- [ ] Database tables created in Supabase
- [ ] RLS policies applied
- [ ] All features tested in production
- [ ] Error handling verified
- [ ] Performance optimized
- [ ] Monitoring enabled
- [ ] Backup strategy in place
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active

---

## 🎉 You're Live!

Your app is now accessible at: `https://your-app-name.streamlit.app`

Share with users: 
```
🚀 FinCA AI is now live!
👉 https://finca-ai.streamlit.app
```

**Enjoy your deployed app!** 🎊
