from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()

@router.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(models.User).filter(models.User.role == "employee").all()
    return [{"id": e.id, "name": e.name, "email": e.email, "department": e.department, "salary_per_day": e.salary_per_day} for e in employees]

@router.post("/employees")
def add_employee(data: dict, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.get("email")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email pehle se exist karta hai")
    emp = models.User(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password", "1234"),
        role="employee",
        department=data.get("department", ""),
        salary_per_day=float(data.get("salary_per_day", 0))
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return {"message": "Employee Added Successfully", "id": emp.id}

@router.put("/employees/{emp_id}")
def update_employee(emp_id: int, data: dict, db: Session = Depends(get_db)):
    emp = db.query(models.User).filter(models.User.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee nahi mila")
    emp.name = data.get("name", emp.name)
    emp.email = data.get("email", emp.email)
    emp.department = data.get("department", emp.department)
    emp.salary_per_day = float(data.get("salary_per_day", emp.salary_per_day))
    if data.get("password"):
        emp.password = data.get("password")
    db.commit()
    return {"message": "Employee Updated Successfully"}

@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.User).filter(models.User.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee nahi mila")
    db.delete(emp)
    db.commit()
    return {"message": "Employee Deleted Successfully"}

# HR Managers list
@router.get("/hr-managers")
def get_hr_managers(db: Session = Depends(get_db)):
    hrs = db.query(models.User).filter(models.User.role == "hr").all()
    return [{"id": h.id, "name": h.name, "email": h.email, "department": h.department} for h in hrs]

# HR Manager add karna (sirf superadmin)
@router.post("/hr-managers")
def add_hr_manager(data: dict, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.get("email")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email pehle se exist karta hai")
    hr = models.User(
        name           = data.get("name"),
        email          = data.get("email"),
        password       = data.get("password", "1234"),
        role           = "hr",
        department     = data.get("department", ""),
        salary_per_day = 0
    )
    db.add(hr)
    db.commit()
    db.refresh(hr)
    return {"message": "HR Manager Added Successfully", "id": hr.id}

# HR Manager delete karna
@router.delete("/hr-managers/{hr_id}")
def delete_hr_manager(hr_id: int, db: Session = Depends(get_db)):
    hr = db.query(models.User).filter(models.User.id == hr_id).first()
    if not hr:
        raise HTTPException(status_code=404, detail="HR Manager nahi mila")
    db.delete(hr)
    db.commit()
    return {"message": "HR Manager Deleted Successfully"}