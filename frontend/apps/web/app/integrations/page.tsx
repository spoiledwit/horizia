import { getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'
import { authOptions } from '@/lib/auth'
import { JiraIntegrationCard } from '@/components/jira-integration-card'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Integrations - Horizia'
}

export default async function IntegrationsPage() {
  const session = await getServerSession(authOptions)
  
  if (!session) {
    redirect('/login')
  }

  return (
    <div className="fixed inset-0 overflow-hidden">
      <div className="h-full flex flex-col bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 flex-shrink-0">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-semibold">Horizia</h1>
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">{session.user?.username || 'User'}</span>
                <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-medium">
                  {session.user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 bg-white border-r border-gray-200 flex-shrink-0 flex flex-col">
            <div className="p-4 space-y-2 flex-1">
              <a href="/dashboard" className="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg flex items-center gap-3 hover:bg-gray-200 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Dashboard
              </a>
              <a href="/integrations" className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg flex items-center gap-3 hover:bg-blue-700 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Integrations
              </a>
            </div>
            <div className="p-4 border-t border-gray-200">
              <form action="/api/auth/signout" method="POST">
                <button type="submit" className="w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg flex items-center gap-3 transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Logout
                </button>
              </form>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto">
            <div className="p-8 max-w-4xl mx-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2">Integrations</h2>
                <p className="text-gray-600">Connect your tools to get AI-powered insights from your team's activity</p>
              </div>

              <div className="grid grid-cols-2 gap-6">
                {/* Slack Integration */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                      <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold">Slack</h3>
                      <p className="text-sm text-gray-600">Team communication insights</p>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-4">
                    Connect Slack to analyze team communication patterns, detect blockers, and get standup summaries.
                  </p>

                  <div className="space-y-3 mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Sentiment analysis</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Discussion summaries</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Blocker detection</span>
                    </div>
                  </div>

                  <button className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                    Connect Slack Workspace
                  </button>
                </div>

                {/* Jira Integration */}
                <JiraIntegrationCard />
              </div>

              <div className="mt-8 p-6 bg-gray-100 rounded-lg">
                <h4 className="font-semibold mb-2">How it works</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Once connected, Horizia's AI will analyze your team's activity across these platforms to provide actionable insights:
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-purple-600 mt-0.5">•</span>
                    <span>Real-time detection of blockers and risks</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-600 mt-0.5">•</span>
                    <span>Team sentiment and communication analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-600 mt-0.5">•</span>
                    <span>Sprint progress and velocity insights</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-600 mt-0.5">•</span>
                    <span>Automated standup summaries and reports</span>
                  </li>
                </ul>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}