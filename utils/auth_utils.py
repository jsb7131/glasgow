import uuid
import hashlib

def hash_password(password: str, salt: str = None):
    salt = salt or uuid.uuid4().hex
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, hashed_password: str):
    salt, hash_val = hashed_password.split("$")
    return hash_password(password, salt) == hashed_password
