# 🚀 FinCA AI - Deployment Guide

## Quick Deploy to Streamlit Cloud (5 Minutes)

### Step 1: Prepare Repository
```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit: FinCA AI v1.0"

# Create GitHub repository
# Go to github.com/new
# Name: finca-ai
# Public or Private
# Don't initialize with README

# Push code
git remote add origin https://github.com/YOUR_USERNAME/finca-ai.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub
3. **Click**: "New app"
4. **Configure**:
   - Repository: `YOUR_USERNAME/finca-ai`
   - Branch: `main`
   - Main file path: `src/ui/streamlit_app.py`
   - App URL: `finca-ai` (or custom name)

5. **Advanced Settings** → **Secrets**:
   ```toml
   # Copy from your .env file
   APP_NAME = "FinCA_AI"
   DEBUG = false
   
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_ANON_KEY = "your_anon_key"
   SUPABASE_SERVICE_KEY = "your_service_key"
   
   OPENAI_API_KEY = "sk-your_key"
   ENCRYPTION_KEY = "your_fernet_key"
   
   LANGCHAIN_TRACING_V2 = true
   LANGCHAIN_API_KEY = "your_key"
   LANGCHAIN_PROJECT = "finca-ai-prod"
   
   NEWS_API_KEY = "your_key"
   ALPHAVANTAGE_API_KEY = "your_key"
   ```

6. **Click**: "Deploy!"
7. **Wait**: ~2-3 minutes
8. **Done**: Your app is live at `https://finca-ai.streamlit.app`

---

## Production Deployment (Docker)

### Option 1: Docker Compose

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./src:/app/src
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Deploy**:
```bash
docker-compose up -d
```

---

## Cloud Providers

### AWS (EC2 + ALB)

**1. Launch EC2 Instance**:
```bash
# t3.medium (2 vCPU, 4GB RAM)
# Ubuntu 22.04 LTS
# Security Group: Allow 8501, 80, 443
```

**2. Install Dependencies**:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx -y

# Clone repo
git clone https://github.com/YOUR_USERNAME/finca-ai.git
cd finca-ai

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Create Systemd Service**:
```ini
# /etc/systemd/system/finca.service
[Unit]
Description=FinCA AI Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/finca-ai
Environment="PATH=/home/ubuntu/finca-ai/venv/bin"
ExecStart=/home/ubuntu/finca-ai/venv/bin/streamlit run src/ui/streamlit_app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

**4. Start Service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable finca
sudo systemctl start finca
```

**5. Configure Nginx**:
```nginx
# /etc/nginx/sites-available/finca
server {
    listen 80;
    server_name finca.ai www.finca.ai;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**6. Enable SSL (Let's Encrypt)**:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d finca.ai -d www.finca.ai
```

---

### GCP (Cloud Run)

**1. Build Container**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/finca-ai
```

**2. Deploy**:
```bash
gcloud run deploy finca-ai \
  --image gcr.io/PROJECT_ID/finca-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat .env | tr '\n' ',')"
```

---

### Azure (Container Instances)

**1. Create Resource Group**:
```bash
az group create --name finca-rg --location eastus
```

**2. Deploy Container**:
```bash
az container create \
  --resource-group finca-rg \
  --name finca-ai \
  --image your-registry/finca-ai:latest \
  --dns-name-label finca-ai \
  --ports 8501 \
  --environment-variables $(cat .env | xargs)
```

---

## Database Setup (Supabase)

### Already Configured ✅
- Your Supabase project is ready
- 25 tables deployed via schema.sql
- RLS policies active
- Indexes optimized

### Verify Setup:
1. Go to Supabase Dashboard
2. Check "Table Editor" - should see 25 tables
3. Test query:
   ```sql
   SELECT version FROM schema_version;
   -- Should return: 1.0.0
   ```

---

## Monitoring & Observability

### Sentry (Error Tracking)

**Already configured in settings.py** ✅

Monitor at: https://sentry.io/organizations/YOUR_ORG/issues/

### LangSmith (AI Tracing)

**Already configured** ✅

View traces at: https://smith.langchain.com/

### Custom Metrics

Add to `src/utils/metrics.py`:
```python
import prometheus_client as prom

