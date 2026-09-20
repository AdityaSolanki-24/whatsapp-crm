import logging
import os
from datetime import datetime
from database.db import db
from models.instagram import InstagramContent
from services.instagram_service import InstagramService
from flask import current_app

logger = logging.getLogger(__name__)

class SchedulerService:
    def process_scheduled_content(self):
        """Finds and publishes Instagram content scheduled for the current time."""
        now = datetime.utcnow()
        contents = InstagramContent.query.filter(
            InstagramContent.status == 'scheduled',
            InstagramContent.schedule_time <= now
        ).all()
        
        ig_service = InstagramService()
        results = []
        
        for content in contents:
            try:
                # Lock status
                content.status = 'processing'
                db.session.commit()
                
                try:
                    base_url = current_app.config.get("APP_BASE_URL", "http://localhost:5000")
                except RuntimeError:
                    base_url = os.environ.get("APP_BASE_URL", "http://localhost:5000")

                result = ig_service.publish_content(content.id, base_url=base_url)
                
                if result.get('success'):
                    content.status = 'published'
                    content.published_at = datetime.utcnow()
                else:
                    content.status = 'failed'
                    content.error_message = result.get('error', 'Unknown error')
                db.session.commit()
                results.append({"id": content.id, "success": result.get('success')})
            except Exception as e:
                logger.exception(f"Scheduler Error for Content {content.id}: {e}")
        return results