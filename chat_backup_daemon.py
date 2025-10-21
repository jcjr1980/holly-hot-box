#!/usr/bin/env python3
"""
Holly Hot Box - Chat Backup Daemon
Backs up chat sessions every 30 seconds to JSON files
"""
import os
import sys
import django
import json
import time
from datetime import datetime
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hbb_core.settings')
django.setup()

from brain_chat.models import ChatSession, ChatMessage, ChatBackup


class ChatBackupDaemon:
    """Backs up chat sessions every 30 seconds"""
    
    def __init__(self, interval_seconds=30):
        self.interval_seconds = interval_seconds
        self.backup_dir = Path(__file__).parent / 'chat_backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        self.pid_file = Path(__file__).parent / 'chat_backup.pid'
        self.log_file = Path(__file__).parent / 'chat_backup.log'
        
        # Save PID
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.log(f"🚀 Chat Backup Daemon started - PID: {os.getpid()}")
        self.log(f"📁 Backup directory: {self.backup_dir}")
        self.log(f"⏱️  Backup interval: {self.interval_seconds} seconds")
    
    def log(self, message):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
    
    def backup_all_sessions(self):
        """Backup all active chat sessions"""
        try:
            sessions = ChatSession.objects.filter(is_active=True)
            
            for session in sessions:
                self.backup_session(session)
            
            self.log(f"✅ Backed up {sessions.count()} active sessions")
            
        except Exception as e:
            self.log(f"❌ Error backing up sessions: {e}")
    
    def backup_session(self, session):
        """Backup a single session"""
        try:
            # Get all messages
            messages = session.messages.all().order_by('created_at')
            
            backup_data = {
                'session_id': session.id,
                'user': session.user.username,
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'message_count': messages.count(),
                'messages': []
            }
            
            # Add all messages
            for msg in messages:
                backup_data['messages'].append({
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'llm_provider': msg.llm_provider,
                    'tokens_used': msg.tokens_used,
                    'response_time_ms': msg.response_time_ms,
                    'created_at': msg.created_at.isoformat(),
                    'metadata': msg.metadata
                })
            
            # Save to database
            ChatBackup.objects.create(
                session=session,
                backup_data=backup_data,
                message_count=messages.count()
            )
            
            # Save to JSON file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.backup_dir / f"session_{session.id}_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            self.log(f"💾 Session {session.id}: {messages.count()} messages → {filename.name}")
            
        except Exception as e:
            self.log(f"❌ Error backing up session {session.id}: {e}")
    
    def run(self):
        """Main daemon loop"""
        self.log("🔄 Starting backup loop...")
        
        try:
            while True:
                self.backup_all_sessions()
                time.sleep(self.interval_seconds)
        
        except KeyboardInterrupt:
            self.log("⏹️  Daemon stopped by user")
        
        except Exception as e:
            self.log(f"❌ Daemon crashed: {e}")
        
        finally:
            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            self.log("👋 Daemon shut down")


if __name__ == "__main__":
    daemon = ChatBackupDaemon(interval_seconds=30)
    daemon.run()

