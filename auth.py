from passlib.context import CryptContext
from database import SessionLocal
from models import User

# ✅ NO bcrypt anywhere
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def authenticate(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if user and verify_password(password, user.password_hash):
        return {"id": user.id, "username": user.username, "role": user.role}
    return None

def create_admin_if_not_exists():
    db = SessionLocal()
    if not db.query(User).filter(User.role == "admin").first():
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
    db.close()
