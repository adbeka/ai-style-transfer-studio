from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import sqlite3
import os

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# Database initialization
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create default test user if not exists
    cursor.execute("SELECT * FROM users WHERE email = ?", ("test@example.com",))
    if not cursor.fetchone():
        hashed_password = pwd_context.hash("testpassword")
        cursor.execute("""
            INSERT INTO users (email, username, full_name, hashed_password)
            VALUES (?, ?, ?, ?)
        """, ("test@example.com", "test@example.com", "Test User", hashed_password))
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    created_at: datetime | None = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None = None
    is_active: bool
    created_at: datetime

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str) -> UserInDB | None:
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT email, username, full_name, hashed_password, is_active FROM users WHERE username = ? OR email = ?",
        (username, username)
    )
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return UserInDB(
            email=user_data[0],
            username=user_data[1],
            full_name=user_data[2],
            hashed_password=user_data[3],
            is_active=bool(user_data[4])
        )
    return None

def authenticate_user(username: str, password: str) -> UserInDB | bool:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_user(user_data: UserCreate) -> UserResponse:
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", 
                   (user_data.email, user_data.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    cursor.execute("""
        INSERT INTO users (email, username, full_name, hashed_password)
        VALUES (?, ?, ?, ?)
    """, (user_data.email, user_data.username, user_data.full_name, hashed_password))
    
    user_id = cursor.lastrowid
    cursor.execute("""
        SELECT id, email, username, full_name, is_active, created_at
        FROM users WHERE id = ?
    """, (user_id,))
    
    user_row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    return UserResponse(
        id=user_row[0],
        email=user_row[1], 
        username=user_row[2],
        full_name=user_row[3],
        is_active=bool(user_row[4]),
        created_at=datetime.fromisoformat(user_row[5])
    )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

auth_router = APIRouter()

@auth_router.post("/api/v1/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    return create_user(user)

@auth_router.post("/api/v1/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Update last login
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
        (user.username,)
    )
    conn.commit()
    conn.close()
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/api/v1/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@auth_router.post("/api/v1/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    # In a real implementation, you might blacklist the token
    return {"message": "Successfully logged out"}
