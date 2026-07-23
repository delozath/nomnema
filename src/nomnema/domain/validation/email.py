import re

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def is_valid_email(email: str) -> bool:
    if re.match(EMAIL_PATTERN, email):
        return True
    return False

def raise_valid_email(email: str):
    if not is_valid_email(email):
        raise ValueError(f"`{email}` is not a valid email")
    return email