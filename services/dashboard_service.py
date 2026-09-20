from database.db import db
from models.customer import Customer
from models.campaign import Campaign
from models.campaign_log import CampaignLog


class DashboardService:

    def get_stats(self) -> dict:
        total_customers = Customer.query.count()
        total_campaigns = Campaign.query.count()
        total_sent = db.session.query(db.func.sum(Campaign.sent_count)).scalar() or 0
        total_failed = db.session.query(db.func.sum(Campaign.failed_count)).scalar() or 0

        recent_campaigns = (
            Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
        )

        active_customers = Customer.query.filter_by(status="active").count()
        completed_campaigns = Campaign.query.filter_by(status="completed").count()
        running_campaigns = Campaign.query.filter_by(status="running").count()

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "total_campaigns": total_campaigns,
            "completed_campaigns": completed_campaigns,
            "running_campaigns": running_campaigns,
            "total_sent": total_sent,
            "total_failed": total_failed,
            "recent_campaigns": recent_campaigns,
        }
