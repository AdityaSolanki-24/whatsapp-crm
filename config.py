import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://root:password@localhost/whatsapp_crm"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "static/uploads")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_CSV_EXTENSIONS = {"csv"}
    WHATSAPP_API_URL = "https://graph.facebook.com/v19.0"
    WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID", "")
    WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
    CAMPAIGN_BATCH_SIZE = 50
    CAMPAIGN_DELAY_SECONDS = 1
    FB_APP_ID = os.environ.get("FB_APP_ID", "")
    FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")
    FB_WEBHOOK_VERIFY_TOKEN = os.environ.get("FB_WEBHOOK_VERIFY_TOKEN", "my_secure_verify_token")
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "https://yourdomain.com")
    
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
