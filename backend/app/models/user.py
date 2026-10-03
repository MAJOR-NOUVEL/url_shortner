from datetime import datetime, timezone

import bcrypt

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    urls = db.relationship("URL", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, raw_password: str) -> None:
        """Hashes raw password using bcrypt with 12 rounds."""
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """Verifies raw password against stored bcrypt hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
