from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json
from ..core.database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.task import Task, TaskStatus
from ..services.task_service import TaskService
from .auth import get_current_user

router = APIRouter()


class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: str = ""
    deadline: Optional[str] = None
    assignee: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    task_type: str
    deadline: Optional[str] = None
    assignee: Optional[str] = None
    priority_score: float
    ai_risk_level: str
    tags: List[str]
    acceptance_criteria: List[str]
    subtasks: List[str]
    story_points: Optional[int] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, task: Task):
        return cls(
            id=task.id,
            title=task.title,
            description=task.description or "",
            status=task.status.value if hasattr(task.status, 'value') else task.status,
            task_type=task.task_type.value if hasattr(task.task_type, 'value') else task.task_type,
            deadline=str(task.deadline) if task.deadline else None,
            assignee=task.assignee,
            priority_score=task.priority_score or 0.0,
            ai_risk_level=task.ai_risk_level.value if hasattr(task.ai_risk_level, 'value') else task.ai_risk_level,
            tags=json.loads(task.tags) if task.tags else [],
            acceptance_criteria=json.loads(task.acceptance_criteria) if task.acceptance_criteria else [],
            subtasks=json.loads(task.subtasks) if task.subtasks else [],
            story_points=task.story_points
        )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task with AI analysis"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == task_data.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Create task with AI analysis
    task_service = TaskService(db)
    task = task_service.create_task_from_text(
        task_data.title,
        task_data.description,
        task_data.project_id
    )

    # Update optional fields
    if task_data.deadline:
        try:
            task.deadline = datetime.fromisoformat(task_data.deadline)
        except:
            pass

    if task_data.assignee:
        task.assignee = task_data.assignee

    db.commit()
    db.refresh(task)

    return TaskResponse.from_orm(task)


@router.get("/project/{project_id}", response_model=List[TaskResponse])
def get_project_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for a project"""
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

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return [TaskResponse.from_orm(task) for task in tasks]


@router.post("/import/csv", response_model=List[TaskResponse])
async def import_csv(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import tasks from CSV file"""
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

    # Read CSV content
    content = await file.read()
    csv_content = content.decode('utf-8')

    # Import tasks
    task_service = TaskService(db)
    tasks = task_service.import_from_csv(csv_content, project_id)

    return [TaskResponse.from_orm(task) for task in tasks]


@router.post("/import/trello")
async def import_trello(
    project_id: int = Form(...),
    board_id: str = Form(...),
    api_key: str = Form(...),
    token: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import tasks from Trello board"""
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

    # Import tasks
    try:
        task_service = TaskService(db)
        tasks = task_service.import_from_trello(board_id, project_id, api_key, token)
        return [TaskResponse.from_orm(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error importing from Trello: {str(e)}"
        )


@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    status: TaskStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task status"""
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.status = status
    db.commit()

    return {"message": "Status updated successfully"}
