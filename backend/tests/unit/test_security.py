from app.utils.security import hash_ip, validate_url_security
from app.utils.user_agent import clean_referrer, parse_user_agent


def test_ssrf_blocking_private_and_loopback_ips():
    # Loopbacks
    is_safe, err = validate_url_security("http://127.0.0.1/admin")
    assert not is_safe
    assert "blocked" in err.lower() or "forbidden" in err.lower()

    is_safe, err = validate_url_security("http://localhost:8080/internal")
    assert not is_safe

    # AWS/Cloud metadata link-local
    is_safe, err = validate_url_security("http://169.254.169.254/latest/meta-data/")
    assert not is_safe

    # RFC 1918 Private networks
    assert not validate_url_security("http://10.0.0.1/api")[0]
    assert not validate_url_security("http://192.168.1.1/router")[0]
    assert not validate_url_security("http://172.16.0.5/secret")[0]

def test_dangerous_schemes_blocked():
    assert not validate_url_security("file:///etc/passwd")[0]
    assert not validate_url_security("gopher://localhost:70")[0]
    assert not validate_url_security("ftp://server.local/file.txt")[0]
    assert not validate_url_security("javascript:alert(1)")[0]

def test_valid_public_urls_allowed():
    assert validate_url_security("https://github.com/torvalds/linux")[0]
    assert validate_url_security("https://news.ycombinator.com/item?id=12345")[0]
    assert validate_url_security("http://example.com:80/path")[0]

def test_privacy_preserving_ip_hashing():
    salt = "secret-test-salt"
    ip = "198.51.100.42"
    h1 = hash_ip(ip, salt)
    h2 = hash_ip(ip, salt)

    # Deterministic with same salt
    assert h1 == h2
    assert len(h1) == 16
    assert ip not in h1  # Raw IP must never be present in the output

    # Different salt yields completely different hash
    h3 = hash_ip(ip, "another-salt")
    assert h1 != h3

def test_user_agent_and_referrer_classification():
    # User Agent
    dev, browser = parse_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari")
    assert dev == "Mobile"
    assert browser == "Safari"

    dev, browser = parse_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
    assert dev == "Desktop"
    assert browser == "Chrome"

    # Referrers
    assert clean_referrer("https://t.co/xyz123") == "Twitter / X"
    assert clean_referrer("https://www.linkedin.com/feed/") == "LinkedIn"
    assert clean_referrer("") == "Direct"
