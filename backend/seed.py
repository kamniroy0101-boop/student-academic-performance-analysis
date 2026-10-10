"""
seed.py — Run once to populate the database with 3 students, 3 subjects, and sample grades.
Usage: cd backend && python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
import models  # registers all models
from models.user import User
from models.student import Student
from models.subject import Subject
from models.grade import Grade
from core.security import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Subjects ─────────────────────────────────────────────────────────────
subjects_data = [
    {"name": "Mathematics", "code": "MATH101", "department": "Science", "max_marks": 100.0},
    {"name": "Physics", "code": "PHY101", "department": "Science", "max_marks": 100.0},
    {"name": "Computer Science", "code": "CS101", "department": "Engineering", "max_marks": 100.0},
]

subjects = []
for sd in subjects_data:
    existing = db.query(Subject).filter(Subject.code == sd["code"]).first()
    if not existing:
        s = Subject(**sd)
        db.add(s)
        db.flush()
        subjects.append(s)
    else:
        subjects.append(existing)
db.commit()
print(f"Subjects ready: {[s.name for s in subjects]}")

# ── Students ──────────────────────────────────────────────────────────────
students_data = [
    {"name": "Alice Johnson", "roll_number": "CS2024001", "department": "Engineering", "year": 2, "username": "alice", "password": "alice123"},
    {"name": "Bob Smith",     "roll_number": "CS2024002", "department": "Engineering", "year": 2, "username": "bob",   "password": "bob123"},
    {"name": "Carol Davis",   "roll_number": "SC2024001", "department": "Science",     "year": 1, "username": "carol", "password": "carol123"},
]

students = []
for sd in students_data:
    existing_user = db.query(User).filter(User.username == sd["username"]).first()
    if not existing_user:
        user = User(username=sd["username"], hashed_password=get_password_hash(sd["password"]), role="student")
        db.add(user)
        db.flush()
        student = Student(user_id=user.id, name=sd["name"], roll_number=sd["roll_number"],
                          department=sd["department"], year=sd["year"])
        db.add(student)
        db.flush()
        students.append(student)
    else:
        student = db.query(Student).filter(Student.user_id == existing_user.id).first()
        students.append(student)
db.commit()
print(f"Students ready: {[s.name for s in students]}")

# ── Grades ────────────────────────────────────────────────────────────────
grades_data = [
    # Alice
    {"student_idx": 0, "subject_idx": 0, "exam_type": "internal", "marks_obtained": 78, "semester": "Sem-1"},
    {"student_idx": 0, "subject_idx": 0, "exam_type": "final",    "marks_obtained": 85, "semester": "Sem-1"},
    {"student_idx": 0, "subject_idx": 1, "exam_type": "internal", "marks_obtained": 72, "semester": "Sem-1"},
    {"student_idx": 0, "subject_idx": 1, "exam_type": "final",    "marks_obtained": 68, "semester": "Sem-1"},
    {"student_idx": 0, "subject_idx": 2, "exam_type": "midterm",  "marks_obtained": 91, "semester": "Sem-1"},
    {"student_idx": 0, "subject_idx": 2, "exam_type": "final",    "marks_obtained": 88, "semester": "Sem-1"},
    # Bob
    {"student_idx": 1, "subject_idx": 0, "exam_type": "internal", "marks_obtained": 55, "semester": "Sem-1"},
    {"student_idx": 1, "subject_idx": 0, "exam_type": "final",    "marks_obtained": 62, "semester": "Sem-1"},
    {"student_idx": 1, "subject_idx": 1, "exam_type": "internal", "marks_obtained": 35, "semester": "Sem-1"},
    {"student_idx": 1, "subject_idx": 1, "exam_type": "final",    "marks_obtained": 38, "semester": "Sem-1"},
    {"student_idx": 1, "subject_idx": 2, "exam_type": "midterm",  "marks_obtained": 74, "semester": "Sem-1"},
    {"student_idx": 1, "subject_idx": 2, "exam_type": "final",    "marks_obtained": 70, "semester": "Sem-1"},
    # Carol
    {"student_idx": 2, "subject_idx": 0, "exam_type": "internal", "marks_obtained": 90, "semester": "Sem-1"},
    {"student_idx": 2, "subject_idx": 0, "exam_type": "final",    "marks_obtained": 94, "semester": "Sem-1"},
    {"student_idx": 2, "subject_idx": 1, "exam_type": "internal", "marks_obtained": 80, "semester": "Sem-1"},
    {"student_idx": 2, "subject_idx": 1, "exam_type": "final",    "marks_obtained": 76, "semester": "Sem-1"},
]

count = 0
for gd in grades_data:
    student = students[gd["student_idx"]]
    subject = subjects[gd["subject_idx"]]
    existing = db.query(Grade).filter(
        Grade.student_id == student.id,
        Grade.subject_id == subject.id,
        Grade.exam_type == gd["exam_type"],
        Grade.semester == gd["semester"],
    ).first()
    if not existing:
        grade = Grade(
            student_id=student.id, subject_id=subject.id,
            exam_type=gd["exam_type"], marks_obtained=gd["marks_obtained"],
            semester=gd["semester"],
        )
        db.add(grade)
        count += 1

db.commit()
print(f"Grades added: {count}")
print("Seed complete.")
