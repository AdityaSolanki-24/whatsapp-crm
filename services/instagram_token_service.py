import logging
import requests
from datetime import datetime, timedelta
from database.db import db
from models.instagram import InstagramAccount
from services.notification_service import NotificationService
from flask import current_app

logger = logging.getLogger(__name__)

class InstagramTokenService:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def refresh_token(self, account_id: int) -> dict:
        account = InstagramAccount.query.get(account_id)
        if not account or not account.access_token:
            return {"success": False, "error": "Account or token missing"}
        
        try:
            url = f"{self.BASE_URL}/oauth/access_token?grant_type=fb_exchange_token&client_id={current_app.config['FB_APP_ID']}&client_secret={current_app.config['FB_APP_SECRET']}&fb_exchange_token={account.access_token}"
            res = requests.get(url, timeout=15).json()
            
            if "access_token" in res:
                account.access_token = res["access_token"]
                # Reset expiry to roughly 60 days
                account.token_expiry = datetime.utcnow() + timedelta(seconds=res.get("expires_in", 5184000))
                db.session.commit()
                return {"success": True, "expires_in": res.get("expires_in")}
            return {"success": False, "error": res.get("error", {}).get("message", "Unknown error")}
        except Exception as e:
            logger.exception(f"Token Refresh Error for account {account_id}")
            return {"success": False, "error": str(e)}

    def check_expiries(self):
        """Scheduled job to check token expiry dates and notify/refresh."""
        accounts = InstagramAccount.query.filter_by(status="active").all()
        now = datetime.utcnow()
        warning_threshold = now + timedelta(days=7)
        
        for account in accounts:
            if not account.token_expiry:
                continue
            
            if account.token_expiry <= now:
                account.status = "disconnected"
                NotificationService.create("Token Expired", f"Access token for {account.username} has expired. Please reconnect.", "token_expired")
                db.session.commit()
            elif account.token_expiry <= warning_threshold:
                # Attempt auto-refresh 7 days before expiry
                res = self.refresh_token(account.id)
                if not res["success"]:
                    NotificationService.create("Token Expiring Soon", f"Access token for {account.username} will expire in {(account.token_expiry - now).days} days.", "token_expiring")