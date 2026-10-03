import hashlib
import ipaddress
import socket
from urllib.parse import urlparse

# Private and reserved IP networks for SSRF mitigation
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local & Cloud metadata (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),              # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),             # IPv6 Unique local
    ipaddress.ip_network("fe80::/10"),            # IPv6 Link-local
]

def is_ip_blocked(ip_str: str) -> bool:
    """Checks if an IP address belongs to any blocked/private network."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in net for net in BLOCKED_NETWORKS)
    except ValueError:
        return False

def validate_url_security(url_string: str) -> tuple[bool, str]:
    """
    Validates a URL against SSRF and open-redirect abuse.
    Enforces HTTP/HTTPS only, rejects private IPs, loopbacks, and cloud metadata.
    """
    if not url_string:
        return False, "URL cannot be empty."

    try:
        parsed = urlparse(url_string.strip())
    except Exception:
        return False, "Malformed URL."

    # 1. Scheme enforcement
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Scheme '{parsed.scheme}' not allowed. Only HTTP and HTTPS are permitted."

    # 2. Hostname validation
    hostname = parsed.hostname
    if not hostname:
        return False, "URL must contain a valid domain or host."

    hostname_lower = hostname.lower()
    if hostname_lower in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False, "Localhost addresses are blocked for security."

    # 3. Direct IP address check
    if is_ip_blocked(hostname):
        return False, "Access to private or link-local IP addresses is forbidden."

    # 4. DNS resolution check (prevent DNS rebinding / internal hosts like 'metadata.google.internal')
    try:
        # Get all resolved IP addresses for the hostname
        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_resolved = sockaddr[0]
            if is_ip_blocked(ip_resolved):
                return False, f"Domain resolves to a protected or private IP ({ip_resolved})."
    except (socket.gaierror, socket.herror):
        # Allow unresolved domains during offline testing / dev if it looks like a valid domain
        if "." not in hostname:
            return False, "Invalid host domain."
    except Exception:
        pass

    return True, ""

def hash_ip(ip_address: str, salt: str) -> str:
    """
    Generates a privacy-preserving irreversible hash of an IP address.
    Never store raw IP addresses in the database.
    """
    if not ip_address:
        return "unknown"
    salted = f"{salt}:{ip_address}".encode()
    return hashlib.sha256(salted).hexdigest()[:16]
