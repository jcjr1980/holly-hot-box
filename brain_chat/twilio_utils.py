"""
Holly Hot Box - Twilio SMS Utilities
Send SMS notifications and alerts
"""
import os
import logging
from twilio.rest import Client
from typing import Optional

logger = logging.getLogger(__name__)


class TwilioSMS:
    """Handle Twilio SMS operations"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.enabled = os.getenv('TWILIO_SMS_ENABLED', 'true').lower() == 'true'
        
        if self.account_sid and self.auth_token and self.phone_number and self.enabled:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio SMS client initialized successfully")
            except Exception as e:
                logger.error(f"Twilio init error: {e}")
                self.client = None
        else:
            self.client = None
            if not self.enabled:
                logger.info("Twilio SMS is disabled")
            else:
                logger.warning("Twilio credentials not found")
    
    def send_sms(self, to_number: str, message: str) -> dict:
        """
        Send an SMS message
        
        Args:
            to_number: Phone number in E.164 format (e.g., +13055390208)
            message: Message text to send
            
        Returns:
            dict: Result with status and message SID or error
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not initialized"
            }
        
        try:
            message = self.client.messages.create(
                from_=self.phone_number,
                to=to_number,
                body=message
            )
            
            logger.info(f"SMS sent successfully to {to_number}. SID: {message.sid}")
            
            return {
                "success": True,
                "message_sid": message.sid,
                "to": to_number,
                "from": self.phone_number,
                "status": message.status
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_llm_success_notification(self, to_number: str) -> dict:
        """Send Holly Hot Box LLM success notification"""
        message = "🔥 Holly Hot Box - All 6 LLM's Are Working! 🎉"
        return self.send_sms(to_number, message)
    
    def send_project_notification(self, to_number: str, project_name: str, notification_type: str = "update") -> dict:
        """Send project-related notification"""
        messages = {
            "update": f"📝 Holly Hot Box: Update on project '{project_name}'",
            "complete": f"✅ Holly Hot Box: Project '{project_name}' completed!",
            "alert": f"⚠️ Holly Hot Box: Alert for project '{project_name}'",
        }
        
        message = messages.get(notification_type, f"Holly Hot Box: Notification about '{project_name}'")
        return self.send_sms(phone_number, message)