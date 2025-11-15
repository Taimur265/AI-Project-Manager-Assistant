# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

---

## Authentication Endpoints

### Register User

**POST** `/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "plan_tier": "free"
}
```

### Login

**POST** `/auth/login`

Login and receive access token.

**Request Body (form-urlencoded):**
```
username=user@example.com
password=securepassword123
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Get Current User

**GET** `/auth/me`

Get current authenticated user information.

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "plan_tier": "free"
}
```

---

## Project Endpoints

### List Projects

**GET** `/projects`

Get all projects for the current user.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Mobile App Redesign",
    "description": "Complete redesign of mobile application",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### Create Project

**POST** `/projects`

Create a new project.

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description"
}
```

**Response (201):**
```json
{
  "id": 2,
  "name": "New Project",
  "description": "Project description",
  "created_at": "2024-01-20T14:00:00"
}
```

### Get Project

**GET** `/projects/{project_id}`

Get a specific project.

**Response (200):**
```json
{
  "id": 1,
  "name": "Mobile App Redesign",
  "description": "Complete redesign of mobile application",
  "created_at": "2024-01-15T10:30:00"
}
```

### Delete Project

**DELETE** `/projects/{project_id}`

Delete a project and all its tasks.

**Response (204):** No content

---

## Task Endpoints

### Get Project Tasks

**GET** `/tasks/project/{project_id}`

Get all tasks for a project.

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Implement user authentication",
    "description": "Build secure login system with JWT tokens",
    "status": "in_progress",
    "task_type": "feature",
    "deadline": "2024-02-01T00:00:00",
    "assignee": "john@example.com",
    "priority_score": 45.5,
    "ai_risk_level": "medium",
    "tags": ["authentication", "security", "backend"],
    "acceptance_criteria": [
      "Users can register with email/password",
      "Login returns JWT token",
      "Protected routes validate token"
    ],
    "subtasks": [
      "Create User model",
      "Implement registration endpoint",
      "Implement login endpoint",
      "Add JWT middleware"
    ],
    "story_points": 5
  }
]
```

### Create Task

**POST** `/tasks`

Create a new task with AI analysis.

**Request Body:**
```json
{
  "project_id": 1,
  "title": "Fix login bug",
  "description": "Users can't login with special characters in password",
  "deadline": "2024-01-25T00:00:00",
  "assignee": "jane@example.com"
}
```

**Response (201):**
```json
{
  "id": 2,
  "title": "Fix login bug",
  "description": "Users experiencing authentication failures when passwords contain special characters. Need to fix password encoding in login endpoint.",
  "status": "todo",
  "task_type": "bug",
  "deadline": "2024-01-25T00:00:00",
  "assignee": "jane@example.com",
  "priority_score": 38.0,
  "ai_risk_level": "medium",
  "tags": ["bug", "authentication", "urgent"],
  "acceptance_criteria": [
    "Users can login with passwords containing special characters",
    "Password encoding handles all UTF-8 characters",
    "Add tests for special character passwords"
  ],
  "subtasks": [
    "Investigate password encoding issue",
    "Update password validation logic",
    "Add unit tests",
    "Test with various special characters"
  ],
  "story_points": 3
}
```

### Import Tasks from CSV

**POST** `/tasks/import/csv`

Import multiple tasks from a CSV file.

**Request (multipart/form-data):**
```
project_id: 1
file: tasks.csv
```

**CSV Format:**
```csv
title,description,status,assignee,deadline
Build API,Create REST API endpoints,todo,john@example.com,2024-02-15
Design UI,Create mockups,in_progress,jane@example.com,2024-02-10
```

**Response (200):**
```json
[
  {
    "id": 3,
    "title": "Build API",
    ...
  },
  {
    "id": 4,
    "title": "Design UI",
    ...
  }
]
```

### Import from Trello

**POST** `/tasks/import/trello`

Import tasks from a Trello board.

**Request (multipart/form-data):**
```
project_id: 1
board_id: abc123
api_key: your_trello_api_key
token: your_trello_token
```

**Response (200):**
```json
[
  {
    "id": 5,
    "title": "Task from Trello",
    ...
  }
]
```

### Update Task Status

**PATCH** `/tasks/{task_id}/status`

Update the status of a task.

**Request Body:**
```json
{
  "status": "done"
}
```

**Response (200):**
```json
{
  "message": "Status updated successfully"
}
```

---

## Report Endpoints

### Generate Daily Report

**POST** `/reports/generate/{project_id}`

Generate a new daily report for a project.

**Response (200):**
```json
{
  "date": "2024-01-20",
  "summary": "Project is progressing well with 8 of 12 tasks completed. Backend API integration is 60% complete. Login page development is delayed due to authentication library issues.",
  "priority_tasks": [
    {
      "id": 1,
      "title": "Fix authentication bug",
      "priority_score": 85.5
    }
  ],
  "risks": [
    {
      "task": "API Integration",
      "reason": "Deadline in 2 days, currently at 60% completion"
    }
  ],
  "blocked_tasks": [
    {
      "task": "Login Page",
      "reason": "Waiting for authentication library update"
    }
  ]
}
```

### Get Latest Report

**GET** `/reports/{project_id}/latest`

Get the most recent daily report.

**Response (200):**
```json
{
  "date": "2024-01-20",
  "summary": "...",
  "priority_tasks": [...],
  "risks": [...],
  "blocked_tasks": [...]
}
```

### Get Timeline Status

**GET** `/reports/{project_id}/timeline-status`

Get overall project timeline status.

**Response (200):**
```json
{
  "status": "At Risk",
  "reason": "3 high-risk tasks, 2 overdue tasks",
  "metrics": {
    "total_tasks": 15,
    "completed": 8,
    "blocked": 2,
    "overdue": 2,
    "high_risk": 3,
    "completion_rate": 53.3
  }
}
```

### Get Stakeholder Email

**GET** `/reports/{project_id}/stakeholder-email`

Generate a stakeholder-friendly update email.

**Response (200):**
```json
{
  "subject": "Project Update: Mobile App Redesign",
  "body": "This week we made significant progress on the Mobile App Redesign project, completing 8 of 12 planned tasks. Our team successfully finished the backend API integration and user authentication system.\n\nWe're currently working through a minor delay on the login page due to a third-party library update, but we expect to resolve this within the next two days. Overall, the project remains on track for our February 15th delivery date.\n\nKey accomplishments:\n- Completed backend API (100%)\n- User authentication system live\n- Database migration successful\n\nNext steps focus on frontend components and testing."
}
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Project not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
