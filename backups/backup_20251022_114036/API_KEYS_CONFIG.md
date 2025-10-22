# 🔑 Holly Hot Box API Keys Configuration

## Where to Add Your API Keys

### Option 1: Local Development (.env file)

Create a file called `.env` in the project root:

```bash
cd /Users/johnny/Projects/holly_hot_box
touch .env
```

Then add your API keys to the `.env` file:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,hbb.johnnycollins.io

# Database (optional for local - uses SQLite by default)
# DATABASE_URL=postgresql://user:password@localhost:5432/holly_hot_box

# Authentication
HBB_USERNAME=jcjr1980
HBB_PASSWORD=@cc0r-D69_8123$!
HBB_2FA_CODE=267769

# ⭐ LLM API Keys - POWER DUO
GEMINI_API_KEY=your-gemini-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# 🤖 Other LLM API Keys
OPENAI_API_KEY=your-openai-api-key-here

# 🆕 NEW ANTHROPIC KEY FOR HOLLY-HOT-BOX
CLAUDE_API_KEY=your-anthropic-api-key-here

GROK_API_KEY=your-grok-api-key-here

HUGGINGFACE_API_KEY=your-huggingface-api-key-here

# Optional - Knowledge Base
NOTION_API_KEY=your-notion-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
```

---

### Option 2: Railway Deployment (Production)

When deploying to Railway, add your keys in the **Railway Dashboard**:

1. Go to https://railway.app/dashboard
2. Select your Holly Hot Box project
3. Click on your service → **Variables** tab
4. Add each environment variable:

**Required Variables:**
- `SECRET_KEY` = (generate random string)
- `DEBUG` = False
- `ALLOWED_HOSTS` = hbb.johnnycollins.io
- `HBB_USERNAME` = jcjr1980
- `HBB_PASSWORD` = @cc0r-D69_8123$!
- `HBB_2FA_CODE` = 267769

**LLM API Keys:**
- `GEMINI_API_KEY` = your-gemini-api-key-here
- `DEEPSEEK_API_KEY` = your-deepseek-api-key-here
- `OPENAI_API_KEY` = your-openai-api-key-here
- `CLAUDE_API_KEY` = your-anthropic-api-key-here
- `GROK_API_KEY` = your-grok-api-key-here
- `HUGGINGFACE_API_KEY` = your-huggingface-api-key-here

---

## 📝 How to Get Your New Anthropic API Key

If you need to get your key from Anthropic Console:

1. Go to https://console.anthropic.com/
2. Login with your account
3. Navigate to **API Keys** section
4. Find the key named **"holly-hot-box"**
5. Copy the key (starts with `sk-ant-api03-...`)
6. Paste it into your `.env` file or Railway variables

---

## ✅ Testing Your API Keys

After adding the keys, test them locally:

```bash
cd /Users/johnny/Projects/holly_hot_box

# Test all LLM connections
python manage.py shell

# In the shell:
from brain_chat.llm_orchestrator import LLMOrchestrator
orchestrator = LLMOrchestrator()

# Test Anthropic/Claude
response, metadata = orchestrator.query_claude("Hello, can you hear me?")
print(response)
```

---

## 🔒 Security Notes

1. **NEVER commit `.env` file to git** (already in `.gitignore`)
2. **Keep API keys secret** - don't share publicly
3. **Rotate keys regularly** (every 90 days recommended)
4. **Monitor usage** on each provider's dashboard
5. **Set spending limits** on Anthropic/OpenAI/etc to avoid surprises

---

**Last Updated**: October 21, 2025  
**Project**: Holly Hot Box (hbb.johnnycollins.io)

