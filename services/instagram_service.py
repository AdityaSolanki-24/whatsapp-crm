import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, List
from models.instagram import InstagramAccount, InstagramContent
from database.db import db
from flask import current_app

logger = logging.getLogger(__name__)

class InstagramService:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def _get_account(self, account_id: int) -> Optional[InstagramAccount]:
        return InstagramAccount.query.get(account_id)

    def test_connection(self, account_id: int) -> dict:
        """Verify if the Instagram token is still valid."""
        account = self._get_account(account_id)
        if not account or not account.access_token:
            return {"success": False, "error": "Account or token missing."}

        try:
            url = f"{self.BASE_URL}/{account.ig_user_id}?fields=id,username,profile_picture_url&access_token={account.access_token}"
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if response.status_code == 200:
                # Update profile picture if it changed
                if 'profile_picture_url' in data:
                    account.profile_picture_url = data['profile_picture_url']
                    db.session.commit()
                return {"success": True, "data": data}
            else:
                error_msg = data.get("error", {}).get("message", "Invalid connection")
                return {"success": False, "error": error_msg}
        except Exception as e:
            logger.exception("IG Test Connection Error")
            return {"success": False, "error": str(e)}

    def get_authorization_url(self, redirect_uri: str) -> str:
        app_id = current_app.config.get("FB_APP_ID")
        scopes = "instagram_basic,instagram_content_publish,instagram_manage_comments,instagram_manage_messages,pages_show_list,pages_read_engagement,pages_manage_metadata"
        return f"https://www.facebook.com/v19.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={scopes}&response_type=code"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        app_id = current_app.config.get("FB_APP_ID")
        app_secret = current_app.config.get("FB_APP_SECRET")
        url = f"{self.BASE_URL}/oauth/access_token?client_id={app_id}&client_secret={app_secret}&code={code}&redirect_uri={redirect_uri}"
        response = requests.get(url)
        return response.json()

    def get_long_lived_token(self, short_token: str) -> dict:
        app_id = current_app.config.get("FB_APP_ID")
        app_secret = current_app.config.get("FB_APP_SECRET")
        url = f"{self.BASE_URL}/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_token}"
        response = requests.get(url)
        return response.json()

    def connect_instagram_accounts(self, long_token_data: dict) -> List[InstagramAccount]:
        """Fetches Pages and links associated Instagram Business Accounts."""
        long_token = long_token_data.get("access_token")
        expires_in = long_token_data.get("expires_in", 5184000)
        
        url = f"{self.BASE_URL}/me/accounts?access_token={long_token}"
        pages_res = requests.get(url).json()
        pages = pages_res.get("data", [])
        
        connected_accounts = []
        for page in pages:
            page_id = page.get("id")
            page_token = page.get("access_token")
            
            ig_url = f"{self.BASE_URL}/{page_id}?fields=instagram_business_account&access_token={page_token}"
            ig_res = requests.get(ig_url).json()
            
            if "instagram_business_account" in ig_res:
                ig_id = ig_res["instagram_business_account"]["id"]
                
                profile_url = f"{self.BASE_URL}/{ig_id}?fields=id,username,name,profile_picture_url&access_token={page_token}"
                prof_res = requests.get(profile_url).json()
                
                account = InstagramAccount.query.filter_by(ig_user_id=ig_id).first()
                if not account:
                    account = InstagramAccount(ig_user_id=ig_id)
                    db.session.add(account)
                
                account.username = prof_res.get("username", "")
                account.account_name = prof_res.get("name", "")
                account.profile_picture_url = prof_res.get("profile_picture_url", "")
                account.access_token = page_token
                account.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
                account.status = "active"
                db.session.commit()
                connected_accounts.append(account)
                
        return connected_accounts

    def publish_content(self, content_id: int, base_url: str = None) -> dict:
        """
        Workflow to publish a post/reel to Instagram via Graph API.
        1. Create media container
        2. Publish media container
        """
        if not base_url:
             base_url = current_app.config.get("APP_BASE_URL", "")
             
        content = InstagramContent.query.get(content_id)
        if not content:
            return {"success": False, "error": "Content not found."}
            
        account = content.account
        if not account:
            return {"success": False, "error": "Associated IG account not found."}

        paths = content.media_paths.split(',') if content.media_paths else []
        if not paths:
            return {"success": False, "error": "No media attached."}

        container_url = f"{self.BASE_URL}/{account.ig_user_id}/media"
        container_payload = {
            "access_token": account.access_token,
            "caption": content.caption or "",
        }
        
        # Handle single vs Carousel vs Reels vs Stories
        try:
            if len(paths) > 1 and content.content_type == "post":
                children_ids = []
                for path in paths:
                    child_url = f"{base_url.rstrip('/')}/{path.strip()}"
                    c_res = requests.post(container_url, data={"image_url": child_url, "is_carousel_item": "true", "access_token": account.access_token}).json()
                    if "id" in c_res:
                        children_ids.append(c_res["id"])
                container_payload["media_type"] = "CAROUSEL"
                container_payload["children"] = ",".join(children_ids)
            else:
                media_url = f"{base_url.rstrip('/')}/{paths[0].strip()}"
                if content.content_type == "post":
                    container_payload["image_url"] = media_url
                elif content.content_type == "reel":
                    container_payload["media_type"] = "REELS"
                    container_payload["video_url"] = media_url
                elif content.content_type == "story":
                    container_payload["media_type"] = "STORIES"
                    if media_url.lower().endswith(("mp4", "mov")):
                        container_payload["video_url"] = media_url
                    else:
                        container_payload["image_url"] = media_url

            # Step 1: Create Container
            res = requests.post(container_url, data=container_payload).json()
            if "error" in res:
                from services.notification_service import NotificationService
                NotificationService.create("Upload Failed", f"Failed to upload {content.content_type}: {res['error']['message']}", "upload_failed")
                return {"success": False, "error": res["error"]["message"]}
                
            creation_id = res["id"]
            
            # Polling required for videos
            if "video_url" in container_payload or content.content_type == "reel":
                for _ in range(12):
                    status_res = requests.get(f"{self.BASE_URL}/{creation_id}?fields=status_code&access_token={account.access_token}").json()
                    if status_res.get("status_code") == "FINISHED":
                        break
                    time.sleep(5)
        
            # Step 2: Publish Container
            pub_url = f"{self.BASE_URL}/{account.ig_user_id}/media_publish"
            pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": account.access_token}).json()
            
            if "id" in pub_res:
                content.ig_media_id = pub_res["id"]
                db.session.commit()
                return {"success": True, "media_id": pub_res["id"]}
            else:
                return {"success": False, "error": pub_res.get("error", {}).get("message", "Publish failed.")}
        except Exception as e:
            logger.exception("Publish Content Error")
            return {"success": False, "error": str(e)}