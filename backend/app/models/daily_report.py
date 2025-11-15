from sqlalchemy import Column, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from ..core.database import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    summary_text = Column(Text)  # Main summary with progress, risks, urgent tasks
    priority_list_json = Column(Text)  # JSON string of prioritized tasks
    risks_json = Column(Text)  # JSON string of detected risks
    blocked_tasks_json = Column(Text)  # JSON string of blocked items

    # Relationships
    project = relationship("Project", back_populates="daily_reports")
