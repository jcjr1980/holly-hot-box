# 🚀 Holly Hot Box - Railway Deployment Guide

## Pre-Deployment Checklist

✅ Project Structure Created  
✅ All 6 LLMs Integrated  
✅ 2FA Authentication Configured  
✅ Chat Backup Daemon Ready  
✅ Beautiful UI Complete  
✅ Git Repository Initialized  

---

## Step 1: Create GitHub Repository (Optional but Recommended)

```bash
# Create a new repository on GitHub, then:
cd /Users/johnny/Projects/holly_hot_box
git remote add origin https://github.com/jcjr1980/holly-hot-box.git
git push -u origin main
```

---

## Step 2: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose the `holly-hot-box` repository
5. Railway will auto-detect Django and deploy

### Option B: Deploy from Local Directory
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from Local Directory"
4. Select `/Users/johnny/Projects/holly_hot_box`
5. Railway will auto-detect Django and deploy

---

## Step 3: Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically inject `DATABASE_URL` into your app

---

## Step 4: Configure Environment Variables

In Railway Project Settings → Variables, add:

### Required Variables:
```bash
SECRET_KEY=holly-hot-box-production-secret-key-change-this-to-random-string
DEBUG=False
ALLOWED_HOSTS=hbb.johnnycollins.io

# Authentication (from your requirements)
HBB_USERNAME=jcjr1980
HBB_PASSWORD=@cc0r-D69_8123$!
HBB_2FA_CODE=267769

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key-here

GEMINI_API_KEY=your-gemini-api-key-here

DEEPSEEK_API_KEY=your-deepseek-api-key-here

CLAUDE_API_KEY=your-anthropic-api-key-here

GROK_API_KEY=your-grok-api-key-here

HUGGINGFACE_API_KEY=your-huggingface-api-key-here
```

### Optional Variables:
```bash
NOTION_API_KEY=your-notion-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
```

---

## Step 5: Configure Custom Domain

1. In Railway Project → Settings → Domains
2. Click "Add Domain"
3. Enter: `hbb.johnnycollins.io`
4. Railway will provide DNS instructions
5. Add CNAME record in your DNS provider:
   ```
   CNAME  hbb  ->  [your-railway-app].up.railway.app
   ```
6. Wait for DNS propagation (5-30 minutes)

---

## Step 6: Verify Deployment

Once deployed, check:

1. **Health Check**: `https://hbb.johnnycollins.io/health/`
   - Should return: `{"status": "healthy", "service": "Holly Hot Box"}`

2. **Login Page**: `https://hbb.johnnycollins.io/login/`
   - Should show the beautiful login form

3. **Admin**: `https://hbb.johnnycollins.io/admin/`
   - Django admin should be accessible

---

## Step 7: Create Admin User (Optional)

Run in Railway CLI or web console:

```bash
railway run python manage.py createsuperuser
```

Or use the Railway web shell:
1. Go to Project → Service → Shell
2. Run: `python manage.py createsuperuser`

---

## Step 8: Test All Features

### Login Test:
- Username: `jcjr1980`
- Password: `@cc0r-D69_8123$!`
- 2FA Code: `267769`

### Chat Test:
1. Send a test message
2. Try all 4 modes:
   - Consensus (all LLMs collaborate)
   - Fastest (quickest response)
   - Best (GPT-4o picks best)
   - Parallel (see all responses)

### Backup Test:
- Send a few messages
- Wait 30 seconds
- Check that backups are created in database

---

## Step 9: Monitor & Logs

### View Logs:
```bash
# From local machine with Railway CLI
railway logs

# Or view in Railway dashboard
Project → Service → Deployments → [Latest] → Logs
```

### Check Database:
```bash
railway run python manage.py dbshell
```

---

## Troubleshooting

### Issue: Static files not loading
**Solution**: Make sure WhiteNoise is configured (it already is!)

### Issue: Database connection errors
**Solution**: Verify `DATABASE_URL` is injected by Railway PostgreSQL

### Issue: LLM errors
**Solution**: Check that all API keys are set correctly in environment variables

### Issue: 500 errors
**Solution**: Check Railway logs for detailed error messages

---

## Post-Deployment Tasks

1. **Test backup daemon locally**:
   ```bash
   cd /Users/johnny/Projects/holly_hot_box
   python chat_backup_daemon.py
   ```

2. **Monitor API usage**:
   - OpenAI: https://platform.openai.com/usage
   - Gemini: https://aistudio.google.com/
   - Claude: https://console.anthropic.com/
   - DeepSeek: https://platform.deepseek.com/
   - Grok: https://x.ai/
   - HuggingFace: https://huggingface.co/settings/tokens

3. **Set up monitoring** (optional):
   - Add Sentry for error tracking
   - Add New Relic for performance monitoring
   - Set up Railway alerts

---

## Backup & Recovery

### Database Backup:
Railway automatically backs up PostgreSQL databases.

### Chat Backups:
All chats are backed up to:
- Database (`ChatBackup` model)
- JSON files (if daemon is running)

### Restore from Backup:
```bash
# Export all sessions
railway run python manage.py dumpdata brain_chat > backup.json

# Restore
railway run python manage.py loaddata backup.json
```

---

## Scaling Considerations

### Current Limits:
- Free tier supports up to 500 hours/month
- Database: 500MB storage
- Bandwidth: Unlimited

### Upgrade to Pro:
- Railway Pro: $20/month
- More resources
- Priority support

---

## Security Recommendations

1. **Change SECRET_KEY** in production
2. **Rotate API keys** regularly (every 90 days)
3. **Enable 2FA** on all API provider accounts
4. **Monitor usage** to detect anomalies
5. **Use HTTPS only** (Railway handles this)
6. **Regular backups** (automated with daemon)

---

## Quick Commands

```bash
# View logs
railway logs

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Open shell
railway run python manage.py shell

# Database shell
railway run python manage.py dbshell

# Collect static files
railway run python manage.py collectstatic --noinput

# Check deployment status
railway status
```

---

## Support & Contacts

- **Railway Support**: https://railway.app/help
- **Project Owner**: Johnny Collins (jcjr1980)
- **Domain**: hbb.johnnycollins.io

---

## Deployment Timeline

1. **Create Railway Project**: 2 minutes
2. **Add PostgreSQL**: 1 minute
3. **Configure Environment Variables**: 5 minutes
4. **Initial Deployment**: 3-5 minutes
5. **Configure Domain**: 5-30 minutes (DNS propagation)
6. **Testing**: 10 minutes

**Total**: ~30-60 minutes

---

## Success Checklist

- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] All environment variables configured
- [ ] Domain configured (hbb.johnnycollins.io)
- [ ] Application deployed successfully
- [ ] Health check returns healthy
- [ ] Login works with 2FA
- [ ] Chat interface loads
- [ ] All 4 modes work (consensus, fastest, best, parallel)
- [ ] Messages are saved to database
- [ ] Sessions are created properly

---

**Status**: ✅ Ready for Deployment  
**Created**: October 21, 2025  
**Last Updated**: October 21, 2025

