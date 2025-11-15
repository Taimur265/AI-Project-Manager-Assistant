# AI Project Manager Assistant 🤖

> An AI-powered SaaS that automatically analyzes project tasks, generates daily summaries, detects risks, and provides intelligent project insights.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

## 🚀 What It Does

The AI Project Manager Assistant is a SaaS application that transforms how you manage projects by:

- **Automatically analyzing tasks** using Claude AI to generate detailed descriptions, acceptance criteria, and estimates
- **Generating daily summaries** with progress updates, risk assessments, and priority rankings
- **Detecting project risks** and timeline issues before they become problems
- **Prioritizing tasks intelligently** based on deadlines, dependencies, and team workload
- **Creating stakeholder updates** with AI-generated professional summaries

## ✨ Core Features

### MVP Features (✅ Implemented)

- ✅ **Task Import** - CSV and Trello integration
- ✅ **AI Task Analysis** - Automatic task breakdown with acceptance criteria
- ✅ **Daily Summaries** - AI-generated project status reports
- ✅ **Priority Ranking** - Intelligent task prioritization algorithm
- ✅ **Timeline Risk Detection** - Automatic identification of at-risk tasks
- ✅ **Dashboard** - Clean, intuitive project overview
- ✅ **Authentication** - Secure user registration and login
- ✅ **Multi-Project Support** - Manage multiple projects in one account

### Coming Soon

- 🔜 **Email Reports** - Automated daily email summaries
- 🔜 **Slack Integration** - Daily bot summaries in Slack
- 🔜 **Jira/Asana Import** - Additional PM tool integrations
- 🔜 **Burn-down Charts** - Visual progress tracking
- 🔜 **Team Collaboration** - Multi-user project management

## 🏗️ Architecture

### Backend (FastAPI + Claude AI)

```
backend/
├── app/
│   ├── api/           # API endpoints (auth, projects, tasks, reports)
│   ├── core/          # Config, database, security
│   ├── models/        # SQLAlchemy models (User, Project, Task, DailyReport)
│   ├── services/      # Business logic (AI, task, report services)
│   └── utils/         # Utility functions
├── main.py            # FastAPI application entry point
└── requirements.txt   # Python dependencies
```

### Frontend (Next.js + TypeScript + Tailwind)

```
frontend/
├── src/
│   ├── app/           # Next.js 14 app directory
│   │   ├── dashboard/ # Main dashboard page
│   │   ├── login/     # Authentication page
│   │   └── globals.css
│   ├── components/    # Reusable React components
│   ├── lib/           # API client, state management
│   └── types/         # TypeScript type definitions
└── package.json       # Node dependencies
```

## 📊 Data Model

### User
- `id` - Unique identifier
- `email` - User email
- `password_hash` - Hashed password
- `plan_tier` - Subscription tier (free, solo, team, enterprise)
- `created_at` - Account creation timestamp

### Project
- `id` - Unique identifier
- `user_id` - Foreign key to User
- `name` - Project name
- `description` - Project description
- `created_at` - Creation timestamp

### Task
- `id` - Unique identifier
- `project_id` - Foreign key to Project
- `title` - Task title
- `description` - AI-enhanced description
- `status` - Task status (todo, in_progress, done, blocked, unclear)
- `task_type` - Type (feature, bug, research, blocked, unclear)
- `deadline` - Due date
- `assignee` - Person assigned
- `priority_score` - AI-calculated priority (0-100+)
- `ai_risk_level` - Risk assessment (low, medium, high)
- `tags` - AI-generated tags (JSON)
- `acceptance_criteria` - AI-generated criteria (JSON)
- `subtasks` - AI-generated breakdown (JSON)
- `story_points` - AI-estimated effort (1, 2, 3, 5, 8, 13, 21)

