import json
from typing import List, Dict, Any
from anthropic import Anthropic
from ..core.config import settings
from ..models.task import Task, TaskType, RiskLevel


class AIService:
    """Service for all AI-powered features using Claude"""

    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    def analyze_task(self, task_title: str, task_description: str = "") -> Dict[str, Any]:
        """
        Analyze a task and return detailed breakdown with acceptance criteria,
        subtasks, story points, tags, and task type.
        """
        prompt = f"""Analyze this project task and provide a detailed breakdown:

Task Title: {task_title}
Task Description: {task_description if task_description else "No description provided"}

Please provide:
1. A detailed description (if not provided or unclear)
2. Acceptance criteria (clear, testable conditions for completion)
3. Subtasks (break down into smaller actionable steps)
4. Story point estimate (1, 2, 3, 5, 8, 13, or 21)
5. Task type (feature, bug, research, blocked, unclear)
6. Relevant tags (3-5 keywords)

Return your analysis as a JSON object with these exact keys:
{{
    "description": "detailed description",
    "acceptance_criteria": ["criterion 1", "criterion 2", ...],
    "subtasks": ["subtask 1", "subtask 2", ...],
    "story_points": 5,
    "task_type": "feature",
    "tags": ["tag1", "tag2", "tag3"]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            # Extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            result = json.loads(json_str)

            return result
        except Exception as e:
            print(f"Error analyzing task: {e}")
            return {
                "description": task_description or task_title,
                "acceptance_criteria": [],
                "subtasks": [],
                "story_points": 3,
                "task_type": "feature",
                "tags": []
            }

    def detect_risk_level(self, task: Dict[str, Any]) -> str:
        """Detect risk level for a task based on various factors"""
        risk_score = 0

        # Check if overdue
        if task.get('deadline') and task.get('deadline') < task.get('current_date'):
            risk_score += 3

        # Check if unassigned
        if not task.get('assignee'):
            risk_score += 1

        # Check if blocked
        if task.get('status') == 'blocked':
            risk_score += 3

        # Check if unclear
        if task.get('status') == 'unclear' or not task.get('description'):
            risk_score += 2

        # Check story points (high complexity)
        if task.get('story_points', 0) >= 8:
            risk_score += 1

        if risk_score >= 4:
            return RiskLevel.HIGH.value
        elif risk_score >= 2:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value

    def calculate_priority_score(self, task: Dict[str, Any]) -> float:
        """Calculate priority score for task ranking"""
        score = 0.0

        # Urgency (deadline proximity)
        if task.get('deadline'):
            days_until_deadline = (task['deadline'] - task.get('current_date', task['deadline'])).days
            if days_until_deadline < 0:
                score += 100  # Overdue
            elif days_until_deadline <= 1:
                score += 50
            elif days_until_deadline <= 3:
                score += 30
            elif days_until_deadline <= 7:
                score += 20

        # Status
        if task.get('status') == 'blocked':
            score += 40
        elif task.get('status') == 'in_progress':
            score += 25

        # Risk level
        risk_weights = {'high': 30, 'medium': 15, 'low': 5}
        score += risk_weights.get(task.get('ai_risk_level', 'low'), 5)

        # Task type
        if task.get('task_type') == 'bug':
            score += 20

        return score

    def generate_daily_summary(self, tasks: List[Dict[str, Any]], project_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive daily project summary with progress,
        risks, urgent tasks, and blocked items.
        """
        # Prepare task data for Claude
        task_summary = []
        for task in tasks:
            task_summary.append({
                "title": task.get("title"),
                "status": task.get("status"),
                "deadline": str(task.get("deadline")) if task.get("deadline") else "No deadline",
                "assignee": task.get("assignee", "Unassigned"),
                "priority_score": task.get("priority_score", 0),
                "risk_level": task.get("ai_risk_level", "low")
            })

        prompt = f"""Analyze this project's current status and generate a comprehensive daily summary:

Project: {project_name}
Tasks: {json.dumps(task_summary, indent=2)}

Generate a daily summary with these sections:

1. **Key Progress** (3 bullet points of what's been completed or advanced)
2. **Delays / Risks** (with specific reasons)
3. **Urgent Tasks Today** (top 3-5 most critical tasks)
4. **Blocked Items** (tasks that cannot proceed and why)

Format your response as JSON:
{{
    "key_progress": ["progress 1", "progress 2", "progress 3"],
    "risks": [
        {{"task": "task name", "reason": "why it's at risk"}},
        ...
    ],
    "urgent_tasks": ["task 1", "task 2", "task 3"],
    "blocked_items": [
        {{"task": "task name", "reason": "blocking reason"}},
        ...
    ],
    "summary_text": "A brief paragraph summarizing overall project health and key observations"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            result = json.loads(json_str)

            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {
                "key_progress": [],
                "risks": [],
                "urgent_tasks": [],
                "blocked_items": [],
                "summary_text": "Unable to generate summary at this time."
            }

    def generate_stakeholder_update(self, daily_summary: Dict[str, Any], project_name: str) -> str:
        """Generate a stakeholder-friendly update message"""
        prompt = f"""Based on this project summary, write a professional stakeholder update email:

Project: {project_name}
Summary Data: {json.dumps(daily_summary, indent=2)}

Write a concise, professional update that:
- Highlights key accomplishments
- Mentions any concerns or delays tactfully
- Provides confidence about next steps
- Is suitable for non-technical stakeholders

Keep it under 200 words."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text
        except Exception as e:
            print(f"Error generating stakeholder update: {e}")
            return f"Project {project_name} update: Work is progressing as planned."

    def classify_task_type(self, title: str, description: str = "") -> str:
        """Quick classification of task type"""
        text = (title + " " + description).lower()

        if any(word in text for word in ['fix', 'bug', 'error', 'issue', 'broken']):
            return TaskType.BUG.value
        elif any(word in text for word in ['research', 'investigate', 'explore', 'study']):
            return TaskType.RESEARCH.value
        elif any(word in text for word in ['blocked', 'waiting', 'dependency']):
            return TaskType.BLOCKED.value
        elif not description or len(description.strip()) < 10:
            return TaskType.UNCLEAR.value
        else:
            return TaskType.FEATURE.value

    def rank_tasks_by_priority(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank tasks by calculated priority scores"""
        # Calculate priority for each task
        for task in tasks:
            task['priority_score'] = self.calculate_priority_score(task)

        # Sort by priority score (descending)
        return sorted(tasks, key=lambda x: x.get('priority_score', 0), reverse=True)
