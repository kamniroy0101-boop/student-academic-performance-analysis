from pydantic import BaseModel


class StudentCreate(BaseModel):
    name: str
    roll_number: str
    department: str
    year: int
    username: str
    password: str


class StudentOut(BaseModel):
    id: int
    name: str
    roll_number: str
    department: str
    year: int
    user_id: int

    class Config:
        from_attributes = True
