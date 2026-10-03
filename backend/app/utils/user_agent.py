from urllib.parse import urlparse


def parse_user_agent(ua_string: str) -> tuple[str, str]:
    """Classifies user agent into device category and browser family."""
    if not ua_string:
        return "Unknown", "Unknown"

    ua = ua_string.lower()

    # Device Classification
    if any(b in ua for b in ["bot", "crawl", "spider", "slurp", "facebookexternalhit", "curl", "wget", "python"]):
        device = "Bot"
    elif "ipad" in ua or "tablet" in ua:
        device = "Tablet"
    elif any(m in ua for m in ["mobi", "android", "iphone"]):
        device = "Mobile"
    else:
        device = "Desktop"

    # Browser Classification
    if "edg" in ua:
        browser = "Edge"
    elif "opr" in ua or "opera" in ua:
        browser = "Opera"
    elif "chrome" in ua:
        browser = "Chrome"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "firefox" in ua:
        browser = "Firefox"
    else:
        browser = "Other"

    return device, browser

def clean_referrer(referrer_url: str) -> str:
    """Extracts a readable brand or domain from a Referer header."""
    if not referrer_url:
        return "Direct"

    ref_lower = referrer_url.lower()
    if any(k in ref_lower for k in ["t.co", "twitter.com", "x.com"]):
        return "Twitter / X"
    if "linkedin.com" in ref_lower:
        return "LinkedIn"
    if "github.com" in ref_lower:
        return "GitHub"
    if "reddit.com" in ref_lower:
        return "Reddit"
    if "google." in ref_lower:
        return "Google"
    if any(k in ref_lower for k in ["facebook.com", "fb.me"]):
        return "Facebook"
    if "instagram.com" in ref_lower:
        return "Instagram"
    if any(k in ref_lower for k in ["youtube.com", "youtu.be"]):
        return "YouTube"

    try:
        domain = urlparse(referrer_url).netloc
        return domain if domain else "Direct"
    except Exception:
        return "Direct"

def extract_coarse_country(headers: dict) -> str:
    """Extracts coarse country code from edge proxy headers (Cloudflare / CDN)."""
    for header in ["cf-ipcountry", "x-country-code", "x-geoip-country-code"]:
        val = headers.get(header) or headers.get(header.upper())
        if val and val != "XX":
            return val.upper()
    return "Unknown"
