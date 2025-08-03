from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from .models import JiraIntegration

User = get_user_model()


class UserCurrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]


class UserCurrentErrorSerializer(serializers.Serializer):
    username = serializers.ListSerializer(child=serializers.CharField(), required=False)
    first_name = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )
    last_name = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password_new = serializers.CharField(style={"input_type": "password"})
    password_retype = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    default_error_messages = {
        "password_mismatch": _("Current password is not matching"),
        "password_invalid": _("Password does not meet all requirements"),
        "password_same": _("Both new and current passwords are same"),
    }

    class Meta:
        model = User
        fields = ["password", "password_new", "password_retype"]

    def validate(self, attrs):
        request = self.context.get("request", None)

        if not request.user.check_password(attrs["password"]):
            raise serializers.ValidationError(
                {"password": self.default_error_messages["password_mismatch"]}
            )

        try:
            validate_password(attrs["password_new"])
        except ValidationError as e:
            raise exceptions.ValidationError({"password_new": list(e.messages)}) from e

        if attrs["password_new"] != attrs["password_retype"]:
            raise serializers.ValidationError(
                {"password_retype": self.default_error_messages["password_invalid"]}
            )

        if attrs["password_new"] == attrs["password"]:
            raise serializers.ValidationError(
                {"password_new": self.default_error_messages["password_same"]}
            )
        return super().validate(attrs)


class UserChangePasswordErrorSerializer(serializers.Serializer):
    password = serializers.ListSerializer(child=serializers.CharField(), required=False)
    password_new = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )
    password_retype = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password_retype = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    default_error_messages = {
        "password_mismatch": _("Password are not matching."),
        "password_invalid": _("Password does not meet all requirements."),
    }

    class Meta:
        model = User
        fields = ["username", "password", "password_retype"]

    def validate(self, attrs):
        password_retype = attrs.pop("password_retype")

        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError:
            self.fail("password_invalid")

        if attrs["password"] == password_retype:
            return attrs

        return self.fail("password_mismatch")

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)

            # By default newly registered accounts are inactive.
            user.is_active = False
            user.save(update_fields=["is_active"])

        return user


class UserCreateErrorSerializer(serializers.Serializer):
    username = serializers.ListSerializer(child=serializers.CharField(), required=False)
    password = serializers.ListSerializer(child=serializers.CharField(), required=False)
    password_retype = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )


class JiraIntegrationStatusSerializer(serializers.ModelSerializer):
    """Serializer for Jira integration status"""
    is_connected = serializers.SerializerMethodField()
    is_token_expired = serializers.ReadOnlyField()
    has_outdated_scopes = serializers.ReadOnlyField()
    needs_reauth = serializers.SerializerMethodField()
    
    class Meta:
        model = JiraIntegration
        fields = [
            'is_connected', 
            'site_name', 
            'site_url', 
            'is_active', 
            'is_token_expired',
            'has_outdated_scopes',
            'needs_reauth',
            'last_sync_at',
            'created_at'
        ]
    
    def get_is_connected(self, obj):
        return obj.is_active and not obj.is_token_expired and not obj.has_outdated_scopes
    
    def get_needs_reauth(self, obj):
        return obj.is_token_expired or obj.has_outdated_scopes


class JiraOAuthInitSerializer(serializers.Serializer):
    """Serializer for initiating Jira OAuth flow"""
    authorization_url = serializers.URLField(read_only=True)
    state = serializers.CharField(read_only=True)


class JiraOAuthCallbackSerializer(serializers.Serializer):
    """Serializer for handling Jira OAuth callback"""
    code = serializers.CharField(required=True)
    state = serializers.CharField(required=True)


class JiraProjectSerializer(serializers.Serializer):
    """Serializer for Jira project data"""
    id = serializers.CharField()
    key = serializers.CharField()
    name = serializers.CharField()
    project_type_key = serializers.CharField()
    lead = serializers.DictField(required=False)
