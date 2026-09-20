import time
import logging
from datetime import datetime
from typing import Optional, List
from database.db import db
from models.campaign import Campaign
from models.campaign_log import CampaignLog
from models.customer import Customer
from services.whatsapp import WhatsAppService
from utils.helpers import render_message
from flask import current_app, request

logger = logging.getLogger(__name__)


class CampaignService:

    def create_campaign(self, title: str, message: str, image_path: str = None) -> Campaign:
        """Create a new campaign in draft state."""
        try:
            campaign = Campaign(
                title=title,
                message=message,
                image_path=image_path,
                status="draft",
            )
            db.session.add(campaign)
            db.session.commit()
            return campaign
        except Exception as e:
            db.session.rollback()
            raise e

    def send_campaign(
        self,
        campaign_id: int,
        customer_ids: Optional[List[int]] = None,
        base_url: str = "",
    ) -> dict:
        """
        Send a campaign to customers.
        If customer_ids is None or empty, send to all active customers.
        Returns a summary dict.
        """
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}

        if customer_ids:
            customers = Customer.query.filter(
                Customer.id.in_(customer_ids),
                Customer.status == "active",
            ).all()
        else:
            customers = Customer.query.filter_by(status="active").all()

        if not customers:
            return {"success": False, "error": "No active customers found"}

        campaign.status = "running"
        campaign.total_customers = len(customers)
        campaign.sent_count = 0
        campaign.failed_count = 0
        db.session.commit()

        whatsapp = WhatsAppService()
        delay = current_app.config.get("CAMPAIGN_DELAY_SECONDS", 1)

        sent = 0
        failed = 0

        for customer in customers:
            message_text = render_message(campaign.message, customer.to_dict())
            has_image = bool(campaign.image_path)

            if has_image:
                image_url = f"{base_url}/{campaign.image_path}"
                result = whatsapp.send_image_message(
                    to=customer.phone,
                    image_url=image_url,
                    caption=message_text,
                )
            else:
                result = whatsapp.send_text_message(
                    to=customer.phone,
                    message=message_text,
                )

            if not result["success"]:
                # Retry once
                time.sleep(2)
                if has_image:
                    result = whatsapp.send_image_message(
                        to=customer.phone,
                        image_url=image_url,
                        caption=message_text,
                    )
                else:
                    result = whatsapp.send_text_message(
                        to=customer.phone,
                        message=message_text,
                    )

            status = "sent" if result["success"] else "failed"
            log = CampaignLog(
                campaign_id=campaign.id,
                customer_id=customer.id,
                phone=customer.phone,
                status=status,
                error_message=result.get("error") if not result["success"] else None,
                retry_count=1 if not result["success"] else 0,
            )
            db.session.add(log)

            if result["success"]:
                sent += 1
            else:
                failed += 1

            campaign.sent_count = sent
            campaign.failed_count = failed
            db.session.commit()

            if delay > 0:
                time.sleep(delay)

        campaign.status = "completed"
        campaign.completed_at = datetime.utcnow()
        db.session.commit()

        return {
            "success": True,
            "sent": sent,
            "failed": failed,
            "total": len(customers),
        }

    def get_campaign_stats(self, campaign_id: int) -> dict:
        """Get detailed stats for a campaign."""
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return {}
        logs = CampaignLog.query.filter_by(campaign_id=campaign_id).all()
        return {
            "campaign": campaign.to_dict(),
            "logs": [log.to_dict() for log in logs],
        }

    def delete_campaign(self, campaign_id: int) -> bool:
        """Delete a campaign and all its logs."""
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return False
        db.session.delete(campaign)
        db.session.commit()
        return True
