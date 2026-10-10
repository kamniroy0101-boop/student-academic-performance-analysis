from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.student import Student
from models.subject import Subject
from models.grade import Grade
from core.deps import get_current_user, require_admin

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Dict[str, Any]:
    total_students = db.query(Student).count()
    total_subjects = db.query(Subject).count()

    subjects = db.query(Subject).all()
    subject_stats = []
    total_pass = 0
    total_fail = 0

    for subject in subjects:
        grades = db.query(Grade).filter(Grade.subject_id == subject.id).all()
        if not grades:
            subject_stats.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "subject_code": subject.code,
                "average_marks": 0,
                "pass_count": 0,
                "fail_count": 0,
                "max_marks": subject.max_marks,
            })
            continue

        threshold = subject.max_marks * 0.4
        pass_count = sum(1 for g in grades if g.marks_obtained >= threshold)
        fail_count = len(grades) - pass_count
        avg = sum(g.marks_obtained for g in grades) / len(grades)

        total_pass += pass_count
        total_fail += fail_count

        subject_stats.append({
            "subject_id": subject.id,
            "subject_name": subject.name,
            "subject_code": subject.code,
            "average_marks": round(avg, 2),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "max_marks": subject.max_marks,
        })

    overall_pass_rate = 0.0
    if (total_pass + total_fail) > 0:
        overall_pass_rate = round(total_pass / (total_pass + total_fail) * 100, 1)

    return {
        "total_students": total_students,
        "total_subjects": total_subjects,
        "overall_pass_rate": overall_pass_rate,
        "subject_stats": subject_stats,
    }


@router.get("/student/{student_id}")
def student_dashboard(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    grades = (
        db.query(Grade, Subject)
        .join(Subject, Grade.subject_id == Subject.id)
        .filter(Grade.student_id == student_id)
        .all()
    )

    grade_rows = []
    subject_map: Dict[str, Dict] = {}

    for grade, subject in grades:
        threshold = subject.max_marks * 0.4
        passed = grade.marks_obtained >= threshold
        grade_rows.append({
            "grade_id": grade.id,
            "subject_name": subject.name,
            "subject_code": subject.code,
            "exam_type": grade.exam_type,
            "marks_obtained": grade.marks_obtained,
            "max_marks": subject.max_marks,
            "semester": grade.semester,
            "passed": passed,
        })
        # For chart: track marks per subject (use latest/highest for display)
        if subject.name not in subject_map or grade.marks_obtained > subject_map[subject.name]["marks_obtained"]:
            subject_map[subject.name] = {
                "subject_name": subject.name,
                "marks_obtained": grade.marks_obtained,
                "max_marks": subject.max_marks,
            }

    subjects_enrolled = len(subject_map)
    overall_avg = 0.0
    highest_subject = None

    if grade_rows:
        overall_avg = round(
            sum(r["marks_obtained"] for r in grade_rows) / len(grade_rows), 1
        )
        highest_subject = max(subject_map.values(), key=lambda x: x["marks_obtained"])["subject_name"]

    return {
        "student_name": student.name,
        "roll_number": student.roll_number,
        "department": student.department,
        "year": student.year,
        "subjects_enrolled": subjects_enrolled,
        "overall_average": overall_avg,
        "highest_subject": highest_subject,
        "subject_chart_data": list(subject_map.values()),
        "grades": grade_rows,
    }
