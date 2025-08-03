/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for Jira integration status
 */
export type JiraIntegrationStatus = {
    readonly is_connected: string;
    site_name: string;
    site_url: string;
    is_active?: boolean;
    readonly is_token_expired: string;
    readonly has_outdated_scopes: string;
    readonly needs_reauth: string;
    last_sync_at?: string | null;
    readonly created_at: string;
};

