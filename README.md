# Ask Pulse

Ask Pulse is an AI-powered project management assistant that integrates with Jira to provide intelligent insights and analytics for your development workflow.

## Overview

Ask Pulse combines a Django REST API backend with a Next.js frontend to create a seamless experience for project management and Jira integration. The application features secure OAuth authentication with Jira, AI-powered chat assistance using OpenAI, and a modern responsive web interface.

## Architecture

### Backend (Django + Python)
- **Framework**: Django 5.1+ with Django REST Framework
- **Database**: PostgreSQL with encrypted token storage
- **Authentication**: JWT tokens with Django REST Framework SimpleJWT
- **AI Integration**: OpenAI GPT-4o-mini for chat functionality
- **Jira Integration**: OAuth 2.0 with encrypted token storage
- **API Documentation**: Automatic OpenAPI schema generation

### Frontend (Next.js + React)
- **Framework**: Next.js 15+ with React 19
- **Authentication**: NextAuth.js for session management
- **Styling**: Tailwind CSS with modern UI components
- **Type Safety**: TypeScript throughout
- **Package Management**: pnpm workspace for monorepo structure

## Features

- **Jira OAuth Integration**: Secure connection to Jira Cloud instances
- **AI Chat Assistant**: Natural language queries about your projects and issues
- **User Management**: Registration, login, profile management
- **Project Analytics**: Get insights from your Jira data
- **Real-time Data**: Live project and issue information
- **Responsive Design**: Works on desktop and mobile devices

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 18+
- pnpm
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd turbo
   ```

2. **Set up environment files**
   ```bash
   # Backend environment
   cp .env.backend.example .env.backend
   # Frontend environment  
   cp .env.frontend.example .env.frontend
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Django API on port 8000
   - Next.js frontend on port 3000

### Manual Development Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Run migrations**
   ```bash
   uv run -- python manage.py migrate
   ```

5. **Start development server**
   ```bash
   uv run -- python manage.py runserver
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Start development server**
   ```bash
   pnpm --filter web dev
   ```

## Configuration

### Backend Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Development mode flag
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for chat functionality
- `JIRA_CLIENT_ID`: Jira OAuth app client ID
- `JIRA_CLIENT_SECRET`: Jira OAuth app client secret
- `JIRA_TOKEN_ENCRYPTION_KEY`: Key for encrypting stored tokens

### Frontend Environment Variables

- `NEXTAUTH_URL`: Base URL for NextAuth
- `NEXTAUTH_SECRET`: Secret for NextAuth sessions
- `NEXT_PUBLIC_API_URL`: Backend API URL

## API Documentation

The API documentation is automatically generated and available at:
- Development: `http://localhost:8000/api/schema/swagger-ui/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## Jira Integration

### OAuth Setup

1. Create a Jira Cloud app at [developer.atlassian.com](https://developer.atlassian.com)
2. Configure OAuth 2.0 with required scopes:
   - `read:jira-work`
   - `read:jira-user`
   - `read:account`
3. Set redirect URI to your application's callback URL
4. Add client credentials to environment variables

### Available Functions

The AI assistant can perform these Jira operations:
- Get all projects
- Get user's assigned issues
- Search issues with JQL
- Get project details
- Get agile boards

## Testing

### Backend Tests
```bash
cd backend
uv run -- pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## Code Quality

### Backend
- **Linting**: Ruff with comprehensive rule set
- **Formatting**: Ruff auto-formatting
- **Type Checking**: Python type hints

### Frontend
- **Linting**: Biome for JavaScript/TypeScript
- **Type Checking**: TypeScript strict mode
- **Formatting**: Biome auto-formatting

## Security Features

- Encrypted storage of OAuth tokens using Fernet symmetric encryption
- JWT-based authentication for API access
- Secure session management with NextAuth
- Environment-based configuration for sensitive data
- Input validation and sanitization

## Deployment

The application is containerized and ready for deployment with Docker Compose. For production:

1. Set production environment variables
2. Configure SSL/TLS certificates
3. Set up proper database backups
4. Configure monitoring and logging

## License

See [LICENSE.md](LICENSE.md) for license information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.# horizia
