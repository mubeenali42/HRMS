from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import calendar

router = APIRouter()

@router.post("/salary/calculate")
def calculate_salary(data: dict, db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    month   = data.get("month")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employee nahi mila")

    year, mon  = map(int, month.split("-"))
    total_days = calendar.monthrange(year, mon)[1]

    attendances = db.query(models.Attendance).filter(
        models.Attendance.user_id == user_id,
        models.Attendance.date.like(f"{month}%")
    ).all()

    present_days = sum(1 for a in attendances if a.status == "present")
    total_salary = present_days * user.salary_per_day

    existing = db.query(models.Salary).filter(
        models.Salary.user_id == user_id,
        models.Salary.month == month
    ).first()

    if existing:
        existing.total_days    = total_days
        existing.present_days  = present_days
        existing.salary_per_day = user.salary_per_day
        existing.total_salary  = total_salary
        db.commit()
        sal = existing
    else:
        sal = models.Salary(
            user_id        = user_id,
            month          = month,
            total_days     = total_days,
            present_days   = present_days,
            salary_per_day = user.salary_per_day,
            total_salary   = total_salary
        )
        db.add(sal)
        db.commit()
        db.refresh(sal)

    return {
        "name"          : user.name,
        "month"         : month,
        "total_days"    : total_days,
        "present_days"  : present_days,
        "salary_per_day": user.salary_per_day,
        "total_salary"  : total_salary
    }

@router.get("/salary/{user_id}")
def get_salary(user_id: int, db: Session = Depends(get_db)):
    records = db.query(models.Salary).filter(models.Salary.user_id == user_id).all()
    return [{"month": r.month, "total_days": r.total_days, "present_days": r.present_days,
             "salary_per_day": r.salary_per_day, "total_salary": r.total_salary} for r in records]

@router.get("/salary")
def get_all_salary(db: Session = Depends(get_db)):
    records = db.query(models.Salary, models.User).join(
        models.User, models.Salary.user_id == models.User.id
    ).all()
    return [{"name": u.name, "month": s.month, "total_days": s.total_days,
             "present_days": s.present_days, "total_salary": s.total_salary} for s, u in records]