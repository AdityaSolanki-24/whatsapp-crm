from database.db import db
from datetime import datetime


class MessageTemplate(db.Model):
    __tablename__ = "message_templates"

    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(200), nullable=False, unique=True)
    template_content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="custom")  # welcome, offer, festival, order_update, custom
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "template_name": self.template_name,
            "template_content": self.template_content,
            "category": self.category,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
        }

    def __repr__(self):
        return f"<MessageTemplate {self.template_name}>"
