from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import base64


class User(AbstractUser):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("modified at"), auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email if self.email else self.username


class JiraIntegration(models.Model):
    """Model to store Jira OAuth integration data for users"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='jira_integration'
    )
    
    # OAuth token data (encrypted)
    _access_token = models.TextField(_("encrypted access token"))
    _refresh_token = models.TextField(_("encrypted refresh token"))
    token_type = models.CharField(_("token type"), max_length=50, default="Bearer")
    expires_at = models.DateTimeField(_("token expires at"))
    
    # Jira instance data
    cloud_id = models.CharField(_("cloud id"), max_length=255)
    site_url = models.URLField(_("site url"))
    site_name = models.CharField(_("site name"), max_length=255)
    
    # Integration status
    is_active = models.BooleanField(_("is active"), default=True)
    last_sync_at = models.DateTimeField(_("last sync at"), null=True, blank=True)
    scopes_version = models.IntegerField(_("scopes version"), default=1)  # Track scope updates
    
    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    class Meta:
        db_table = "jira_integrations"
        verbose_name = _("jira integration")
        verbose_name_plural = _("jira integrations")
    
    def __str__(self):
        return f"{self.user.username} - {self.site_name}"
    
    @property
    def is_token_expired(self):
        """Check if the access token has expired"""
        return timezone.now() >= self.expires_at
    
    @property
    def has_outdated_scopes(self):
        """Check if the integration was created with older scopes"""
        # Current scopes version is 2 (includes Jira Software scopes)
        return self.scopes_version < 2
    
    @property
    def access_token(self):
        """Decrypt and return the access token"""
        return self._decrypt_token(self._access_token)
    
    @access_token.setter
    def access_token(self, value):
        """Encrypt and store the access token"""
        self._access_token = self._encrypt_token(value)
    
    @property
    def refresh_token(self):
        """Decrypt and return the refresh token"""
        return self._decrypt_token(self._refresh_token)
    
    @refresh_token.setter
    def refresh_token(self, value):
        """Encrypt and store the refresh token"""
        self._refresh_token = self._encrypt_token(value)
    
    def _get_encryption_key(self):
        """Get or generate encryption key from settings"""
        # In production, this should come from environment variable
        key = getattr(settings, 'JIRA_TOKEN_ENCRYPTION_KEY', None)
        if not key:
            # Generate a key for development (should be set in production)
            key = Fernet.generate_key()
        if isinstance(key, str):
            key = key.encode()
        return key
    
    def _encrypt_token(self, token):
        """Encrypt a token using Fernet symmetric encryption"""
        if not token:
            return ""
        fernet = Fernet(self._get_encryption_key())
        return fernet.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token):
        """Decrypt a token using Fernet symmetric encryption"""
        if not encrypted_token:
            return ""
        fernet = Fernet(self._get_encryption_key())
        return fernet.decrypt(encrypted_token.encode()).decode()
