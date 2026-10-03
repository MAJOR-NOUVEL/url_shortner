import pytest

from app.utils.base62 import decode_base62, encode_base62, generate_random_base62


def test_encode_and_decode_base62():
    # Test zero
    encoded_zero = encode_base62(0, use_offset=False)
    assert encoded_zero == "0"
    assert decode_base62(encoded_zero, use_offset=False) == 0

    # Test roundtrips with positive integers
    test_integers = [1, 42, 61, 62, 1000, 999999, 123456789]
    for n in test_integers:
        encoded = encode_base62(n, use_offset=False)
        decoded = decode_base62(encoded, use_offset=False)
        assert decoded == n

    # Test with offset enabled (default for hiding small sequential IDs)
    for n in [1, 2, 3]:
        encoded_offset = encode_base62(n, use_offset=True)
        assert len(encoded_offset) >= 4
        decoded_offset = decode_base62(encoded_offset, use_offset=True)
        assert decoded_offset == n

def test_generate_random_base62():
    code1 = generate_random_base62(length=6)
    code2 = generate_random_base62(length=6)
    code3 = generate_random_base62(length=8)

    assert len(code1) == 6
    assert len(code2) == 6
    assert len(code3) == 8
    assert code1 != code2

def test_decode_invalid_character():
    with pytest.raises(ValueError):
        decode_base62("abc#123", use_offset=False)
