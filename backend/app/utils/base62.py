import secrets
import string

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = len(BASE62_ALPHABET)

# Offset prevents small sequential numbers like '1', '2' for initial users
ID_OFFSET = 10_000_000

def encode_base62(num: int, use_offset: bool = True) -> str:
    """Encodes a positive integer into a Base62 string."""
    if use_offset:
        num += ID_OFFSET
    if num == 0:
        return BASE62_ALPHABET[0]

    digits = []
    while num > 0:
        remainder = num % BASE
        digits.append(BASE62_ALPHABET[remainder])
        num = num // BASE
    digits.reverse()
    return "".join(digits)

def decode_base62(code: str, use_offset: bool = True) -> int:
    """Decodes a Base62 string back to an integer."""
    num = 0
    for char in code:
        idx = BASE62_ALPHABET.find(char)
        if idx == -1:
            raise ValueError(f"Invalid character '{char}' in Base62 code.")
        num = num * BASE + idx

    if use_offset:
        num -= ID_OFFSET
    return num

def generate_random_base62(length: int = 6) -> str:
    """Generates a cryptographically random Base62 string."""
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))
