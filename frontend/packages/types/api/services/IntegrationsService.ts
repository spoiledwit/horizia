/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JiraIntegrationStatus } from '../models/JiraIntegrationStatus';
import type { JiraOAuthInit } from '../models/JiraOAuthInit';
import type { PaginatedJiraProjectList } from '../models/PaginatedJiraProjectList';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class IntegrationsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Handle OAuth callback and create integration
     * @returns JiraIntegrationStatus
     * @throws ApiError
     */
    public integrationsJiraCallbackRetrieve(): CancelablePromise<JiraIntegrationStatus> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/integrations/jira/callback/',
            errors: {
                400: `No response body`,
            },
        });
    }
    /**
     * Initiate Jira OAuth flow
     * @returns JiraOAuthInit
     * @throws ApiError
     */
    public integrationsJiraConnectCreate(): CancelablePromise<JiraOAuthInit> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/integrations/jira/connect/',
            errors: {
                400: `No response body`,
            },
        });
    }
    /**
     * Get comprehensive dashboard data from Jira
     * @returns any No response body
     * @throws ApiError
     */
    public integrationsJiraDashboardDataRetrieve(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/integrations/jira/dashboard-data/',
            errors: {
                400: `No response body`,
                404: `No response body`,
            },
        });
    }
    /**
     * Disconnect Jira integration
     * @returns void
     * @throws ApiError
     */
    public integrationsJiraDisconnectDestroy(): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/integrations/jira/disconnect/',
            errors: {
                404: `No response body`,
            },
        });
    }
    /**
     * Get projects from user's Jira instance
     * @param page A page number within the paginated result set.
     * @returns PaginatedJiraProjectList
     * @throws ApiError
     */
    public integrationsJiraProjectsList(
        page?: number,
    ): CancelablePromise<PaginatedJiraProjectList> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/integrations/jira/projects/',
            query: {
                'page': page,
            },
            errors: {
                400: `No response body`,
                404: `No response body`,
            },
        });
    }
    /**
     * Get current Jira integration status for the user
     * @returns JiraIntegrationStatus
     * @throws ApiError
     */
    public integrationsJiraStatusRetrieve(): CancelablePromise<JiraIntegrationStatus> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/integrations/jira/status/',
            errors: {
                404: `No response body`,
            },
        });
    }
}
