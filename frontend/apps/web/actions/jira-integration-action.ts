'use server'

import { getApiClient } from '@/lib/api'
import { authOptions } from '@/lib/auth'
import { ApiError } from '@frontend/types/api'
import { getServerSession } from 'next-auth'
import { revalidatePath } from 'next/cache'

export interface JiraStatusResponse {
  is_connected: boolean
  site_name?: string
  site_url?: string
  is_active?: boolean
  is_token_expired?: boolean
  last_sync_at?: string
  created_at?: string
  message?: string
}

export async function getJiraIntegrationStatus(): Promise<JiraStatusResponse> {
  try {
    const session = await getServerSession(authOptions)
    const apiClient = await getApiClient(session)

    const response = await apiClient.integrations.integrationsJiraStatusRetrieve()
    return {
      //@ts-ignore
      is_connected: response.is_connected === true,
      site_name: response.site_name,
      site_url: response.site_url,
      is_active: response.is_active,
      //@ts-ignore
      is_token_expired: response.is_token_expired === true,
      last_sync_at: response.last_sync_at || undefined,
      created_at: response.created_at,
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return { is_connected: false, message: 'No integration found' }
    }
    console.error('Error fetching Jira integration status:', error)
    return { is_connected: false, message: 'Failed to fetch status' }
  }
}

export async function initiateJiraOAuth(): Promise<{ success: boolean; authorization_url?: string; error?: string }> {
  try {
    const session = await getServerSession(authOptions)
    const apiClient = await getApiClient(session)

    const response = await apiClient.integrations.integrationsJiraConnectCreate()
    
    if (response && 'authorization_url' in response) {
      return { success: true, authorization_url: response.authorization_url }
    }

    return { success: false, error: 'Failed to initiate OAuth flow' }
  } catch (error) {
    console.error('Error initiating Jira OAuth:', error)
    return { success: false, error: 'Failed to initiate OAuth flow' }
  }
}


export async function disconnectJiraIntegration(): Promise<{ success: boolean; error?: string }> {
  try {
    const session = await getServerSession(authOptions)
    const apiClient = await getApiClient(session)

    await apiClient.integrations.integrationsJiraDisconnectDestroy()

    revalidatePath('/integrations')
    return { success: true }
  } catch (error) {
    console.error('Error disconnecting Jira integration:', error)
    return { success: false, error: 'Failed to disconnect integration' }
  }
}

export interface JiraDashboardData {
  projects: any[]
  current_user: any
  user_issues: any
  recent_activity: any
  sprint_data: any[]
  velocity_data: any[]
  stats: {
    total_projects: number
    user_open_issues: number
    recent_activity_count: number
  }
}

export async function getJiraDashboardData(): Promise<JiraDashboardData | null> {
  try {
    const session = await getServerSession(authOptions)
    const apiClient = await getApiClient(session)

    const response = await apiClient.integrations.integrationsJiraDashboardDataRetrieve()
    return response as JiraDashboardData
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null // No integration found
    }
    console.error('Error fetching Jira dashboard data:', error)
    return null
  }
}