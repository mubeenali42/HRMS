from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()

@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == data.get("email"),
        models.User.password == data.get("password")
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Email ya password galat hai")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "salary_per_day": user.salary_per_day
    }