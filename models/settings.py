from database.db import db
from datetime import datetime


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    whatsapp_phone_id = db.Column(db.String(200), nullable=True, default="")
    whatsapp_access_token = db.Column(db.Text, nullable=True, default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls()
            from database.db import db
            db.session.add(settings)
            db.session.commit()
        return settings

    def to_dict(self):
        return {
            "id": self.id,
            "whatsapp_phone_id": self.whatsapp_phone_id or "",
            "whatsapp_access_token": self.whatsapp_access_token or "",
        }

    def __repr__(self):
        return f"<Settings phone_id={self.whatsapp_phone_id}>"
