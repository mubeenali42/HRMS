from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, SessionLocal
import models
import os
from routes import auth, employees, attendance, salary, leaves, report
from config import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME

# Database tables banao
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HRMS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth.router,        prefix="/api", tags=["Auth"])
app.include_router(employees.router,   prefix="/api", tags=["Employees"])
app.include_router(attendance.router,  prefix="/api", tags=["Attendance"])
app.include_router(salary.router,      prefix="/api", tags=["Salary"])
app.include_router(leaves.router,      prefix="/api", tags=["Leaves"])
app.include_router(report.router,      prefix="/api", tags=["Report"])

# Frontend folder
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Pages
@app.get("/")
def login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/hr")
def hr_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "hr_dashboard.html"))

@app.get("/employee")
def employee_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "employee_dashboard.html"))

@app.get("/super")
def super_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "super_dashboard.html"))

# Default SuperAdmin banana
def create_default_admin():
    db = SessionLocal()
    existing = db.query(models.User).filter(models.User.email == DEFAULT_ADMIN_EMAIL).first()
    if not existing:
        admin = models.User(
            name           = DEFAULT_ADMIN_NAME,
            email          = DEFAULT_ADMIN_EMAIL,
            password       = DEFAULT_ADMIN_PASSWORD,
            role           = "superadmin",
            department     = "Management",
            salary_per_day = 0
        )
        db.add(admin)
        db.commit()
    db.close()

create_default_admin()