import hmac
import hashlib


def make_secure_val(val):
    """Create a secure sha256 + SECRET hash of val

    Return: val|sha256_hash
    """
    SECRET = b'progrmoiz'

    h = hmac.new(SECRET, val.encode(), hashlib.sha256).hexdigest()
    return '%s|%s' % (val, h)


def check_secure_val(secure_val):
    """Splits value and make a hash of it and check it against secure_val

    secure_val="val|sha256_hash"
    """
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
