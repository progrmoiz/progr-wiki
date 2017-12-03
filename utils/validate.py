import re


def valid_username(name):
    USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
    return name and USER_RE.match(name)


def valid_password(password):
    PASSWORD_RE = re.compile(r'^.{6,20}$')
    return password and PASSWORD_RE.match(password)


def valid_email(email):
    EMAIL_RE = re.compile(
        r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
    return not email or EMAIL_RE.match(email)
