from database.db import db
from datetime import datetime


class CampaignLog(db.Model):
    __tablename__ = "campaign_logs"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True, index=True)
    phone = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, sent, failed
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    retry_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "customer_id": self.customer_id,
            "phone": self.phone,
            "status": self.status,
            "error_message": self.error_message,
            "sent_at": self.sent_at.strftime("%Y-%m-%d %H:%M:%S") if self.sent_at else "",
            "retry_count": self.retry_count,
        }

    def __repr__(self):
        return f"<CampaignLog campaign={self.campaign_id} phone={self.phone} status={self.status}>"
