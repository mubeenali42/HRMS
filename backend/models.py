from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = "users"
    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String)
    email          = Column(String, unique=True, index=True)
    password       = Column(String)
    role           = Column(String)
    department     = Column(String, default="")
    salary_per_day = Column(Float, default=0)

class Attendance(Base):
    __tablename__ = "attendance"
    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date    = Column(String)
    status  = Column(String)

class Salary(Base):
    __tablename__ = "salary"
    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer)
    month          = Column(String)
    present_days   = Column(Integer, default=0)
    total_days     = Column(Integer, default=0)
    salary_per_day = Column(Float, default=0)
    total_salary   = Column(Float, default=0)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"  # type: ignore
    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date    = Column(String)
    reason  = Column(String)
    status  = Column(String, default="pending")