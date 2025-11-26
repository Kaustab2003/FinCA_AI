# Security Policy 🔒

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report

1. **Email**: security@finca-ai.com
2. **Subject**: [SECURITY] Brief description
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 24-48 hours
- **Initial Assessment**: Within 5 business days
- **Fix Timeline**: Depends on severity
  - Critical: 1-2 days
  - High: 3-7 days
  - Medium: 7-14 days
  - Low: Next release cycle

### Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide regular updates on the fix progress
- We will credit you in the security advisory (if desired)
- We request you keep the issue confidential until we release a fix

## Security Best Practices

### For Users

1. **Environment Variables**
   - Never commit `.env` file to Git
   - Use strong, unique API keys
   - Rotate keys regularly (every 90 days)
   - Use different keys for dev/staging/prod

2. **API Keys**
   ```bash
   # Good ✅
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx  # In .env only
   
   # Bad ❌
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx  # In source code
   ```

3. **Database**
   - Use Supabase Row Level Security (RLS)
   - Enable MFA on Supabase account
   - Regularly backup data
   - Use service key only on server-side

4. **Passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Use password manager
   - Enable 2FA where available

### For Contributors

1. **Code Review**
   - Never merge your own PR
   - All PRs require 1 approval
   - Run security checks before merging

2. **Dependencies**
   - Keep dependencies updated
   - Run `pip audit` regularly
   - Review dependency security advisories

3. **Sensitive Data**
   - Never log sensitive information
   - Sanitize user inputs
   - Use encryption for sensitive data
   - Follow least privilege principle

4. **Testing**
   ```python
   # Good ✅
   def test_login_with_invalid_token():
       response = client.post("/login", headers={"token": "invalid"})
       assert response.status_code == 401
       assert "token" not in response.json()  # Don't leak token
   
   # Bad ❌
   def test_login():
       response = client.post("/login", 
           headers={"token": "actual_production_token"})  # Don't use real tokens!
   ```

## Known Security Considerations

### Data Storage

- **User Financial Data**: Encrypted at rest in Supabase
- **API Keys**: Stored in environment variables only
- **Chat History**: Can be disabled by user
- **Logs**: Sanitized, no PII

### Third-Party Services

We use the following third-party services:

| Service | Purpose | Data Shared |
|---------|---------|-------------|
| Groq/DeepSeek | AI Inference | User queries only |
| Supabase | Database | User profile, financial data |
| Sentry (optional) | Error tracking | Error logs (no PII) |

### Compliance

- **GDPR**: Users can request data deletion
- **Indian IT Act**: Compliant with 2000 Act
- **Data Retention**: Configurable (default 730 days)

## Security Checklist

Before deploying:

- [ ] All secrets in `.env` (not in code)
- [ ] `.env` in `.gitignore`
- [ ] Supabase RLS policies enabled
- [ ] API rate limiting configured
- [ ] CORS properly configured
- [ ] HTTPS enabled in production
- [ ] Regular backups scheduled
- [ ] Error messages don't leak sensitive info
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)

## Vulnerability Disclosure Examples

### Critical: SQL Injection
```
Severity: Critical
Description: Unparameterized SQL query in budget service
Impact: Database compromise, data theft
Fix: Use parameterized queries
Status: Fixed in v1.0.1
```

### High: API Key Exposure
```
Severity: High
Description: OpenAI key visible in browser console
Impact: API key theft, unauthorized usage
Fix: Move key to server-side only
Status: Fixed in v1.0.2
```

### Medium: Weak Password Policy
```
Severity: Medium
Description: Allows passwords < 8 characters
Impact: Brute force attacks easier
Fix: Enforce 12+ character minimum
Status: Fixed in v1.0.3
```

## Security Updates

Subscribe to security advisories:
- Watch this repository for security advisories
- Follow us on Twitter: @FinCA_AI
- Join our Discord security channel

## Hall of Fame 🏆

We thank the following researchers for responsible disclosure:

*(No reports yet)*

## Contact

- **Security Email**: security@finca-ai.com
- **PGP Key**: [Download](https://finca-ai.com/pgp-key.txt)
- **Response Time**: 24-48 hours

---

**Security is everyone's responsibility. Thank you for helping keep FinCA AI safe!** 🛡️
