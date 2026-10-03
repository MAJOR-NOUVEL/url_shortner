from app.routes.analytics import analytics_bp
from app.routes.auth import auth_bp
from app.routes.health import health_bp
from app.routes.redirect import redirect_bp
from app.routes.urls import urls_bp

__all__ = ["analytics_bp", "auth_bp", "health_bp", "redirect_bp", "urls_bp"]
