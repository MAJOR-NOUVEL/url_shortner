from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.click import ClickAnalytics
from app.models.url import URL

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/urls")

@analytics_bp.route("/<int:url_id>/analytics", methods=["GET"])
@jwt_required()
def get_url_analytics(url_id: int):
    """
    Returns aggregated analytics for a specific shortened link:
    - Total clicks & unique visitors
    - 30-day time series breakdown
    - Referrer sources
    - Device and browser breakdown
    - Country geographical breakdown
    """
    user_id = int(get_jwt_identity())
    url = URL.query.filter_by(id=url_id, user_id=user_id).first()

    if not url:
        return jsonify({"error": "Link not found or unauthorized."}), 404

    # 1. Total Clicks
    total_clicks = url.clicks.count()

    # 2. Unique Visitors (distinct IP hashes)
    unique_visitors = (
        db.session.query(func.count(func.distinct(ClickAnalytics.ip_hash)))
        .filter(ClickAnalytics.url_id == url_id)
        .scalar() or 0
    )

    # 3. 30-Day Daily Timeline
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_clicks = (
        db.session.query(ClickAnalytics.clicked_at)
        .filter(ClickAnalytics.url_id == url_id, ClickAnalytics.clicked_at >= thirty_days_ago)
        .all()
    )

    daily_counts = defaultdict(int)
    for c in recent_clicks:
        d_str = c.clicked_at.strftime("%Y-%m-%d")
        daily_counts[d_str] += 1

    # Ensure all last 7 days are represented even if 0 clicks
    timeline = []
    for i in range(29, -1, -1):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        timeline.append({
            "date": day,
            "clicks": daily_counts.get(day, 0)
        })

    # Helper function for calculating percentages
    def get_breakdown(query_results):
        items = []
        for name, count in query_results:
            pct = round((count / total_clicks) * 100, 1) if total_clicks > 0 else 0.0
            items.append({"name": name or "Unknown", "count": count, "percentage": pct})
        return items

    # 4. Top Referrers
    top_referrers_query = (
        db.session.query(ClickAnalytics.referrer, func.count(ClickAnalytics.id).label("count"))
        .filter(ClickAnalytics.url_id == url_id)
        .group_by(ClickAnalytics.referrer)
        .order_by(func.count(ClickAnalytics.id).desc())
        .limit(10)
        .all()
    )
    top_referrers = get_breakdown(top_referrers_query)

    # 5. Device Breakdown
    devices_query = (
        db.session.query(ClickAnalytics.device, func.count(ClickAnalytics.id).label("count"))
        .filter(ClickAnalytics.url_id == url_id)
        .group_by(ClickAnalytics.device)
        .order_by(func.count(ClickAnalytics.id).desc())
        .all()
    )
    devices = get_breakdown(devices_query)

    # 6. Browser Breakdown
    browsers_query = (
        db.session.query(ClickAnalytics.browser, func.count(ClickAnalytics.id).label("count"))
        .filter(ClickAnalytics.url_id == url_id)
        .group_by(ClickAnalytics.browser)
        .order_by(func.count(ClickAnalytics.id).desc())
        .all()
    )
    browsers = get_breakdown(browsers_query)

    # 7. Country Breakdown
    countries_query = (
        db.session.query(ClickAnalytics.country, func.count(ClickAnalytics.id).label("count"))
        .filter(ClickAnalytics.url_id == url_id)
        .group_by(ClickAnalytics.country)
        .order_by(func.count(ClickAnalytics.id).desc())
        .limit(10)
        .all()
    )
    countries = get_breakdown(countries_query)

    return jsonify({
        "url_id": url.id,
        "short_code": url.short_code,
        "original_url": url.original_url,
        "total_clicks": total_clicks,
        "unique_visitors": unique_visitors,
        "clicks_per_day": timeline,
        "top_referrers": top_referrers,
        "devices": devices,
        "browsers": browsers,
        "countries": countries
    }), 200
