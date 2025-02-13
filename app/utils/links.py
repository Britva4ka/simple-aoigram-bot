from urllib.parse import urlparse


def generate_user_link(username=None, user_id=None):
    if username:
        return f"https://t.me/{username}"
    elif user_id:
        return f"tg://user?id={user_id}"
    else:
        raise ValueError("Either username or user_id must be provided")


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
