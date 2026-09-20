from database.db import db
from datetime import datetime


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(500), nullable=True)
    total_customers = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default="draft")  # draft, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    logs = db.relationship(
        "CampaignLog", backref="campaign", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def success_rate(self):
        if self.total_customers == 0:
            return 0
        return round((self.sent_count / self.total_customers) * 100, 1)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "image_path": self.image_path,
            "total_customers": self.total_customers,
            "sent_count": self.sent_count,
            "failed_count": self.failed_count,
            "status": self.status,
            "success_rate": self.success_rate,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
        }

    def __repr__(self):
        return f"<Campaign {self.title}>"
