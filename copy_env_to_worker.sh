#!/bin/bash
# Copy environment variables from holly-hot-box to holly-hot-box-worker

echo "🔧 Copying environment variables to worker service..."

# Switch to worker service
railway service holly-hot-box-worker

# Add all required variables
echo "Adding DATABASE_URL..."
railway variables --set DATABASE_URL='${{Postgres-OEMK.DATABASE_URL}}'

echo "Adding REDIS_URL..."
railway variables --set REDIS_URL='${{Redis.REDIS_URL}}'

echo "Adding GEMINI_API_KEY..."
railway variables --set GEMINI_API_KEY='${{holly-hot-box.GEMINI_API_KEY}}'

echo "Adding OPENAI_API_KEY..."
railway variables --set OPENAI_API_KEY='${{holly-hot-box.OPENAI_API_KEY}}'

echo "Adding CLAUDE_API_KEY..."
railway variables --set CLAUDE_API_KEY='${{holly-hot-box.CLAUDE_API_KEY}}'

echo "Adding DEEPSEEK_API_KEY..."
railway variables --set DEEPSEEK_API_KEY='${{holly-hot-box.DEEPSEEK_API_KEY}}'

echo "Adding GROK_API_KEY..."
railway variables --set GROK_API_KEY='${{holly-hot-box.GROK_API_KEY}}'

echo "Adding HUGGINGFACE_API_KEY..."
railway variables --set HUGGINGFACE_API_KEY='${{holly-hot-box.HUGGINGFACE_API_KEY}}'

echo "Adding HHB_PASSWORD..."
railway variables --set HHB_PASSWORD='${{holly-hot-box.HHB_PASSWORD}}'

echo "Adding DJANGO_SECRET_KEY..."
railway variables --set DJANGO_SECRET_KEY='${{holly-hot-box.DJANGO_SECRET_KEY}}'

echo "✅ All variables copied! Worker will restart automatically."

