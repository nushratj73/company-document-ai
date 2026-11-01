from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse
)
from security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token
)


# Create the authentication router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Extract JWT Bearer tokens from API requests
oauth2_scheme = HTTPBearer()


# Register a new employee
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Check whether the email is already registered
    existing_user = db.scalar(
        select(User).where(User.email == str(user_data.email))
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    # Hash the employee's password
    hashed_password = hash_password(user_data.password)

    # Create a new user database record
    new_user = User(
        email=str(user_data.email),
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role="employee",
        is_active=True
    )

    # Save the new user in PostgreSQL
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    return new_user


# Log in an existing employee
@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    # Find the employee using their email
    user = db.scalar(
        select(User).where(User.email == str(user_data.email))
    )

    # Reject an unknown email or incorrect password
    if not user or not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Reject inactive employee accounts
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive"
        )

    # Generate an access token for the employee
    access_token = create_access_token(user.id)

    # Return the token to the client
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# Get the currently authenticated employee
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    
    # Verify the access token
    try:
        payload = verify_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract the employee ID from the token
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )

    # Find the employee in PostgreSQL
    user = db.get(User, int(user_id))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee not found or inactive"
        )

    return user

# Get the profile of the currently authenticated employee
@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user