### DailyReport
- `id` - Unique identifier
- `project_id` - Foreign key to Project
- `date` - Report date
- `summary_text` - Main AI-generated summary
- `priority_list_json` - Top prioritized tasks
- `risks_json` - Detected risks with reasons
- `blocked_tasks_json` - Blocked items

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL (or SQLite for development)
- Anthropic API key (Claude)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_claude_api_key_here
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///./aipm.db
   ```

5. **Run the server:**
   ```bash
   python main.py
   ```

   Backend will run on `http://localhost:8000`
   API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   Frontend will run on `http://localhost:3000`

### First Time Usage

1. Open `http://localhost:3000` in your browser
2. Click "Sign up" and create an account
3. Create your first project
4. Import tasks via CSV or create them manually
5. View AI-generated daily summary and insights!

## 📝 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

**Projects:**
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `DELETE /api/v1/projects/{id}` - Delete project

**Tasks:**
- `GET /api/v1/tasks/project/{project_id}` - Get all tasks for project
- `POST /api/v1/tasks` - Create task with AI analysis
- `POST /api/v1/tasks/import/csv` - Import tasks from CSV
- `POST /api/v1/tasks/import/trello` - Import from Trello
- `PATCH /api/v1/tasks/{id}/status` - Update task status

**Reports:**
- `POST /api/v1/reports/generate/{project_id}` - Generate daily report
- `GET /api/v1/reports/{project_id}/latest` - Get latest report
- `GET /api/v1/reports/{project_id}/timeline-status` - Get timeline status
- `GET /api/v1/reports/{project_id}/stakeholder-email` - Generate stakeholder update

## 🎯 How It Works

### 1. Task Analysis

When you create or import a task, the AI:
- Analyzes the title and description
- Generates detailed acceptance criteria
- Breaks it down into subtasks
- Estimates story points (1-21)
- Classifies task type (feature, bug, research, etc.)
- Generates relevant tags

### 2. Priority Calculation

Tasks are ranked based on:
- **Urgency** - Days until deadline
- **Status** - Blocked or in-progress tasks get higher priority
- **Risk Level** - High-risk tasks ranked higher
- **Task Type** - Bugs get priority boost

### 3. Risk Detection

The AI identifies risks based on:
- Overdue deadlines
- Unassigned tasks
- Blocked status
- Missing requirements
- High complexity (story points ≥ 8)

### 4. Daily Summary Generation

Each day (or on-demand), the AI:
- Analyzes all project tasks
- Identifies key progress and accomplishments
- Detects delays and risks with reasons
- Highlights urgent tasks for today
- Lists blocked items
- Generates overall project health summary

## 💰 Pricing Strategy

### Free Tier
- 1 project
- 50 tasks
- Basic AI analysis
- Manual report generation

### Solo Plan ($19/month)
- Unlimited projects
- Unlimited tasks
- Full AI features
- Daily automated reports
- Email summaries

### Team Plan ($49/month)
- Everything in Solo
- Multi-user collaboration
- Slack integration
- Advanced analytics
- Priority support

### Enterprise ($99-199/month)
- Everything in Team
- Custom workflows
- SSO integration
- Private deployment
- Dedicated support

## 🔒 Security

- Passwords hashed with bcrypt
- JWT token-based authentication
- CORS protection
- SQL injection prevention via SQLAlchemy ORM
- Environment variables for sensitive data

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 📄 CSV Import Format

Create a CSV file with these columns:

```csv
title,description,status,assignee,deadline
Implement login,Build user authentication,todo,john@example.com,2024-03-15
Fix bug in API,Error 500 on /users endpoint,in_progress,jane@example.com,2024-03-10
Design homepage,Create wireframes and mockups,todo,,2024-03-20
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Powered by [Claude AI](https://www.anthropic.com/claude) from Anthropic
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend built with [Next.js](https://nextjs.org/)
- UI styled with [Tailwind CSS](https://tailwindcss.com/)

## 📧 Support

For issues, questions, or feedback, please open an issue on GitHub.

---

**Built with ❤️ using AI-powered project management**