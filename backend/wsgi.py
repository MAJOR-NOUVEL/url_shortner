import os

from app import create_app

env = os.getenv("FLASK_ENV", "production" if os.getenv("ENV") == "production" else "development")
app = create_app(env)

if __name__ == "__main__":
    # Local developer fallback runner
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
