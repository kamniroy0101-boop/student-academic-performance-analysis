from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
import models  # noqa: F401 — registers all ORM models with Base
from models.user import User
from core.security import get_password_hash
from routers import auth, students, subjects, grades, dashboard

app = FastAPI(title="Student Academic Performance Analytics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://[::1]:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables on startup
Base.metadata.create_all(bind=engine)


def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created.")
    finally:
        db.close()


seed_admin()

# Mount routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(subjects.router)
app.include_router(grades.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}
