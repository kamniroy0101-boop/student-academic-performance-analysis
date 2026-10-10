from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    max_marks = Column(Float, nullable=False, default=100.0)

    grades = relationship("Grade", back_populates="subject")
