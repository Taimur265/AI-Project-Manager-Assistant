import csv
import json
from io import StringIO
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from ..models.task import Task, TaskStatus
from .ai_service import AIService


class TaskService:
    """Service for task management and import functionality"""

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    def import_from_csv(self, csv_content: str, project_id: int) -> List[Task]:
        """Import tasks from CSV content"""
        tasks = []
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)

        for row in reader:
            # Parse CSV row
            title = row.get('title') or row.get('Title') or row.get('name') or row.get('Name')
            description = row.get('description') or row.get('Description', '')
            status = row.get('status') or row.get('Status', 'todo')
            assignee = row.get('assignee') or row.get('Assignee', '')
            deadline_str = row.get('deadline') or row.get('Deadline', '')

            if not title:
                continue

            # Parse deadline
            deadline = None
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                except:
                    try:
                        deadline = datetime.strptime(deadline_str, '%m/%d/%Y')
                    except:
                        pass

            # Analyze task with AI
            ai_analysis = self.ai_service.analyze_task(title, description)

            # Create task
            task = Task(
                project_id=project_id,
                title=title,
                description=ai_analysis.get('description', description),
                status=self._normalize_status(status),
                task_type=ai_analysis.get('task_type', 'feature'),
                assignee=assignee if assignee else None,
                deadline=deadline,
                acceptance_criteria=json.dumps(ai_analysis.get('acceptance_criteria', [])),
                subtasks=json.dumps(ai_analysis.get('subtasks', [])),
                story_points=ai_analysis.get('story_points', 3),
                tags=json.dumps(ai_analysis.get('tags', []))
            )

            # Calculate priority and risk
            task_dict = self._task_to_dict(task)
            task.priority_score = self.ai_service.calculate_priority_score(task_dict)
            task.ai_risk_level = self.ai_service.detect_risk_level(task_dict)

            self.db.add(task)
            tasks.append(task)

        self.db.commit()
        return tasks

    def import_from_trello(self, board_id: str, project_id: int, api_key: str, token: str) -> List[Task]:
        """Import tasks from Trello board"""
        try:
            from trello import TrelloClient

            client = TrelloClient(api_key=api_key, token=token)
            board = client.get_board(board_id)
            tasks = []

            for card in board.all_cards():
                # Analyze with AI
                ai_analysis = self.ai_service.analyze_task(card.name, card.description or "")

                # Parse deadline
                deadline = None
                if card.due_date:
                    deadline = datetime.strptime(card.due_date[:10], '%Y-%m-%d')

                # Create task
                task = Task(
                    project_id=project_id,
                    title=card.name,
                    description=ai_analysis.get('description', card.description or ""),
                    status=self._trello_status_to_task_status(card.list_id, board),
                    task_type=ai_analysis.get('task_type', 'feature'),
                    deadline=deadline,
                    acceptance_criteria=json.dumps(ai_analysis.get('acceptance_criteria', [])),
                    subtasks=json.dumps(ai_analysis.get('subtasks', [])),
                    story_points=ai_analysis.get('story_points', 3),
                    tags=json.dumps(ai_analysis.get('tags', []))
                )

                # Calculate priority and risk
                task_dict = self._task_to_dict(task)
                task.priority_score = self.ai_service.calculate_priority_score(task_dict)
                task.ai_risk_level = self.ai_service.detect_risk_level(task_dict)

                self.db.add(task)
                tasks.append(task)

            self.db.commit()
            return tasks
        except Exception as e:
            print(f"Error importing from Trello: {e}")
            raise

    def create_task_from_text(self, title: str, description: str, project_id: int) -> Task:
        """Create a single task with AI analysis"""
        ai_analysis = self.ai_service.analyze_task(title, description)

        task = Task(
            project_id=project_id,
            title=title,
            description=ai_analysis.get('description', description),
            task_type=ai_analysis.get('task_type', 'feature'),
            acceptance_criteria=json.dumps(ai_analysis.get('acceptance_criteria', [])),
            subtasks=json.dumps(ai_analysis.get('subtasks', [])),
            story_points=ai_analysis.get('story_points', 3),
            tags=json.dumps(ai_analysis.get('tags', []))
        )

        # Calculate priority and risk
        task_dict = self._task_to_dict(task)
        task.priority_score = self.ai_service.calculate_priority_score(task_dict)
        task.ai_risk_level = self.ai_service.detect_risk_level(task_dict)

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def _normalize_status(self, status: str) -> TaskStatus:
        """Normalize status string to TaskStatus enum"""
        status_lower = status.lower().replace(' ', '_')
        status_map = {
            'todo': TaskStatus.TODO,
            'to_do': TaskStatus.TODO,
            'in_progress': TaskStatus.IN_PROGRESS,
            'inprogress': TaskStatus.IN_PROGRESS,
            'doing': TaskStatus.IN_PROGRESS,
            'done': TaskStatus.DONE,
            'completed': TaskStatus.DONE,
            'blocked': TaskStatus.BLOCKED,
            'unclear': TaskStatus.UNCLEAR
        }
        return status_map.get(status_lower, TaskStatus.TODO)

    def _trello_status_to_task_status(self, list_id: str, board) -> TaskStatus:
        """Convert Trello list to task status"""
        # This is a simple heuristic - can be customized
        try:
            list_obj = board.get_list(list_id)
            list_name = list_obj.name.lower()

            if 'done' in list_name or 'complete' in list_name:
                return TaskStatus.DONE
            elif 'progress' in list_name or 'doing' in list_name:
                return TaskStatus.IN_PROGRESS
            elif 'blocked' in list_name or 'waiting' in list_name:
                return TaskStatus.BLOCKED
            else:
                return TaskStatus.TODO
        except:
            return TaskStatus.TODO

    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Convert Task model to dictionary for AI processing"""
        return {
            'title': task.title,
            'description': task.description,
            'status': task.status.value if hasattr(task.status, 'value') else task.status,
            'deadline': task.deadline,
            'assignee': task.assignee,
            'story_points': task.story_points,
            'current_date': datetime.now(),
            'ai_risk_level': task.ai_risk_level.value if hasattr(task.ai_risk_level, 'value') else task.ai_risk_level,
            'task_type': task.task_type.value if hasattr(task.task_type, 'value') else task.task_type
        }
