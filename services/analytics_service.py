from models.instagram import InstagramContent, InstagramLead, InstagramAnalytics
from datetime import datetime, timedelta
from database.db import db

class AnalyticsService:
    def get_dashboard_stats(self) -> dict:
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        
        posts = InstagramContent.query.filter(InstagramContent.content_type == 'post').count()
        reels = InstagramContent.query.filter(InstagramContent.content_type == 'reel').count()
        stories = InstagramContent.query.filter(InstagramContent.content_type == 'story').count()
        leads_30d = InstagramLead.query.filter(InstagramLead.created_at >= thirty_days_ago).count()
        
        # Returning standard aggregated stats
        return {
            "total_posts": posts,
            "total_reels": reels,
            "total_stories": stories,
            "leads_last_30d": leads_30d,
            "engagement_rate": "4.2%" # Mocked representation
        }