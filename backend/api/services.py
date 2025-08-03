import requests
import secrets
from urllib.parse import urlencode
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from atlassian import Jira
from .models import JiraIntegration


class JiraOAuthService:
    """Service class for handling Jira OAuth 2.0 integration"""
    
    AUTHORIZATION_BASE_URL = "https://auth.atlassian.com/authorize"
    TOKEN_URL = "https://auth.atlassian.com/oauth/token"
    ACCESSIBLE_RESOURCES_URL = "https://api.atlassian.com/oauth/token/accessible-resources"
    
    SCOPES = [
        "read:jira-user",
        "read:jira-work", 
        "write:jira-work",
        "read:project:jira",
        "read:board-scope:jira-software",
        "read:sprint:jira-software",
        "read:issue:jira-software",
        "read:epic:jira-software",
        "offline_access"
    ]
    
    @classmethod
    def generate_authorization_url(cls, user_id):
        """Generate authorization URL for OAuth flow"""
        import json
        import base64
        
        # Create state with user info encoded
        state_data = {
            'user_id': user_id,
            'nonce': secrets.token_urlsafe(16)
        }
        state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()
        
        params = {
            'audience': 'api.atlassian.com',
            'client_id': settings.JIRA_CLIENT_ID,
            'scope': ' '.join(cls.SCOPES),
            'redirect_uri': settings.JIRA_REDIRECT_URI,
            'state': state,
            'response_type': 'code',
            'prompt': 'consent'
        }
        
        authorization_url = f"{cls.AUTHORIZATION_BASE_URL}?{urlencode(params)}"
        return authorization_url, state
    
    @classmethod
    def decode_state(cls, state):
        """Decode state parameter to get user info"""
        import json
        import base64
        
        try:
            decoded_bytes = base64.urlsafe_b64decode(state.encode())
            state_data = json.loads(decoded_bytes.decode())
            return state_data
        except Exception:
            return None
    
    @classmethod
    def exchange_code_for_token(cls, code, state):
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.JIRA_CLIENT_ID,
            'client_secret': settings.JIRA_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.JIRA_REDIRECT_URI,
        }
        
        response = requests.post(cls.TOKEN_URL, data=data)
        response.raise_for_status()
        
        return response.json()
    
    @classmethod
    def get_accessible_resources(cls, access_token):
        """Get accessible Atlassian resources for the user"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }
        
        response = requests.get(cls.ACCESSIBLE_RESOURCES_URL, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    @classmethod
    def refresh_access_token(cls, refresh_token):
        """Refresh an expired access token"""
        data = {
            'grant_type': 'refresh_token',
            'client_id': settings.JIRA_CLIENT_ID,
            'client_secret': settings.JIRA_CLIENT_SECRET,
            'refresh_token': refresh_token,
        }
        
        response = requests.post(cls.TOKEN_URL, data=data)
        response.raise_for_status()
        
        return response.json()
    
    @classmethod
    def create_or_update_integration(cls, user, token_data, resources):
        """Create or update Jira integration for user"""
        if not resources:
            raise ValueError("No accessible resources found")
        
        # Use the first accessible resource (user's primary Jira instance)
        resource = resources[0]
        
        # Calculate token expiration
        expires_in = token_data.get('expires_in', 3600)
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        
        integration, created = JiraIntegration.objects.update_or_create(
            user=user,
            defaults={
                '_access_token': '',  # Will be set via property
                '_refresh_token': '',  # Will be set via property
                'token_type': token_data.get('token_type', 'Bearer'),
                'expires_at': expires_at,
                'cloud_id': resource['id'],
                'site_url': resource['url'],
                'site_name': resource['name'],
                'is_active': True,
                'scopes_version': 2,  # Current version with Jira Software scopes
            }
        )
        
        # Set encrypted tokens
        integration.access_token = token_data['access_token']
        integration.refresh_token = token_data.get('refresh_token', '')
        integration.save()
        
        return integration
    
    @classmethod
    def get_jira_client(cls, integration):
        """Get authenticated Jira client for integration"""
        # Debug print
        print(f"Creating Jira client for URL: {integration.site_url}")
        print(f"Token expired: {integration.is_token_expired}")
        print(f"Token expires at: {integration.expires_at}")
        print(f"Current time: {timezone.now()}")
        print(f"Client ID available: {settings.JIRA_CLIENT_ID is not None}")
        
        # Force token refresh if it's close to expiring (within 5 minutes)
        time_until_expiry = integration.expires_at - timezone.now()
        if time_until_expiry.total_seconds() < 300:  # Less than 5 minutes
            print("Token is close to expiring, forcing refresh...")
            integration.expires_at = timezone.now() - timedelta(seconds=1)  # Force expiry
        
        if integration.is_token_expired:
            # Try to refresh the token
            try:
                if not settings.JIRA_CLIENT_ID or not settings.JIRA_CLIENT_SECRET:
                    raise ValueError("Jira OAuth credentials not configured")
                    
                token_data = cls.refresh_access_token(integration.refresh_token)
                
                # Update integration with new token
                expires_in = token_data.get('expires_in', 3600)
                integration.expires_at = timezone.now() + timedelta(seconds=expires_in)
                integration.access_token = token_data['access_token']
                if 'refresh_token' in token_data:
                    integration.refresh_token = token_data['refresh_token']
                integration.save()
                
            except Exception as e:
                print(f"Token refresh failed: {str(e)}")
                # Token refresh failed, mark integration as inactive
                integration.is_active = False
                integration.save()
                raise ValueError("Token refresh failed. User needs to re-authenticate.")
        
        # Create Jira client with OAuth2 token
        # For OAuth2 in atlassian-python-api, we need to use specific format
        try:
            # Method 1: Use token parameter (Personal Access Token style)
            jira = Jira(
                url=integration.site_url,
                token=integration.access_token,
                cloud=True
            )
            
            # Test the connection by getting current user
            try:
                current_user = jira.myself()  # Correct method name
                print(f"Successfully connected to Jira as: {current_user.get('displayName', 'Unknown')}")
                return jira
            except Exception as auth_e:
                print(f"Auth test failed with token method: {str(auth_e)}")
                raise auth_e
                
        except Exception as e:
            print(f"Error with token method: {str(e)}")
            
            # Method 2: Try with manual Authorization header using requests
            try:
                import requests
                
                # Create a custom Jira client that manually sets the Authorization header
                class OAuthJira:
                    def __init__(self, url, access_token):
                        self.url = url.rstrip('/')
                        self.access_token = access_token
                        self.session = requests.Session()
                        self.session.headers.update({
                            'Authorization': f'Bearer {access_token}',
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        })
                    
                    def _make_request(self, method, endpoint, **kwargs):
                        # For Atlassian Cloud OAuth, we need to use the cloud_id in the URL
                        # Try multiple URL formats based on endpoint type
                        if endpoint.startswith('agile/'):
                            # Agile API endpoints use /rest/agile/1.0/ path
                            urls_to_try = [
                                f"https://api.atlassian.com/ex/jira/{integration.cloud_id}/rest/{endpoint.lstrip('/')}",  # Cloud agile format
                            ]
                        else:
                            # Standard API endpoints use /rest/api/2/ path
                            urls_to_try = [
                                f"https://api.atlassian.com/ex/jira/{integration.cloud_id}/rest/api/2/{endpoint.lstrip('/')}",  # Cloud format
                                f"{self.url}/rest/api/2/{endpoint.lstrip('/')}",  # Standard format (fallback)
                            ]
                        
                        last_error = None
                        for url in urls_to_try:
                            try:
                                print(f"Trying URL: {url}")
                                response = self.session.request(method, url, **kwargs)
                                response.raise_for_status()
                                return response.json() if response.content else {}
                            except Exception as e:
                                print(f"Failed with URL {url}: {str(e)}")
                                last_error = e
                                continue
                        
                        # If all URLs failed, raise the last error
                        if last_error:
                            raise last_error
                        return {}
                    
                    def projects(self):
                        return self._make_request('GET', 'project/search')
                    
                    def myself(self):
                        return self._make_request('GET', 'myself')
                    
                    def jql(self, jql_query, limit=50):
                        params = {'jql': jql_query, 'maxResults': limit}
                        return self._make_request('GET', 'search', params=params)
                    
                    def boards(self, projectKeyOrId=None):
                        endpoint = 'board'
                        params = {}
                        if projectKeyOrId:
                            params['projectKeyOrId'] = projectKeyOrId
                        return self._make_request('GET', f'agile/1.0/{endpoint}', params=params)
                    
                    def sprints(self, board_id, state=None):
                        endpoint = f'agile/1.0/board/{board_id}/sprint'
                        params = {}
                        if state:
                            params['state'] = state
                        return self._make_request('GET', endpoint, params=params)
                    
                    def sprint_issues(self, sprint_id):
                        endpoint = f'agile/1.0/sprint/{sprint_id}/issue'
                        return self._make_request('GET', endpoint)
                
                jira = OAuthJira(integration.site_url, integration.access_token)
                
                # Debug: Print token info (first/last few chars only for security)
                token = integration.access_token
                print(f"Using token: {token[:10]}...{token[-10:] if len(token) > 20 else token}")
                print(f"Token length: {len(token)}")
                print(f"Site URL: {integration.site_url}")
                print(f"Cloud ID: {integration.cloud_id}")
                
                # Test a simple API call first to verify token
                test_url = f"https://api.atlassian.com/oauth/token/accessible-resources"
                test_headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
                test_response = requests.get(test_url, headers=test_headers)
                print(f"Accessible resources test: {test_response.status_code}")
                if test_response.status_code == 200:
                    resources = test_response.json()
                    print(f"Found {len(resources)} accessible resources")
                else:
                    print(f"Accessible resources failed: {test_response.text}")
                
                # Test the connection
                current_user = jira.myself()
                print(f"Successfully connected with custom OAuth client as: {current_user.get('displayName', 'Unknown')}")
                return jira
                
            except Exception as e2:
                print(f"Error with custom OAuth client: {str(e2)}")
                raise ValueError(f"Failed to create Jira client with both methods: {str(e)} / {str(e2)}")
    
    @classmethod
    def get_projects(cls, integration):
        """Get projects from user's Jira instance"""
        jira = cls.get_jira_client(integration)
        
        try:
            projects = jira.projects()
            integration.last_sync_at = timezone.now()
            integration.save(update_fields=['last_sync_at'])
            return projects
        except Exception as e:
            raise ValueError(f"Failed to fetch projects: {str(e)}")
    
    @classmethod
    def get_dashboard_data(cls, integration):
        """Get comprehensive dashboard data from Jira"""
        jira = cls.get_jira_client(integration)
        
        try:
            # Get all projects
            projects = jira.projects()
            
            # Get current user
            current_user = jira.myself()
            
            # Get issues assigned to current user
            user_issues_jql = f'assignee = "{current_user["emailAddress"]}" AND status != Done ORDER BY updated DESC'
            user_issues = jira.jql(user_issues_jql, limit=100)
            
            # Get recent activity (issues updated in last 7 days)
            recent_activity_jql = f'updated >= -7d ORDER BY updated DESC'
            recent_activity = jira.jql(recent_activity_jql, limit=50)
            
            # Get sprint data if available
            sprint_data = cls._get_sprint_data(jira, projects)
            
            # Get team velocity data
            velocity_data = cls._get_velocity_data(jira, projects)
            
            # Update last sync time
            integration.last_sync_at = timezone.now()
            integration.save(update_fields=['last_sync_at'])
            
            # Handle projects count for stats
            if isinstance(projects, dict) and 'values' in projects:
                total_projects = len(projects['values'])
                projects_for_frontend = projects['values']
            elif isinstance(projects, list):
                total_projects = len(projects)
                projects_for_frontend = projects
            else:
                total_projects = 0
                projects_for_frontend = []
            
            return {
                'projects': projects_for_frontend,
                'current_user': current_user,
                'user_issues': user_issues,
                'recent_activity': recent_activity,
                'sprint_data': sprint_data,
                'velocity_data': velocity_data,
                'stats': {
                    'total_projects': total_projects,
                    'user_open_issues': len([i for i in user_issues['issues'] if i['fields']['status']['name'] != 'Done']),
                    'recent_activity_count': len(recent_activity['issues']),
                }
            }
        except Exception as e:
            raise ValueError(f"Failed to fetch dashboard data: {str(e)}")
    
    @classmethod
    def _get_sprint_data(cls, jira, projects):
        """Get sprint data for projects"""
        sprint_data = []
        
        # Handle different project data formats
        if isinstance(projects, dict) and 'values' in projects:
            project_list = projects['values']
        elif isinstance(projects, list):
            project_list = projects
        else:
            print(f"Unexpected projects format: {type(projects)}")
            return sprint_data
        
        for project in project_list[:5]:  # Limit to first 5 projects for performance
            try:
                # Get boards for the project
                boards = jira.boards(projectKeyOrId=project['key'])
                
                for board in boards['values'][:2]:  # Limit boards per project
                    try:
                        # Get active sprints
                        sprints = jira.sprints(board['id'], state='active')
                        
                        for sprint in sprints['values']:
                            # Get issues in sprint
                            sprint_issues = jira.sprint_issues(sprint['id'])
                            
                            # Calculate sprint progress
                            total_issues = len(sprint_issues['issues'])
                            done_issues = len([i for i in sprint_issues['issues'] 
                                             if i['fields']['status']['statusCategory']['name'] == 'Done'])
                            
                            sprint_data.append({
                                'id': sprint['id'],
                                'name': sprint['name'],
                                'state': sprint['state'],
                                'start_date': sprint.get('startDate'),
                                'end_date': sprint.get('endDate'),
                                'project_key': project['key'],
                                'project_name': project['name'],
                                'board_name': board['name'],
                                'total_issues': total_issues,
                                'done_issues': done_issues,
                                'progress_percentage': (done_issues / total_issues * 100) if total_issues > 0 else 0
                            })
                    except Exception:
                        continue  # Skip boards that fail
            except Exception:
                continue  # Skip projects that fail
        
        return sprint_data
    
    @classmethod
    def _get_velocity_data(cls, jira, projects):
        """Get velocity data for the team"""
        velocity_data = []
        
        try:
            # Handle different project data formats
            if isinstance(projects, dict) and 'values' in projects:
                project_list = projects['values']
            elif isinstance(projects, list):
                project_list = projects
            else:
                print(f"Unexpected projects format in velocity: {type(projects)}")
                return velocity_data
            
            # Get completed sprints from last 6 sprints across projects
            for project in project_list[:3]:  # Limit projects for performance
                try:
                    boards = jira.boards(projectKeyOrId=project['key'])
                    
                    for board in boards['values'][:1]:  # One board per project
                        try:
                            # Get closed sprints
                            sprints = jira.sprints(board['id'], state='closed')
                            
                            for sprint in sprints['values'][:6]:  # Last 6 sprints
                                sprint_issues = jira.sprint_issues(sprint['id'])
                                
                                # Calculate story points completed
                                story_points = 0
                                completed_issues = 0
                                
                                for issue in sprint_issues['issues']:
                                    if issue['fields']['status']['statusCategory']['name'] == 'Done':
                                        completed_issues += 1
                                        # Try to get story points (customfield_10016 is common)
                                        sp = issue['fields'].get('customfield_10016')
                                        if sp and isinstance(sp, (int, float)):
                                            story_points += sp
                                
                                velocity_data.append({
                                    'sprint_name': sprint['name'],
                                    'end_date': sprint.get('completeDate'),
                                    'story_points': story_points,
                                    'completed_issues': completed_issues,
                                    'project_key': project['key']
                                })
                        except Exception:
                            continue
                except Exception:
                    continue
        except Exception:
            pass
        
        return sorted(velocity_data, key=lambda x: x.get('end_date', ''), reverse=True)[:10]
    
    @classmethod
    def disconnect_integration(cls, user):
        """Disconnect Jira integration for user"""
        try:
            integration = JiraIntegration.objects.get(user=user)
            integration.delete()
            return True
        except JiraIntegration.DoesNotExist:
            return False