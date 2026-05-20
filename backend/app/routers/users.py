"""Users management router."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user, get_password_hash
from app.schemas.user import UserResponse, UserCreate, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_or_404(db: Session, user_id: UUID) -> User:
    """Helper to get user or raise 404."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all users (admin only in production)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by ID."""
    user = get_user_or_404(db, user_id)
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new user (admin only in production)."""
    # Check if email exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        nombre_completo=user_data.nombre_completo,
        role_id=user_data.role_id,
        activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user."""
    user = get_user_or_404(db, user_id)

    # Check email uniqueness if changing
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        user.email = user_data.email

    if user_data.nombre_completo:
        user.nombre_completo = user_data.nombre_completo

    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)

    if user_data.activo is not None:
        user.activo = user_data.activo

    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete user (soft delete - deactivate)."""
    user = get_user_or_404(db, user_id)

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    # Soft delete
    user.activo = False
    db.commit()

    return None
