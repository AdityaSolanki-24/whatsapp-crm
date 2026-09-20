import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from database.db import init_db, db
from config import get_config
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per day", "100 per hour"])
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    csrf = CSRFProtect()
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Ensure required folders exist
    for folder in [
        os.path.join(app.root_path, "static", "uploads", "campaigns"),
        os.path.join(app.root_path, "static", "uploads", "templates"),
        os.path.join(app.root_path, "static", "uploads", "instagram", "posts"),
        os.path.join(app.root_path, "static", "uploads", "instagram", "reels"),
        os.path.join(app.root_path, "static", "uploads", "instagram", "stories"),
        os.path.join(app.root_path, "static", "uploads", "instagram", "drafts"),
        os.path.join(app.root_path, "logs"),
        os.path.join(app.root_path, "instance"),
    ]:
        os.makedirs(folder, exist_ok=True)

    # Database
    init_db(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from models.admin import Admin

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.customers import customers_bp
    from routes.campaigns import campaigns_bp
    from routes.templates import templates_bp
    from routes.media import media_bp
    from routes.settings import settings_bp
    from routes.instagram import instagram_bp
    from routes.system import system_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(templates_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(instagram_bp)
    app.register_blueprint(system_bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # Logging
    if not app.debug:
        log_dir = os.path.join(app.root_path, "logs")
        os.makedirs(log_dir, exist_ok=True)
        handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    # Initialize DB tables and seed data
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy before create_all
        import models.instagram
        import models.system
        
        db.create_all()
        _seed_initial_data()

    # Initialize APScheduler (Prevent running twice in Werkzeug development debug mode)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        
        def run_publish_job():
            with app.app_context():
                from services.scheduler_service import SchedulerService
                SchedulerService().process_scheduled_content()
                
        def run_token_job():
            with app.app_context():
                from services.instagram_token_service import InstagramTokenService
                InstagramTokenService().check_expiries()
                
        scheduler.add_job(func=run_publish_job, trigger="interval", minutes=1)
        scheduler.add_job(func=run_token_job, trigger="interval", hours=24)
        scheduler.start()

    return app


def _seed_initial_data():
    """Create default admin and seed templates on first run."""
    from models.admin import Admin
    from services.template_service import TemplateService
    from services.auth_service import AuthService

    auth_service = AuthService()
    if not auth_service.admin_exists():
        auth_service.create_admin("admin", "admin123")
        import logging
        logging.getLogger(__name__).info(
            "Default admin created: username=admin password=admin123 — CHANGE THIS IMMEDIATELY!"
        )

    TemplateService().seed_default_templates()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)