# Metrics
request_count = prom.Counter('finca_requests_total', 'Total requests')
response_time = prom.Histogram('finca_response_seconds', 'Response time')
active_users = prom.Gauge('finca_active_users', 'Active users')
```

---

## Performance Optimization

### 1. Caching
```python
# Add to streamlit_app.py
@st.cache_data(ttl=3600)
def load_user_data(user_id):
    # Expensive DB query
    return data

@st.cache_resource
def get_ai_agent():
    # Expensive initialization
    return agent
```

### 2. Database Indexes
```sql
-- Already added in schema.sql ✅
CREATE INDEX idx_budgets_user_month ON budgets(user_id, month DESC);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
```

### 3. API Rate Limiting
```python
# src/utils/rate_limiter.py
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        cutoff = now - self.window
        
        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        return False
```

---

## Security Checklist

### Before Production
- [ ] Change all API keys
- [ ] Rotate encryption key
- [ ] Enable Supabase RLS on all tables
- [ ] Set up firewall rules
- [ ] Enable HTTPS (SSL certificate)
- [ ] Add rate limiting
- [ ] Set up audit logs
- [ ] Enable 2FA for admin accounts
- [ ] Configure CORS properly
- [ ] Review .env (no secrets in git!)

### Secrets Management
```bash
# Use environment-specific .env files
.env.development
.env.staging
.env.production

# Never commit .env!
echo ".env*" >> .gitignore
```

---

## Backup & Disaster Recovery

### Database Backups (Supabase)

Supabase Pro automatically backs up daily. To manually backup:

```bash
# Export database
pg_dump -h db.PROJECT_REF.supabase.co \
  -U postgres \
  -d postgres \
  -F c -f finca_backup_$(date +%Y%m%d).dump

# Restore
pg_restore -h db.PROJECT_REF.supabase.co \
  -U postgres \
  -d postgres \
  finca_backup_20250126.dump
```

### Code Backups
```bash
# GitHub already serves as backup
# But also:
git bundle create finca_backup.bundle --all
```

---

## Scaling Strategy

### Phase 1 (0-1K users)
- Streamlit Cloud free tier
- Supabase free tier
- Works perfectly ✅

### Phase 2 (1K-10K users)
- Streamlit Cloud Pro ($250/month)
- Supabase Pro ($25/month)
- CDN for static assets

### Phase 3 (10K-100K users)
- AWS/GCP with auto-scaling
- Supabase Team ($599/month)
- Redis for caching
- Load balancer

### Phase 4 (100K+ users)
- Kubernetes cluster
- Dedicated PostgreSQL (RDS/Cloud SQL)
- Microservices architecture
- Multi-region deployment

---

## Cost Estimation

### Startup (0-1K users)
```
Streamlit Cloud: Free
Supabase: Free (50K API requests/month)
OpenAI: ~$50/month (20 queries/user/month)
Domain: $12/year
Total: ~$50/month
```

### Scale (10K users)
```
Streamlit Cloud Pro: $250
Supabase Pro: $25
OpenAI: ~$500 (optimized caching)
AWS/CDN: $100
Monitoring: $50
Total: ~$925/month
Revenue: $50K/month (10K × $5)
Margin: 98% 🚀
```

---

## Troubleshooting

### Issue: App crashes on startup
```bash
# Check logs
streamlit run src/ui/streamlit_app.py --logger.level=debug

# Verify dependencies
pip install -r requirements.txt --upgrade
```

### Issue: Slow performance
```python
# Add caching
@st.cache_data
def expensive_function():
    pass

# Use connection pooling
@st.cache_resource
def get_db_client():
    return DatabaseClient.get_client()
```

### Issue: High OpenAI costs
```python
# Cache AI responses
@st.cache_data(ttl=3600)
def get_ai_response(query, user_context):
    return ai_agent.process(query, user_context)

# Use cheaper models for simple tasks
supervisor = SupervisorAgent(model="gpt-3.5-turbo")  # Routing only
```

---

## 🎉 You're Ready!

Your FinCA AI is now:
✅ Deployed to cloud
✅ Monitored for errors
✅ Secured with best practices
✅ Optimized for performance
✅ Ready to scale

**Live URL**: Update README.md with your deployment URL

**Next**: Share with users and iterate based on feedback! 🚀

---

## 📞 Support

- **Streamlit Issues**: https://discuss.streamlit.io
- **Supabase Help**: https://supabase.com/docs
- **OpenAI API**: https://platform.openai.com/docs

**Good luck with your launch!** 🎊
