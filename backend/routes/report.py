from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import models
import io

router = APIRouter()

@router.get("/report/{month}")
def download_report(month: str, db: Session = Depends(get_db)):
    atts = db.query(models.Attendance, models.User).join(
        models.User, models.Attendance.user_id == models.User.id
    ).filter(models.Attendance.date.like(f"{month}%")).all()

    sals = db.query(models.Salary, models.User).join(
        models.User, models.Salary.user_id == models.User.id
    ).filter(models.Salary.month == month).all()

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph(f"HRMS Monthly Report — {month}", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Attendance Records", styles["Heading2"]))
    story.append(Spacer(1, 10))

    att_data = [["Naam", "Date", "Status"]]
    for a, u in atts:
        att_data.append([u.name, a.date, a.status])
    if len(att_data) == 1:
        att_data.append(["Koi record nahi", "", ""])

    att_table = Table(att_data, colWidths=[200, 150, 100])
    att_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#4f7dff")),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0),  11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING",        (0, 0), (-1, -1), 8),
    ]))
    story.append(att_table)
    story.append(Spacer(1, 30))

    story.append(Paragraph("Salary Records", styles["Heading2"]))
    story.append(Spacer(1, 10))

    sal_data = [["Naam", "Month", "Total Din", "Present Din", "Total Salary"]]
    for s, u in sals:
        sal_data.append([u.name, s.month, str(s.total_days), str(s.present_days), f"Rs {s.total_salary}"])
    if len(sal_data) == 1:
        sal_data.append(["Koi record nahi", "", "", "", ""])

    sal_table = Table(sal_data, colWidths=[150, 80, 80, 90, 100])
    sal_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#38c98a")),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0),  11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING",        (0, 0), (-1, -1), 8),
    ]))
    story.append(sal_table)

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=HRMS_Report_{month}.pdf"}
    )


@router.get("/report/{month}/employee/{user_id}")
def download_employee_report(month: str, user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employee nahi mila")

    atts = db.query(models.Attendance).filter(
        models.Attendance.user_id == user_id,
        models.Attendance.date.like(f"{month}%")
    ).all()

    sal = db.query(models.Salary).filter(
        models.Salary.user_id == user_id,
        models.Salary.month == month
    ).first()

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph(f"HRMS Employee Report — {user.name}", styles["Title"]))
    story.append(Paragraph(f"Month: {month} | Department: {user.department or '—'}", styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Attendance Records", styles["Heading2"]))
    story.append(Spacer(1, 10))

    att_data = [["Date", "Status"]]
    for a in atts:
        att_data.append([a.date, a.status])
    if len(att_data) == 1:
        att_data.append(["Koi record nahi", ""])

    att_table = Table(att_data, colWidths=[250, 200])
    att_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#4f7dff")),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING",        (0, 0), (-1, -1), 8),
    ]))
    story.append(att_table)
    story.append(Spacer(1, 30))

    story.append(Paragraph("Salary Summary", styles["Heading2"]))
    story.append(Spacer(1, 10))

    if sal:
        sal_data = [
            ["Total Din", "Present Din", "Per Din Rate", "Total Salary"],
            [str(sal.total_days), str(sal.present_days), f"Rs {sal.salary_per_day}", f"Rs {sal.total_salary}"]
        ]
    else:
        sal_data = [
            ["Total Din", "Present Din", "Per Din Rate", "Total Salary"],
            ["—", "—", "—", "Salary calculate nahi hui"]
        ]

    sal_table = Table(sal_data, colWidths=[100, 100, 120, 130])
    sal_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#38c98a")),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING",        (0, 0), (-1, -1), 8),
    ]))
    story.append(sal_table)

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Report_{user.name}_{month}.pdf"}
    )