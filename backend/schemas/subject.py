from pydantic import BaseModel


class SubjectCreate(BaseModel):
    name: str
    code: str
    department: str
    max_marks: float = 100.0


class SubjectOut(BaseModel):
    id: int
    name: str
    code: str
    department: str
    max_marks: float

    class Config:
        from_attributes = True
