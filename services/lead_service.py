import logging
from database.db import db
from models.instagram import InstagramLead
from models.customer import Customer

logger = logging.getLogger(__name__)

class LeadService:
    def get_all_leads(self, page=1, per_page=20):
        return InstagramLead.query.order_by(InstagramLead.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
    def update_status(self, lead_id: int, new_status: str) -> bool:
        lead = InstagramLead.query.get(lead_id)
        if lead:
            lead.pipeline_status = new_status
            db.session.commit()
            return True
        return False
        
    def convert_to_customer(self, lead_id: int, phone: str, email: str = "") -> dict:
        lead = InstagramLead.query.get(lead_id)
        if not lead:
            return {"success": False, "error": "Lead not found."}
        if lead.crm_customer_id:
            return {"success": False, "error": "Lead is already a CRM customer."}
            
        try:
            customer = Customer(
                customer_id=f"IG-{lead.username}-{lead.id}",
                name=lead.username,
                phone=phone,
                email=email,
                status="active"
            )
            db.session.add(customer)
            db.session.flush()
            lead.crm_customer_id = customer.id
            lead.pipeline_status = "Customer"
            db.session.commit()
            return {"success": True, "customer": customer}
        except Exception as e:
            db.session.rollback()
            logger.exception("Error converting IG lead to CRM customer.")
            return {"success": False, "error": str(e)}