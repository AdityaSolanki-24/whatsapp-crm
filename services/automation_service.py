import logging
import random
from database.db import db
from models.instagram import InstagramAutomationRule, InstagramLead, InstagramAutomationLog, InstagramSettings
from services.instagram_service import InstagramService
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class AutomationService:
    def handle_incoming_comment(self, account_id: int, content_id: int, username: str, text: str) -> dict:
        """Evaluates incoming comments against active automation rules to auto-reply and generate leads."""
        settings = InstagramSettings.query.first()
        if settings and not settings.automation_enabled:
            return {"success": True, "replied": False, "reason": "global automation disabled"}

        rules = InstagramAutomationRule.query.filter_by(account_id=account_id, rule_type='comment_reply', is_active=True).all()
        rules += InstagramAutomationRule.query.filter_by(account_id=account_id, rule_type='lead_capture', is_active=True).all()
        
        for rule in rules:
            if rule.target_content_id and rule.target_content_id != content_id:
                continue
                
            keywords = [k.strip().lower() for k in rule.trigger_keywords.split(',')]
            matched_keyword = next((k for k in keywords if (rule.match_type == "exact" and text.lower() == k) or (rule.match_type == "contains" and k in text.lower())), None)
            
            if matched_keyword:
                # Randomize template if pipe separated
                templates = [t.strip() for t in rule.reply_template.split('|') if t.strip()]
                reply_msg = random.choice(templates) if templates else rule.reply_template
                
                lead_id = None
                if rule.rule_type in ['lead_capture', 'comment_reply']:
                    lead = InstagramLead.query.filter_by(account_id=account_id, username=username).first()
                    if not lead:
                        status = settings.default_lead_status if settings else "New Lead"
                        lead = InstagramLead(
                            account_id=account_id, username=username,
                            source_content_id=content_id, initial_comment=text,
                            matched_keyword=matched_keyword, pipeline_status=status
                        )
                        db.session.add(lead)
                        db.session.flush()
                        lead_id = lead.id
                        if settings and settings.notify_on_lead:
                            NotificationService.create("New Lead", f"New lead captured from {username}", "lead_created")
                
                log = InstagramAutomationLog(rule_id=rule.id, account_id=account_id, event_type="comment_reply", details=f"Replied to {username} for keyword '{matched_keyword}'")
                db.session.add(log)
                db.session.commit()
                
                # In a real environment, trigger ig_service to send reply_template
                
                return {"success": True, "replied": True, "lead_id": lead_id, "reply_msg": reply_msg}
                
        return {"success": True, "replied": False}

    def handle_incoming_dm(self, account_id: int, thread_id: str, username: str, text: str) -> dict:
        """Evaluates incoming DMs against DM rules."""
        settings = InstagramSettings.query.first()
        if settings and not settings.automation_enabled:
            return {"success": True, "replied": False}

        rules = InstagramAutomationRule.query.filter_by(account_id=account_id, rule_type='dm_reply', is_active=True).all()
        for rule in rules:
            keywords = [k.strip().lower() for k in rule.trigger_keywords.split(',')]
            matched_keyword = next((k for k in keywords if (rule.match_type == "exact" and text.lower() == k) or (rule.match_type == "contains" and k in text.lower())), None)
            
            if matched_keyword:
                templates = [t.strip() for t in rule.reply_template.split('|') if t.strip()]
                reply_msg = random.choice(templates) if templates else rule.reply_template
                
                lead = InstagramLead.query.filter_by(account_id=account_id, username=username).first()
                if not lead:
                    status = settings.default_lead_status if settings else "New Lead"
                    lead = InstagramLead(account_id=account_id, username=username, initial_comment=text, matched_keyword=matched_keyword, pipeline_status=status)
                    db.session.add(lead)
                
                log = InstagramAutomationLog(rule_id=rule.id, account_id=account_id, event_type="dm_reply", details=f"Auto DM to {username} for keyword '{matched_keyword}'")
                db.session.add(log)
                db.session.commit()
                
                # In a real environment, trigger ig_service to send DM via Graph API
                return {"success": True, "replied": True, "reply_msg": reply_msg}
        return {"success": True, "replied": False}