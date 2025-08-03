from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging

from .serializers import (
    UserChangePasswordErrorSerializer,
    UserChangePasswordSerializer,
    UserCreateErrorSerializer,
    UserCreateSerializer,
    UserCurrentErrorSerializer,
    UserCurrentSerializer,
    JiraIntegrationStatusSerializer,
    JiraOAuthInitSerializer,
    JiraOAuthCallbackSerializer,
    JiraProjectSerializer,
)
from .models import JiraIntegration
from .chat_service import ChatService
from .services import JiraOAuthService

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserCurrentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "me":
            return UserCurrentSerializer
        elif self.action == "change_password":
            return UserChangePasswordSerializer

        return super().get_serializer_class()

    @extend_schema(
        responses={
            200: UserCreateSerializer,
            400: UserCreateErrorSerializer,
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: UserCurrentSerializer,
            400: UserCurrentErrorSerializer,
        }
    )
    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == "GET":
            serializer = self.get_serializer(self.request.user)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = self.get_serializer(
                self.request.user, data=request.data, partial=False
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = self.get_serializer(
                self.request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @extend_schema(
        responses={
            204: None,
            400: UserChangePasswordErrorSerializer,
        }
    )
    @action(["post"], url_path="change-password", detail=False)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["password_new"])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["delete"], url_path="delete-account", detail=False)
    def delete_account(self, request, *args, **kwargs):
        self.request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


logger = logging.getLogger(__name__)


class JiraIntegrationViewSet(viewsets.GenericViewSet):
    """ViewSet for Jira integration management"""
    permission_classes = [IsAuthenticated]
    serializer_class = JiraIntegrationStatusSerializer
    
    def get_queryset(self):
        return JiraIntegration.objects.filter(user=self.request.user)
    
    @extend_schema(
        responses={
            200: JiraIntegrationStatusSerializer,
            404: None,
        }
    )
    @action(["get"], detail=False, url_path="status")
    def status(self, request, *args, **kwargs):
        """Get current Jira integration status for the user"""
        try:
            integration = JiraIntegration.objects.get(user=request.user)
            serializer = JiraIntegrationStatusSerializer(integration)
            return Response(serializer.data)
        except JiraIntegration.DoesNotExist:
            return Response(
                {"is_connected": False, "message": "No Jira integration found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        request=None,  # No request body required
        responses={
            200: JiraOAuthInitSerializer,
            400: None,
        }
    )
    @action(["post"], detail=False, url_path="connect")
    def connect(self, request, *args, **kwargs):
        """Initiate Jira OAuth flow"""
        try:
            authorization_url, state = JiraOAuthService.generate_authorization_url(request.user.id)
            print(f"Generated Jira OAuth authorization URL: {authorization_url}")
            
            # Create response data directly since fields are read_only
            response_data = {
                'authorization_url': authorization_url,
                'state': state
            }
            
            print("response data:", response_data)
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error initiating Jira OAuth: {str(e)}")
            return Response(
                {"error": "Failed to initiate OAuth flow"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        request=JiraOAuthCallbackSerializer,
        responses={
            200: JiraIntegrationStatusSerializer,
            400: None,
        }
    )
    @action(["get"], detail=False, url_path="callback", permission_classes=[AllowAny])
    def callback(self, request, *args, **kwargs):
        """Handle OAuth callback and create integration"""
        # OAuth callbacks come as GET requests with query parameters
        code = request.GET.get('code')
        state = request.GET.get('state')
        
        print(f"Received callback with code: {code[:20] if code else 'None'}... and state: {state}")
        
        if not code or not state:
            return Response(
                {"error": "Missing required parameters: code and state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Decode state to get user information
        state_data = JiraOAuthService.decode_state(state)
        if not state_data or 'user_id' not in state_data:
            return Response(
                {"error": "Invalid state parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the user from the state
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=state_data['user_id'])
            
            # Exchange code for token
            token_data = JiraOAuthService.exchange_code_for_token(code, state)
            
            # Get accessible resources
            resources = JiraOAuthService.get_accessible_resources(token_data['access_token'])
            
            # Create or update integration
            integration = JiraOAuthService.create_or_update_integration(
                user=user,
                token_data=token_data,
                resources=resources
            )
            
            # Redirect to frontend integrations page with success message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect("http://localhost:3000/integrations?jira_connected=success")
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in Jira OAuth callback: {str(e)}")
            # Redirect to frontend integrations page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect("http://localhost:3000/integrations?jira_connected=error")
    
    @extend_schema(
        responses={
            204: None,
            404: None,
        }
    )
    @action(["delete"], detail=False, url_path="disconnect")
    def disconnect(self, request, *args, **kwargs):
        """Disconnect Jira integration"""
        success = JiraOAuthService.disconnect_integration(request.user)
        
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "No integration found to disconnect"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        responses={
            200: JiraProjectSerializer(many=True),
            400: None,
            404: None,
        }
    )
    @action(["get"], detail=False, url_path="projects")
    def projects(self, request, *args, **kwargs):
        """Get projects from user's Jira instance"""
        try:
            integration = JiraIntegration.objects.get(user=request.user)
            
            if not integration.is_active:
                return Response(
                    {"error": "Jira integration is not active"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            projects = JiraOAuthService.get_projects(integration)
            serializer = JiraProjectSerializer(projects, many=True)
            
            return Response(serializer.data)
            
        except JiraIntegration.DoesNotExist:
            return Response(
                {"error": "No Jira integration found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching Jira projects: {str(e)}")
            return Response(
                {"error": "Failed to fetch projects"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        responses={
            200: None,  # Will define proper serializer later
            400: None,
            404: None,
        }
    )
    @action(["get"], detail=False, url_path="dashboard-data")
    def dashboard_data(self, request, *args, **kwargs):
        """Get comprehensive dashboard data from Jira"""
        try:
            integration = JiraIntegration.objects.get(user=request.user)
            
            if not integration.is_active:
                return Response(
                    {"error": "Jira integration is not active"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            dashboard_data = JiraOAuthService.get_dashboard_data(integration)
            
            return Response(dashboard_data)
            
        except JiraIntegration.DoesNotExist:
            return Response(
                {"error": "No Jira integration found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching Jira dashboard data: {str(e)}")
            return Response(
                {"error": "Failed to fetch dashboard data"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChatViewSet(viewsets.GenericViewSet):
    """ViewSet for AI chat with Jira function calling"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "User message"},
                    "conversation_history": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["user", "assistant"]},
                                "content": {"type": "string"}
                            }
                        },
                        "description": "Previous conversation messages"
                    }
                },
                "required": ["message"]
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "function_calls": {"type": "integer"}
                }
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
            500: {"type": "object", "properties": {"error": {"type": "string"}}}
        },
        description="Send a message to the AI assistant with Jira context"
    )
    @action(detail=False, methods=['post'], url_path='message')
    def send_message(self, request):
        """Send a message to the AI chat assistant"""
        try:
            message = request.data.get('message')
            conversation_history = request.data.get('conversation_history', [])
            
            if not message:
                return Response(
                    {"error": "Message is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Build conversation messages
            messages = []
            for msg in conversation_history:
                if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Get chat response
            chat_service = ChatService()
            result = chat_service.chat_with_jira_context(request.user, messages)
            
            return Response({
                "response": result["content"],
                "function_calls": result["function_calls"]
            })
            
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            return Response(
                {"error": "Failed to process chat message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
