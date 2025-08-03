'use client'

import { useState, useEffect } from 'react'
import { getJiraDashboardData, getJiraIntegrationStatus, type JiraDashboardData } from '@/actions/jira-integration-action'

export function DynamicDashboard() {
  const [dashboardData, setDashboardData] = useState<JiraDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [hasJiraIntegration, setHasJiraIntegration] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      // First check if user has Jira integration
      const status = await getJiraIntegrationStatus()
      setHasJiraIntegration(status.is_connected)

      if (status.is_connected) {
        // Fetch dashboard data from Jira
        const data = await getJiraDashboardData()
        setDashboardData(data)
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-4 border-blue-300 border-t-blue-600 rounded-full animate-spin"></div>
            <span className="ml-3 text-gray-600">Loading dashboard...</span>
          </div>
        </div>
      </div>
    )
  }

  if (!hasJiraIntegration) {
    return (
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <svg className="w-12 h-12 text-blue-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Connect Jira to see insights</h3>
            <p className="text-blue-700 mb-4">Connect your Jira account to get AI-powered project insights and team analytics.</p>
            <a 
              href="/integrations" 
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Integrations
            </a>
          </div>
        </div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">Unable to load Jira data</h3>
            <p className="text-yellow-700">There was an issue fetching your Jira data. Please try refreshing the page.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome back!</h2>
          <p className="text-gray-600">Here's what's happening with your projects</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Projects</p>
                <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_projects}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Open Issues</p>
                <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.user_open_issues}</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recent Activity</p>
                <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.recent_activity_count}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Sprint Progress */}
        {dashboardData.sprint_data && dashboardData.sprint_data.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Sprints</h3>
            <div className="space-y-4">
              {dashboardData.sprint_data.slice(0, 3).map((sprint, index) => (
                <div key={sprint.id || index} className="border border-gray-100 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h4 className="font-medium text-gray-900">{sprint.name}</h4>
                      <p className="text-sm text-gray-600">{sprint.project_name} • {sprint.board_name}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{sprint.done_issues}/{sprint.total_issues} issues</p>
                      <p className="text-xs text-gray-600">{Math.round(sprint.progress_percentage)}% complete</p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${sprint.progress_percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Issues */}
        {dashboardData.user_issues && dashboardData.user_issues.issues && dashboardData.user_issues.issues.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Recent Issues</h3>
            <div className="space-y-3">
              {dashboardData.user_issues.issues.slice(0, 5).map((issue: any) => (
                <div key={issue.key} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      issue.fields.status.statusCategory.name === 'Done' ? 'bg-green-500' :
                      issue.fields.status.statusCategory.name === 'In Progress' ? 'bg-blue-500' :
                      'bg-gray-400'
                    }`}></div>
                    <div>
                      <p className="font-medium text-gray-900">{issue.fields.summary}</p>
                      <p className="text-sm text-gray-600">{issue.key} • {issue.fields.status.name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">{issue.fields.project.name}</p>
                    <p className="text-xs text-gray-500">
                      {issue.fields.priority ? issue.fields.priority.name : 'No priority'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Team Velocity */}
        {dashboardData.velocity_data && dashboardData.velocity_data.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Team Velocity</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboardData.velocity_data.slice(0, 6).map((velocity, index) => (
                <div key={index} className="border border-gray-100 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">{velocity.sprint_name}</h4>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Story Points:</span>
                      <span className="font-medium">{velocity.story_points || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Issues:</span>
                      <span className="font-medium">{velocity.completed_issues}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Project:</span>
                      <span className="font-medium">{velocity.project_key}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Projects Overview */}
        {dashboardData.projects && dashboardData.projects.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Projects</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboardData.projects.slice(0, 6).map((project: any) => (
                <div key={project.key} className="border border-gray-100 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-2">
                    {project.avatarUrls && project.avatarUrls['24x24'] && (
                      <img 
                        src={project.avatarUrls['24x24']} 
                        alt={project.name}
                        className="w-6 h-6 rounded"
                      />
                    )}
                    <div>
                      <h4 className="font-medium text-gray-900">{project.name}</h4>
                      <p className="text-sm text-gray-600">{project.key}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">{project.projectTypeKey}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}