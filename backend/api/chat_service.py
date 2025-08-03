import json
import os
from typing import List, Dict, Any
from openai import OpenAI
from django.conf import settings
from .services import JiraOAuthService
from .models import JiraIntegration


class ChatService:
    """Service for handling OpenAI chat with Jira function calls"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_jira_tools(self) -> List[Dict]:
        """Define function tools for Jira integration"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_projects",
                    "description": "Get all projects from user's Jira instance",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_issues",
                    "description": "Get issues assigned to the current user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": ["string", "null"],
                                "description": "Filter by status (e.g., 'In Progress', 'Done', 'To Do')",
                                "enum": ["To Do", "In Progress", "Done", None]
                            },
                            "limit": {
                                "type": ["integer", "null"],
                                "description": "Maximum number of issues to return (default: 20)",
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["status", "limit"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_issues",
                    "description": "Search for issues using JQL (Jira Query Language)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "jql": {
                                "type": "string",
                                "description": "JQL query string (e.g., 'project = MYPROJ AND status = \"In Progress\"')"
                            },
                            "limit": {
                                "type": ["integer", "null"],
                                "description": "Maximum number of issues to return (default: 20)",
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["jql", "limit"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_project_details",
                    "description": "Get detailed information about a specific project",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "The project key (e.g., 'MYPROJ', 'DEMO')"
                            }
                        },
                        "required": ["project_key"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_boards",
                    "description": "Get agile boards for a project",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": ["string", "null"],
                                "description": "Project key to filter boards (optional)"
                            }
                        },
                        "required": ["project_key"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]
    
    def execute_jira_function(self, user, function_name: str, arguments: Dict) -> str:
        """Execute a Jira function call"""
        try:
            # Get user's Jira integration
            integration = JiraIntegration.objects.get(user=user, is_active=True)
            jira = JiraOAuthService.get_jira_client(integration)
            
            if function_name == "get_projects":
                projects = jira.projects()
                # Handle different project data formats
                if isinstance(projects, dict) and 'values' in projects:
                    project_list = projects['values']
                else:
                    project_list = projects if isinstance(projects, list) else []
                
                result = []
                for project in project_list[:10]:  # Limit to 10 projects
                    result.append({
                        "key": project.get("key"),
                        "name": project.get("name"),
                        "description": project.get("description", ""),
                        "projectTypeKey": project.get("projectTypeKey"),
                        "lead": project.get("lead", {}).get("displayName") if project.get("lead") else None
                    })
                return json.dumps({"projects": result})
            
            elif function_name == "get_user_issues":
                current_user = jira.myself()
                status_filter = f' AND status != "{arguments["status"]}"' if arguments.get("status") == "Done" else f' AND status = "{arguments["status"]}"' if arguments.get("status") else ""
                limit = arguments.get("limit", 20)
                
                jql = f'assignee = "{current_user["emailAddress"]}"{status_filter} ORDER BY updated DESC'
                issues = jira.jql(jql, limit=limit)
                
                result = []
                for issue in issues["issues"]:
                    result.append({
                        "key": issue["key"],
                        "summary": issue["fields"]["summary"],
                        "status": issue["fields"]["status"]["name"],
                        "priority": issue["fields"]["priority"]["name"] if issue["fields"].get("priority") else "None",
                        "project": issue["fields"]["project"]["name"],
                        "updated": issue["fields"]["updated"]
                    })
                return json.dumps({"issues": result})
            
            elif function_name == "search_issues":
                jql = arguments["jql"]
                limit = arguments.get("limit", 20)
                
                issues = jira.jql(jql, limit=limit)
                
                result = []
                for issue in issues["issues"]:
                    result.append({
                        "key": issue["key"],
                        "summary": issue["fields"]["summary"],
                        "status": issue["fields"]["status"]["name"],
                        "priority": issue["fields"]["priority"]["name"] if issue["fields"].get("priority") else "None",
                        "project": issue["fields"]["project"]["name"],
                        "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"].get("assignee") else "Unassigned",
                        "updated": issue["fields"]["updated"]
                    })
                return json.dumps({"issues": result, "total": issues.get("total", len(result))})
            
            elif function_name == "get_project_details":
                project_key = arguments["project_key"]
                
                # Get project info
                projects = jira.projects()
                project_list = projects['values'] if isinstance(projects, dict) and 'values' in projects else projects
                
                project = None
                for p in project_list:
                    if p.get("key") == project_key:
                        project = p
                        break
                
                if not project:
                    return json.dumps({"error": f"Project {project_key} not found"})
                
                # Get issues count for project
                try:
                    issues = jira.jql(f'project = {project_key}', limit=1)
                    total_issues = issues.get("total", 0)
                except:
                    total_issues = 0
                
                result = {
                    "key": project.get("key"),
                    "name": project.get("name"),
                    "description": project.get("description", ""),
                    "projectTypeKey": project.get("projectTypeKey"),
                    "lead": project.get("lead", {}).get("displayName") if project.get("lead") else None,
                    "total_issues": total_issues
                }
                return json.dumps({"project": result})
            
            elif function_name == "get_boards":
                project_key = arguments.get("project_key")
                
                try:
                    boards = jira.boards(projectKeyOrId=project_key) if project_key else jira.boards()
                    
                    result = []
                    board_list = boards.get('values', []) if isinstance(boards, dict) else boards
                    
                    for board in board_list[:10]:  # Limit to 10 boards
                        result.append({
                            "id": board.get("id"),
                            "name": board.get("name"),
                            "type": board.get("type"),
                            "location": board.get("location", {}).get("displayName") if board.get("location") else None
                        })
                    
                    return json.dumps({"boards": result})
                except Exception as e:
                    return json.dumps({"error": f"Could not fetch boards: {str(e)}"})
            
            else:
                return json.dumps({"error": f"Unknown function: {function_name}"})
                
        except JiraIntegration.DoesNotExist:
            return json.dumps({"error": "No Jira integration found. Please connect your Jira account first."})
        except Exception as e:
            return json.dumps({"error": f"Error executing {function_name}: {str(e)}"})
    
    def chat_with_jira_context(self, user, messages: List[Dict], stream: bool = False):
        """Handle chat with Jira function calling capability"""
        
        # Add system prompt with Jira context
        system_message = {
            "role": "system",
            "content": """You are Ask Pulse, an AI assistant for project management and Jira analytics. You help users understand their projects, track issues, and get insights from their Jira data.

You have access to the following Jira functions:
- get_projects: Get all projects in user's Jira instance
- get_user_issues: Get issues assigned to the current user (can filter by status)
- search_issues: Search issues using JQL queries
- get_project_details: Get detailed info about a specific project
- get_boards: Get agile boards (can filter by project)

When users ask about their work, projects, or issues, use these functions to provide accurate, up-to-date information. Always be helpful and provide actionable insights.

Some example queries you can help with:
- "What issues are assigned to me?"
- "Show me projects I'm working on"
- "Find all high priority bugs"
- "What's the status of project XYZ?"
- "Show me all issues in progress"

Be conversational and provide context with your responses. If you need to use JQL for searches, explain what you're doing."""
        }
        
        # Prepare messages with system prompt
        chat_messages = [system_message] + messages
        
        # Get Jira function tools
        tools = self.get_jira_tools()
        
        if stream:
            return self._handle_streaming_chat(user, chat_messages, tools)
        else:
            return self._handle_regular_chat(user, chat_messages, tools)
    
    def _handle_regular_chat(self, user, messages, tools):
        """Handle non-streaming chat"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2000
            )
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.tool_calls:
                # Add assistant's message with tool calls to conversation
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                })
                
                # Execute function calls
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    result = self.execute_jira_function(user, function_name, arguments)
                    
                    # Add function result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                # Get final response with function results
                final_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=tools,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                return {
                    "content": final_response.choices[0].message.content,
                    "function_calls": len(message.tool_calls)
                }
            else:
                return {
                    "content": message.content,
                    "function_calls": 0
                }
                
        except Exception as e:
            return {
                "content": f"Sorry, I encountered an error: {str(e)}",
                "function_calls": 0
            }
    
    def _handle_streaming_chat(self, user, messages, tools):
        """Handle streaming chat (to be implemented)"""
        # For now, fall back to regular chat
        return self._handle_regular_chat(user, messages, tools)