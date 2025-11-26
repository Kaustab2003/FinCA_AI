# Fix OpenAI API Key Issue

## Problem
The AI chat is showing error messages because the OpenAI API key may be invalid or malformed.

## Solution

### Step 1: Get a Valid OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)

### Step 2: Update .env File

Replace the current OPENAI_API_KEY in `.env`:

```env
# OLD (possibly invalid)
OPENAI_API_KEY=sk-sk-svcacct-ikOnpx6iUci...

# NEW (get from OpenAI dashboard)
OPENAI_API_KEY=sk-proj-YOUR_NEW_KEY_HERE
```

### Step 3: Restart Application

```powershell
# Stop current app
Stop-Process -Name streamlit -Force

# Restart
python -m streamlit run src/ui/app_integrated.py --server.port=8503
```

## Alternative: Test Without OpenAI (Mock Responses)

If you don't have an OpenAI key right now, I can create mock responses for demo purposes.

## Check Current Error

With the updated error handling, **try asking a question in the chat now** and you'll see the actual error message which will tell us exactly what's wrong!

The error message will appear in the chat instead of the generic "couldn't process" message.

## Common OpenAI Errors

1. **Invalid API Key**: "Incorrect API key provided"
   - Solution: Get new key from OpenAI dashboard

2. **No Credits**: "You exceeded your current quota"
   - Solution: Add billing info to OpenAI account

3. **Network Error**: "Connection timeout"
   - Solution: Check internet connection

4. **Rate Limit**: "Rate limit exceeded"
   - Solution: Wait a moment and try again

## Next Steps

1. **Try the chat now** - It will show the actual error
2. Based on error, either:
   - Update OpenAI API key in `.env`
   - OR I can create mock responses for demo
3. Restart the app
4. Test again!
