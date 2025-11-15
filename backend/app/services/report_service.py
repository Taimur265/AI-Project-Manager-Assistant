import json
from datetime import date, datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models.daily_report import DailyReport
from ..models.task import Task
from ..models.project import Project
from .ai_service import AIService


class ReportService:
    """Service for generating and managing daily reports"""

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    def generate_daily_report(self, project_id: int) -> DailyReport:
        """Generate a comprehensive daily report for a project"""
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get all tasks
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()

        # Convert tasks to dictionaries for AI processing
        task_dicts = []
        for task in tasks:
            task_dicts.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status.value if hasattr(task.status, 'value') else task.status,
                'deadline': task.deadline,
                'assignee': task.assignee,
                'priority_score': task.priority_score,
                'ai_risk_level': task.ai_risk_level.value if hasattr(task.ai_risk_level, 'value') else task.ai_risk_level,
                'task_type': task.task_type.value if hasattr(task.task_type, 'value') else task.task_type,
                'current_date': datetime.now()
            })

        # Rank tasks by priority
        ranked_tasks = self.ai_service.rank_tasks_by_priority(task_dicts)

        # Generate AI summary
        ai_summary = self.ai_service.generate_daily_summary(task_dicts, project.name)

        # Extract blocked tasks
        blocked_tasks = [
            {'task': t['title'], 'reason': 'Marked as blocked'}
            for t in task_dicts
            if t['status'] == 'blocked'
        ]

        # Create daily report
        report = DailyReport(
            project_id=project_id,
            date=date.today(),
            summary_text=ai_summary.get('summary_text', ''),
            priority_list_json=json.dumps(ranked_tasks[:10]),  # Top 10 tasks
            risks_json=json.dumps(ai_summary.get('risks', [])),
            blocked_tasks_json=json.dumps(blocked_tasks)
        )

        # Check if report already exists for today
        existing_report = self.db.query(DailyReport).filter(
            DailyReport.project_id == project_id,
            DailyReport.date == date.today()
        ).first()

        if existing_report:
            # Update existing report
            existing_report.summary_text = report.summary_text
            existing_report.priority_list_json = report.priority_list_json
            existing_report.risks_json = report.risks_json
            existing_report.blocked_tasks_json = report.blocked_tasks_json
            self.db.commit()
            return existing_report
        else:
            # Create new report
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report

    def get_report_summary(self, report_id: int) -> Dict[str, Any]:
        """Get formatted summary from a daily report"""
        report = self.db.query(DailyReport).filter(DailyReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        return {
            'date': str(report.date),
            'summary': report.summary_text,
            'priority_tasks': json.loads(report.priority_list_json) if report.priority_list_json else [],
            'risks': json.loads(report.risks_json) if report.risks_json else [],
            'blocked_tasks': json.loads(report.blocked_tasks_json) if report.blocked_tasks_json else []
        }

    def generate_stakeholder_email(self, project_id: int) -> str:
        """Generate stakeholder update email for a project"""
        # Get latest report
        report = self.db.query(DailyReport).filter(
            DailyReport.project_id == project_id
        ).order_by(DailyReport.date.desc()).first()

        if not report:
            # Generate new report first
            report = self.generate_daily_report(project_id)

        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Format summary data
        summary_data = {
            'summary_text': report.summary_text,
            'priority_tasks': json.loads(report.priority_list_json) if report.priority_list_json else [],
            'risks': json.loads(report.risks_json) if report.risks_json else [],
            'blocked_tasks': json.loads(report.blocked_tasks_json) if report.blocked_tasks_json else []
        }

        # Generate stakeholder update
        return self.ai_service.generate_stakeholder_update(summary_data, project.name)

    def get_timeline_status(self, project_id: int) -> Dict[str, Any]:
        """Get overall timeline status for a project"""
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()

        if not tasks:
            return {
                'status': 'Needs More Info',
                'reason': 'No tasks found in project'
            }

        # Analyze tasks
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status.value == 'done'])
        blocked_tasks = len([t for t in tasks if t.status.value == 'blocked'])
        overdue_tasks = len([t for t in tasks if t.deadline and t.deadline < datetime.now() and t.status.value != 'done'])
        high_risk_tasks = len([t for t in tasks if t.ai_risk_level.value == 'high'])

        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

        # Determine status
        if blocked_tasks > total_tasks * 0.3 or overdue_tasks > total_tasks * 0.2:
            status = 'Off Track'
            reason = f"{blocked_tasks} blocked tasks, {overdue_tasks} overdue tasks"
        elif high_risk_tasks > total_tasks * 0.3 or overdue_tasks > 0:
            status = 'At Risk'
            reason = f"{high_risk_tasks} high-risk tasks, {overdue_tasks} overdue tasks"
        elif completion_rate > 0.7:
            status = 'On Track'
            reason = f"{int(completion_rate * 100)}% tasks completed"
        else:
            status = 'On Track'
            reason = 'Project progressing normally'

        return {
            'status': status,
            'reason': reason,
            'metrics': {
                'total_tasks': total_tasks,
                'completed': completed_tasks,
                'blocked': blocked_tasks,
                'overdue': overdue_tasks,
                'high_risk': high_risk_tasks,
                'completion_rate': round(completion_rate * 100, 1)
            }
        }
