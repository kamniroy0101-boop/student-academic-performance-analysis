from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.student import Student
from schemas.student import StudentCreate, StudentOut
from core.security import get_password_hash
from core.deps import get_current_user, require_admin

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=List[StudentOut])
def list_students(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(Student).all()


@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    # Check username uniqueness
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(Student).filter(Student.roll_number == payload.roll_number).first():
        raise HTTPException(status_code=400, detail="Roll number already exists")

    # Create linked user account
    user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role="student",
    )
    db.add(user)
    db.flush()  # get user.id before committing

    student = Student(
        user_id=user.id,
        name=payload.name,
        roll_number=payload.roll_number,
        department=payload.department,
        year=payload.year,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # Admin can access any student; student can only access their own record
    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return student
