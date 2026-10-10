from pydantic import BaseModel


class GradeCreate(BaseModel):
    student_id: int
    subject_id: int
    exam_type: str  # "internal", "midterm", "final"
    marks_obtained: float
    semester: str


class GradeOut(BaseModel):
    id: int
    student_id: int
    subject_id: int
    exam_type: str
    marks_obtained: float
    semester: str

    class Config:
        from_attributes = True
