/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ChatService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Send a message to the AI assistant with Jira context
     * @param requestBody
     * @returns any
     * @throws ApiError
     */
    public chatMessageCreate(
        requestBody?: {
            /**
             * User message
             */
            message: string;
            /**
             * Previous conversation messages
             */
            conversation_history?: Array<{
                role?: 'user' | 'assistant';
                content?: string;
            }>;
        },
    ): CancelablePromise<{
        response?: string;
        function_calls?: number;
    }> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/chat/message/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
