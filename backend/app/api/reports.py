from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..models.project import Project
from ..services.report_service import ReportService
from .auth import get_current_user

router = APIRouter()


@router.post("/generate/{project_id}")
def generate_report(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate daily report for a project"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Generate report
    report_service = ReportService(db)
    report = report_service.generate_daily_report(project_id)

    return report_service.get_report_summary(report.id)


@router.get("/{project_id}/latest")
def get_latest_report(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get latest report for a project"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Get latest report
    from ..models.daily_report import DailyReport
    report = db.query(DailyReport).filter(
        DailyReport.project_id == project_id
    ).order_by(DailyReport.date.desc()).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reports found for this project"
        )

    report_service = ReportService(db)
    return report_service.get_report_summary(report.id)


@router.get("/{project_id}/timeline-status")
def get_timeline_status(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get timeline status for a project"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Get timeline status
    report_service = ReportService(db)
    return report_service.get_timeline_status(project_id)


@router.get("/{project_id}/stakeholder-email")
def get_stakeholder_email(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Generate stakeholder update email"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Generate email
    report_service = ReportService(db)
    email_content = report_service.generate_stakeholder_email(project_id)

    return {
        "subject": f"Project Update: {project.name}",
        "body": email_content
    }
