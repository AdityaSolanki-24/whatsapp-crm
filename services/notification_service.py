from database.db import db
from models.instagram import InstagramNotification

class NotificationService:
    @staticmethod
    def create(title: str, message: str, event_type: str) -> InstagramNotification:
        notif = InstagramNotification(
            title=title,
            message=message,
            event_type=event_type
        )
        db.session.add(notif)
        db.session.commit()
        return notif
        
    @staticmethod
    def get_unread():
        return InstagramNotification.query.filter_by(is_read=False).order_by(InstagramNotification.created_at.desc()).all()
        
    @staticmethod
    def mark_read(notif_id: int):
        notif = InstagramNotification.query.get(notif_id)
        if notif:
            notif.is_read = True
            db.session.commit()