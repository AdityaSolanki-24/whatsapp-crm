MESSAGE_VARIABLES = ["{name}", "{customer_id}", "{email}", "{orders}", "{status}"]

CUSTOMER_STATUS_CHOICES = ["active", "inactive", "blocked"]

TEMPLATE_CATEGORIES = {
    "welcome": "Welcome",
    "offer": "Offer",
    "festival": "Festival",
    "order_update": "Order Update",
    "custom": "Custom",
}

CAMPAIGN_STATUS = {
    "draft": "Draft",
    "running": "Running",
    "completed": "Completed",
    "failed": "Failed",
}

LOG_STATUS = {
    "pending": "Pending",
    "sent": "Sent",
    "failed": "Failed",
}

IG_CONTENT_STATUS = {
    "draft": "Draft",
    "review": "Review",
    "approved": "Approved",
    "scheduled": "Scheduled",
    "published": "Published",
    "failed": "Failed",
}

IG_CONTENT_TYPES = ["post", "reel", "story"]

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_CSV_EXTENSIONS = {"csv"}

CSV_REQUIRED_COLUMNS = {"customer_id", "name", "phone"}
CSV_OPTIONAL_COLUMNS = {"email", "orders", "status"}
CSV_ALL_COLUMNS = CSV_REQUIRED_COLUMNS | CSV_OPTIONAL_COLUMNS

DEFAULT_TEMPLATES = [
    {
        "template_name": "Welcome Message",
        "category": "welcome",
        "template_content": "Hi {name}! 👋\n\nWelcome to our store! We're excited to have you with us.\n\nYour Customer ID: {customer_id}\n\nFeel free to explore our products and reach out if you need any help!\n\nThank you! 🙏",
    },
    {
        "template_name": "Special Offer",
        "category": "offer",
        "template_content": "🎉 Exclusive Offer for {name}!\n\nHi {name}, as one of our valued customers with {orders} orders, we have a special deal just for you!\n\nUse your Customer ID {customer_id} to avail this offer.\n\nDon't miss out! Limited time only. 🛒",
    },
    {
        "template_name": "Festival Greetings",
        "category": "festival",
        "template_content": "🪔 Happy Festive Season, {name}!\n\nWishing you and your family joy, prosperity, and happiness this festive season.\n\nThank you for being a valued customer with {orders} orders.\n\nCelebrate with our special festive deals! 🎊",
    },
    {
        "template_name": "Order Update",
        "category": "order_update",
        "template_content": "📦 Order Update for {name}\n\nDear {name}, your order status has been updated.\n\nCustomer ID: {customer_id}\nCurrent Status: {status}\nTotal Orders: {orders}\n\nFor queries, please contact our support team.\n\nThank you for shopping with us! 🙏",
    },
]
