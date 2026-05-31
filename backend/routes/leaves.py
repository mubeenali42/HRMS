from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()

# Employee leave request kare
@router.post("/leaves")
def request_leave(data: dict, db: Session = Depends(get_db)):
    leave = models.LeaveRequest(
        user_id = data.get("user_id"),
        date    = data.get("date"),
        reason  = data.get("reason", ""),
        status  = "pending"
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return {"message": "Leave Request Sent Successfully"}

# HR sab leave requests dekhe
@router.get("/leaves")
def get_leaves(db: Session = Depends(get_db)):
    records = db.query(models.LeaveRequest, models.User).join(
        models.User, models.LeaveRequest.user_id == models.User.id
    ).all()
    return [{
        "id"     : l.id,
        "name"   : u.name,
        "date"   : l.date,
        "reason" : l.reason,
        "status" : l.status
    } for l, u in records]

# Employee apni leave requests dekhe
@router.get("/leaves/{user_id}")
def get_my_leaves(user_id: int, db: Session = Depends(get_db)):
    records = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.user_id == user_id
    ).all()
    return [{"id": r.id, "date": r.date, "reason": r.reason, "status": r.status} for r in records]

# HR leave approve/reject kare
@router.put("/leaves/{leave_id}")
def update_leave(leave_id: int, data: dict, db: Session = Depends(get_db)):
    leave = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.id == leave_id
    ).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request nahi mili")

    leave.status = data.get("status")

    # Approve hone pe attendance mein leave lag jae
    if leave.status == "approved":
        existing = db.query(models.Attendance).filter(
            models.Attendance.user_id == leave.user_id,
            models.Attendance.date    == leave.date
        ).first()
        if existing:
            existing.status = "leave"
        else:
            att = models.Attendance(
                user_id = leave.user_id,
                date    = leave.date,
                status  = "leave"
            )
            db.add(att)

    db.commit()
    return {"message": f"Leave {leave.status.capitalize()} Successfully"}