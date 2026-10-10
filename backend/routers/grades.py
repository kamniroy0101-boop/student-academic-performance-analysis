from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.student import Student
from models.grade import Grade
from schemas.grade import GradeCreate, GradeOut
from core.deps import get_current_user, require_admin

router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("", response_model=GradeOut, status_code=status.HTTP_201_CREATED)
def create_grade(
    payload: GradeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    grade = Grade(**payload.model_dump())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@router.get("/student/{student_id}", response_model=List[GradeOut])
def get_student_grades(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(Grade).filter(Grade.student_id == student_id).all()
