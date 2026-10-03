from datetime import datetime, timezone

from app.extensions import db


class ClickAnalytics(db.Model):
    __tablename__ = "clicks"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    url_id = db.Column(db.BigInteger, db.ForeignKey("urls.id", ondelete="CASCADE"), nullable=False, index=True)
    clicked_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    referrer = db.Column(db.String(255), default="Direct", nullable=False)
    device = db.Column(db.String(50), default="Unknown", nullable=False)
    browser = db.Column(db.String(50), default="Unknown", nullable=False)
    country = db.Column(db.String(100), default="Unknown", nullable=False)
    ip_hash = db.Column(db.String(64), nullable=False)  # Privacy-preserving SHA-256(IP + salt)

    url = db.relationship("URL", back_populates="clicks")

    __table_args__ = (
        db.Index("ix_clicks_url_date", "url_id", "clicked_at"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url_id": self.url_id,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "referrer": self.referrer,
            "device": self.device,
            "browser": self.browser,
            "country": self.country
        }

    def __repr__(self) -> str:
        return f"<ClickAnalytics id={self.id} url_id={self.url_id}>"
