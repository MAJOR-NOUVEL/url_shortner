from datetime import datetime, timezone

from app.extensions import db


class URL(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    short_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    original_url = db.Column(db.Text, nullable=False)
    custom_alias = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)

    user = db.relationship("User", back_populates="urls")
    clicks = db.relationship("ClickAnalytics", back_populates="url", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        # Normalize timezone comparison
        now = datetime.now(timezone.utc)
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now > exp

    def to_dict(self, base_url: str = "") -> dict:
        base = base_url.rstrip("/") if base_url else ""
        return {
            "id": self.id,
            "short_code": self.short_code,
            "short_url": f"{base}/{self.short_code}" if base else f"/{self.short_code}",
            "original_url": self.original_url,
            "custom_alias": self.custom_alias,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "click_count": self.clicks.count()
        }

    def __repr__(self) -> str:
        return f"<URL id={self.id} code={self.short_code}>"
