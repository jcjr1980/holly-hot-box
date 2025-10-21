# 🔥 Holly Hot Box (HBB)

## Multi-LLM Brain Child System

Holly Hot Box is an advanced AI orchestration platform that combines **6 powerful LLMs** to provide the best collaborative responses for complex tasks.

### 🤖 The Power Duo Leadership

- **⭐ Google Gemini Tier 3** - PRIMARY STRATEGIST (Premium, Advanced Thinking)
- **💎 DeepSeek Reasoner** - DEEP ANALYTICAL THINKING (Ultra Cost-Effective, V3.2-Exp)

### Supporting Team

- **OpenAI GPT-4o** - Creative Director & General Intelligence
- **Anthropic Claude** - Strategy & Writing
- **xAI Grok** - Market Pulse & Social Intelligence
- **Hugging Face (Llama 3)** - Johnny's Digital Clone

### ✨ Features

1. **Multi-Mode Operation**
   - **⚡ Power Duo**: Gemini Tier 3 + DeepSeek Reasoner working together (RECOMMENDED!)
   - **Consensus**: All 6 LLMs collaborate, led by Gemini & DeepSeek
   - **⭐ Gemini Only**: Premium Gemini Tier 3 for fast, high-quality responses
   - **💎 DeepSeek Only**: Cost-effective deep reasoning and analysis
   - **Best**: Gemini evaluates all responses and picks the best
   - **All 6**: Shows all responses side-by-side for comparison

2. **Auto-Backup System**
   - Chats backed up every 30 seconds to JSON
   - Database backups with full message history
   - Easy recovery and export

3. **2FA Security**
   - Secure login with username, password, and 2FA code
   - Session management
   - User profiles

4. **Beautiful UI**
   - Modern, responsive chat interface
   - Real-time message streaming
   - Session management sidebar
   - Mode switching on the fly

### 🚀 Deployment

**Domain**: hbb.johnnycollins.io

**Environment Variables Required**:
```bash
SECRET_KEY=your-django-secret-key
DATABASE_URL=postgresql://...
DEBUG=False
ALLOWED_HOSTS=hbb.johnnycollins.io

# Authentication
HBB_USERNAME=jcjr1980
HBB_PASSWORD=@cc0r-D69_8123$!
HBB_2FA_CODE=267769

# LLM API Keys
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
DEEPSEEK_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
GROK_API_KEY=xai-...
HUGGINGFACE_API_KEY=hf_...

# Optional
NOTION_API_KEY=ntn_...
PINECONE_API_KEY=pcsk_...
```

### 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/holly_hot_box.git
cd holly_hot_box

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Start chat backup daemon (optional)
python chat_backup_daemon.py &
```

### 🎯 Usage

1. Navigate to `http://hbb.johnnycollins.io`
2. Login with credentials + 2FA code
3. Start chatting!
4. Switch modes using the mode selector
5. View all LLM responses in parallel mode
6. Sessions auto-save every 30 seconds

### 📊 Architecture

```
Holly Hot Box
├── Django Backend
│   ├── brain_chat (main app)
│   │   ├── models.py (ChatSession, ChatMessage, etc.)
│   │   ├── views.py (chat endpoints)
│   │   ├── llm_orchestrator.py (multi-LLM logic)
│   │   └── templates/
│   └── hbb_core (project settings)
├── chat_backup_daemon.py (30-second backups)
├── requirements.txt
├── Procfile (Railway deployment)
└── railway.toml
```

### 🔧 API Endpoints

- `GET /` - Chat home (requires auth)
- `POST /login/` - Login with 2FA
- `POST /send-message/` - Send message to LLMs
- `GET /new-session/` - Create new chat session
- `GET /session/<id>/` - Load specific session
- `GET /health/` - Health check

### 💾 Database Models

- **ChatSession** - Chat conversation container
- **ChatMessage** - Individual messages
- **LLMResponse** - Individual LLM responses (for consensus mode)
- **ChatBackup** - 30-second backup snapshots
- **UserProfile** - Extended user data with 2FA

### 🎨 Tech Stack

- **Backend**: Django 5.1.1
- **Database**: PostgreSQL (Railway)
- **LLMs**: OpenAI, Gemini, Claude, DeepSeek, Grok, HuggingFace
- **Deployment**: Railway
- **Static Files**: WhiteNoise
- **Security**: 2FA, CSRF protection, session management

### 📝 License

Proprietary - SearchAI / Johnny Collins

### 👨‍💻 Author

**Johnny Collins** - SearchAI  
Domain: hbb.johnnycollins.io  
Created: October 21, 2025

---

**Status**: 🚀 Production Ready

# Force deployment Tue Oct 21 10:30:31 EDT 2025
