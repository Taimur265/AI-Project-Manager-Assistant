'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { projectsAPI, tasksAPI, reportsAPI } from '@/lib/api';
import { BarChart3, AlertTriangle, CheckCircle2, Clock, Plus, FileUp, LogOut } from 'lucide-react';

interface Project {
  id: number;
  name: string;
  description: string;
}

interface DailySummary {
  summary: string;
  priority_tasks: any[];
  risks: any[];
  blocked_tasks: any[];
}

interface TimelineStatus {
  status: string;
  reason: string;
  metrics: {
    total_tasks: number;
    completed: number;
    blocked: number;
    overdue: number;
    high_risk: number;
    completion_rate: number;
  };
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [dailySummary, setDailySummary] = useState<DailySummary | null>(null);
  const [timelineStatus, setTimelineStatus] = useState<TimelineStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    loadProjects();
  }, [user, router]);

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.getAll();
      setProjects(response.data);
      if (response.data.length > 0 && !selectedProject) {
        selectProject(response.data[0]);
      }
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectProject = async (project: Project) => {
    setSelectedProject(project);
    try {
      // Load daily summary
      const summaryResponse = await reportsAPI.getLatest(project.id).catch(() => {
        // If no report exists, generate one
        return reportsAPI.generate(project.id);
      });
      setDailySummary(summaryResponse.data);

      // Load timeline status
      const statusResponse = await reportsAPI.getTimelineStatus(project.id);
      setTimelineStatus(statusResponse.data);
    } catch (error) {
      console.error('Error loading project data:', error);
    }
  };

  const createProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await projectsAPI.create(newProjectName, newProjectDesc);
      setProjects([...projects, response.data]);
      setShowNewProject(false);
      setNewProjectName('');
      setNewProjectDesc('');
      selectProject(response.data);
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'On Track':
        return 'bg-green-100 text-green-800';
      case 'At Risk':
        return 'bg-yellow-100 text-yellow-800';
      case 'Off Track':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">AI Project Manager</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Projects Selector */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Projects</h2>
            <button
              onClick={() => setShowNewProject(!showNewProject)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              <Plus className="w-4 h-4" />
              New Project
            </button>
          </div>

          {showNewProject && (
            <form onSubmit={createProject} className="bg-white p-4 rounded-lg shadow mb-4">
              <input
                type="text"
                placeholder="Project Name"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md mb-2"
              />
              <textarea
                placeholder="Project Description"
                value={newProjectDesc}
                onChange={(e) => setNewProjectDesc(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md mb-2"
                rows={3}
              />
              <button
                type="submit"
                className="w-full bg-primary-600 text-white py-2 rounded-md hover:bg-primary-700"
              >
                Create Project
              </button>
            </form>
          )}

          <div className="flex gap-2 overflow-x-auto pb-2">
            {projects.map((project) => (
              <button
                key={project.id}
                onClick={() => selectProject(project)}
                className={`px-4 py-2 rounded-md whitespace-nowrap ${
                  selectedProject?.id === project.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {project.name}
              </button>
            ))}
          </div>
        </div>

        {selectedProject ? (
          <div className="space-y-6">
            {/* Timeline Status */}
            {timelineStatus && (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Project Status</h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(timelineStatus.status)}`}>
                    {timelineStatus.status}
                  </span>
                </div>
                <p className="text-gray-600 mb-4">{timelineStatus.reason}</p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{timelineStatus.metrics.total_tasks}</div>
                    <div className="text-sm text-gray-600">Total Tasks</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">{timelineStatus.metrics.completed}</div>
                    <div className="text-sm text-gray-600">Completed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-red-600">{timelineStatus.metrics.blocked}</div>
                    <div className="text-sm text-gray-600">Blocked</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-orange-600">{timelineStatus.metrics.overdue}</div>
                    <div className="text-sm text-gray-600">Overdue</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary-600">{timelineStatus.metrics.completion_rate}%</div>
                    <div className="text-sm text-gray-600">Complete</div>
                  </div>
                </div>
              </div>
            )}

            {/* Daily Summary */}
            {dailySummary && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Summary</h3>
                <p className="text-gray-700 mb-6">{dailySummary.summary}</p>

                {/* Priority Tasks */}
                {dailySummary.priority_tasks && dailySummary.priority_tasks.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Clock className="w-5 h-5 text-primary-600" />
                      Priority Tasks
                    </h4>
                    <div className="space-y-2">
                      {dailySummary.priority_tasks.slice(0, 5).map((task: any, idx: number) => (
                        <div key={idx} className="flex items-start gap-2 p-3 bg-gray-50 rounded">
                          <span className="font-bold text-primary-600">{idx + 1}.</span>
                          <div>
                            <div className="font-medium">{task.title}</div>
                            <div className="text-sm text-gray-600">Priority: {task.priority_score?.toFixed(1)}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Risks */}
                {dailySummary.risks && dailySummary.risks.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-yellow-600" />
                      Risks
                    </h4>
                    <div className="space-y-2">
                      {dailySummary.risks.map((risk: any, idx: number) => (
                        <div key={idx} className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                          <div className="font-medium text-yellow-900">{risk.task}</div>
                          <div className="text-sm text-yellow-700">{risk.reason}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Blocked Tasks */}
                {dailySummary.blocked_tasks && dailySummary.blocked_tasks.length > 0 && (
                  <div>
                    <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-red-600" />
                      Blocked Items
                    </h4>
                    <div className="space-y-2">
                      {dailySummary.blocked_tasks.map((blocked: any, idx: number) => (
                        <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded">
                          <div className="font-medium text-red-900">{blocked.task}</div>
                          <div className="text-sm text-red-700">{blocked.reason}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => router.push(`/tasks?project=${selectedProject.id}`)}
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow text-left"
              >
                <BarChart3 className="w-8 h-8 text-primary-600 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-1">View All Tasks</h3>
                <p className="text-sm text-gray-600">Manage and analyze tasks</p>
              </button>

              <button
                onClick={() => router.push(`/import?project=${selectedProject.id}`)}
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow text-left"
              >
                <FileUp className="w-8 h-8 text-primary-600 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-1">Import Tasks</h3>
                <p className="text-sm text-gray-600">CSV or Trello import</p>
              </button>

              <button
                onClick={() => router.push(`/reports?project=${selectedProject.id}`)}
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow text-left"
              >
                <CheckCircle2 className="w-8 h-8 text-primary-600 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-1">View Reports</h3>
                <p className="text-sm text-gray-600">Daily summaries & updates</p>
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-600 mb-4">No projects yet. Create your first project to get started!</p>
            <button
              onClick={() => setShowNewProject(true)}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Create Project
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
