from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    UNCLEAR = "unclear"


class TaskType(str, enum.Enum):
    FEATURE = "feature"
    BUG = "bug"
    RESEARCH = "research"
    BLOCKED = "blocked"
    UNCLEAR = "unclear"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    task_type = Column(Enum(TaskType), default=TaskType.FEATURE)
    deadline = Column(DateTime)
    assignee = Column(String)
    priority_score = Column(Float, default=0.0)  # AI-calculated priority
    ai_risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    tags = Column(Text)  # JSON string of AI-generated tags
    acceptance_criteria = Column(Text)  # AI-generated acceptance criteria
    subtasks = Column(Text)  # JSON string of subtasks
    story_points = Column(Integer)  # AI-estimated effort
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tasks")
