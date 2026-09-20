import logging
from database.db import db
from models.message_template import MessageTemplate
from utils.constants import DEFAULT_TEMPLATES

logger = logging.getLogger(__name__)


class TemplateService:

    def seed_default_templates(self):
        """Insert default templates if none exist."""
        if MessageTemplate.query.count() == 0:
            for tpl in DEFAULT_TEMPLATES:
                template = MessageTemplate(
                    template_name=tpl["template_name"],
                    category=tpl["category"],
                    template_content=tpl["template_content"],
                )
                db.session.add(template)
            db.session.commit()
            logger.info("Default templates seeded.")

    def get_all(self):
        return MessageTemplate.query.order_by(MessageTemplate.category, MessageTemplate.template_name).all()

    def get_by_id(self, template_id: int) -> MessageTemplate:
        return MessageTemplate.query.get(template_id)

    def create(self, name: str, content: str, category: str = "custom") -> MessageTemplate:
        template = MessageTemplate(
            template_name=name,
            template_content=content,
            category=category,
        )
        db.session.add(template)
        db.session.commit()
        return template

    def update(self, template_id: int, name: str, content: str, category: str) -> bool:
        template = MessageTemplate.query.get(template_id)
        if not template:
            return False
        template.template_name = name
        template.template_content = content
        template.category = category
        db.session.commit()
        return True

    def delete(self, template_id: int) -> bool:
        template = MessageTemplate.query.get(template_id)
        if not template:
            return False
        db.session.delete(template)
        db.session.commit()
        return True
