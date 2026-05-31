from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from datetime import date

router = APIRouter()

@router.get("/attendance")
def get_all_attendance(db: Session = Depends(get_db)):
    records = db.query(models.Attendance, models.User).join(
        models.User, models.Attendance.user_id == models.User.id
    ).all()
    return [{"attendance_id": a.id, "user_id": a.user_id, "name": u.name, "date": a.date, "status": a.status} for a, u in records]

@router.get("/attendance/{user_id}")
def get_attendance(user_id: int, db: Session = Depends(get_db)):
    records = db.query(models.Attendance).filter(models.Attendance.user_id == user_id).all()
    return [{"id": r.id, "date": r.date, "status": r.status} for r in records]

@router.post("/attendance")
def mark_attendance(data: dict, db: Session = Depends(get_db)):
    user_id  = data.get("user_id")
    att_date = data.get("date", str(date.today()))
    status   = data.get("status", "present")

    existing = db.query(models.Attendance).filter(
        models.Attendance.user_id == user_id,
        models.Attendance.date == att_date
    ).first()

    if existing:
        existing.status = status
        db.commit()
        return {"message": "Attendance Updated Successfully"}

    att = models.Attendance(user_id=user_id, date=att_date, status=status)
    db.add(att)
    db.commit()
    return {"message": "Attendance Added Successfully"}

@router.delete("/attendance/{att_id}")
def delete_attendance(att_id: int, db: Session = Depends(get_db)):
    att = db.query(models.Attendance).filter(models.Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Record nahi mila")
    db.delete(att)
    db.commit()
    return {"message": "Attendance Deleted Successfully"}