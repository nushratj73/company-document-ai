
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

# Load environment variables from .env
load_dotenv()

# Read the JWT secret key
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured in .env")

# JWT signing algorithm
JWT_ALGORITHM = "HS256"

# Access token lifetime: 30 minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create the password hashing system using Argon2
password_hash = PasswordHash.recommended()


# Convert a plain password into a secure hash
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Check whether a password matches its stored hash
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )

# Create a JWT access token for an authenticated employee
def create_access_token(user_id: int) -> str:
    # Calculate when the token should expire
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Prepare the information stored inside the token
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    # Sign the token using our secret key
    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token 
# Verify a JWT access token and return its payload
def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except jwt.InvalidTokenError:
        raise ValueError("Invalid or expired access token")