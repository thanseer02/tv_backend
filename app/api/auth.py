from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.schemas import UserLogin, LoginResponse, UserBase
from app.db.memory_store import db
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin):
    # Support login with either email or username
    ident = credentials.email or credentials.username
    if not ident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is required"
        )

    user = db.find_user_by_credential(ident)
    # Allow demo test accounts (admin / admin or any valid password >= 4 chars for demo flexibility)
    if not user:
        # Auto-create demo session if username is admin or email matches pattern
        if ident == "admin" or "@" in ident:
            user = {
                "id": f"usr_{hash(ident) % 100000}",
                "email": ident if "@" in ident else f"{ident}@tvadmin.io",
                "username": ident,
                "name": ident.split("@")[0].capitalize(),
                "role": "Administrator"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    else:
        # Check password
        expected_pwd = user.get("password", "admin")
        if credentials.password != expected_pwd and credentials.password != "admin" and len(credentials.password) < 4:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

    token = create_access_token(data={"sub": user["id"], "email": user["email"], "role": user.get("role", "Administrator")})
    
    user_response = UserBase(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user.get("role", "Administrator")
    )

    return LoginResponse(
        success=True,
        user=user_response,
        token=token
    )

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    return {"success": True, "message": "Successfully logged out"}

@router.get("/me", response_model=UserBase)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserBase(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user.get("role", "Administrator")
    )

