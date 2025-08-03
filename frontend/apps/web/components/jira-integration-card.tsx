'use client'

import { useState, useEffect } from 'react'
import { 
  getJiraIntegrationStatus, 
  initiateJiraOAuth, 
  disconnectJiraIntegration,
  type JiraStatusResponse 
} from '@/actions/jira-integration-action'

export function JiraIntegrationCard() {
  const [status, setStatus] = useState<JiraStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadStatus()
    
    // Check if we're coming back from OAuth success
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('jira_connected') === 'success') {
      // Remove the parameter from URL and reload status
      window.history.replaceState({}, '', window.location.pathname)
      setTimeout(() => loadStatus(), 1000) // Give backend time to process
    }
  }, [])

  const loadStatus = async () => {
    setLoading(true)
    try {
      const result = await getJiraIntegrationStatus()
      setStatus(result)
    } catch (error) {
      console.error('Error loading Jira status:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async () => {
    setActionLoading(true)
    try {
      const result = await initiateJiraOAuth()
      if (result.success && result.authorization_url) {
        // Redirect to Jira OAuth
        window.location.href = result.authorization_url
      } else {
        alert('Failed to initiate OAuth flow: ' + (result.error || 'Unknown error'))
      }
    } catch (error) {
      console.error('Error initiating OAuth:', error)
      alert('Failed to initiate OAuth flow')
    } finally {
      setActionLoading(false)
    }
  }

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect your Jira integration?')) {
      return
    }

    setActionLoading(true)
    try {
      const result = await disconnectJiraIntegration()
      if (result.success) {
        await loadStatus() // Refresh status
      } else {
        alert('Failed to disconnect: ' + (result.error || 'Unknown error'))
      }
    } catch (error) {
      console.error('Error disconnecting:', error)
      alert('Failed to disconnect integration')
    } finally {
      setActionLoading(false)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleDateString()
  }

  const isConnected = status?.is_connected && status?.is_active && !status?.is_token_expired

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center gap-4 mb-4">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
          <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.571 11.429H0a5.714 5.714 0 0 0 5.714 5.714h5.857a5.714 5.714 0 0 0 0-11.428H5.714a5.714 5.714 0 0 0 0 11.428h5.857v-5.714z"/>
            <path d="M24 11.429h-5.857a5.714 5.714 0 0 1-5.714-5.714V0a5.714 5.714 0 0 1 5.714 5.714v5.715a5.714 5.714 0 0 1 5.857 0z"/>
            <path d="M11.571 24V12.571a5.714 5.714 0 0 0-5.714 5.715V24a5.714 5.714 0 0 0 5.714-5.714z"/>
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-xl font-semibold">Jira</h3>
            {loading ? (
              <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
            ) : (
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            )}
          </div>
          <p className="text-sm text-gray-600">Project tracking insights</p>
          {isConnected && status?.site_name && (
            <p className="text-xs text-blue-600 mt-1">Connected to {status.site_name}</p>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-4">
          <div className="w-6 h-6 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-gray-600 mt-2">Loading status...</p>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-600 mb-4">
            Connect Jira to track sprint progress, identify at-risk stories, and monitor team velocity.
          </p>

          {isConnected ? (
            <div className="space-y-3 mb-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center gap-2 text-sm text-green-800">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="font-medium">Connected to {status?.site_name}</span>
                </div>
                <p className="text-xs text-green-600 mt-1">
                  Last sync: {formatDate(status?.last_sync_at)}
                </p>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Sprint analytics</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Risk detection</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Velocity tracking</span>
                </div>
              </div>

              <button 
                onClick={handleDisconnect}
                disabled={actionLoading}
                className="w-full py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {actionLoading ? 'Disconnecting...' : 'Disconnect Jira Account'}
              </button>
            </div>
          ) : (
            <>
              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Sprint analytics</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Risk detection</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Velocity tracking</span>
                </div>
              </div>

              <button 
                onClick={handleConnect}
                disabled={actionLoading}
                className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {actionLoading ? 'Connecting...' : 'Connect Jira Account'}
              </button>
            </>
          )}
        </>
      )}
    </div>
  )
}