# Voice AI Sales Agent Admin Panel - Backend API

A comprehensive FastAPI backend for managing AI voice agents that make automated outbound calls for lead qualification, appointment setting, and follow-up campaigns.

## 🚀 Features

### Core Functionality
- **Google OAuth Authentication** with JWT token management
- **Agent Management** with Retell AI integration
- **Lead Management** with CSV import and custom fields
- **Call Scheduling** with business hours and retry logic
- **Template System** with 30+ industry-specific templates
- **Call History & Analytics** with detailed reporting
- **Webhook Processing** for real-time call updates

### Integrations
- **Retell AI** for voice conversations
- **Google Cloud SQL** for data persistence
- **Twilio & Plivo** for phone services
- **Google Cloud Scheduler** for automated calling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Retell AI     │
│   (React)       │◄──►│   Backend       │◄──►│   Voice API     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  PostgreSQL     │
                       │  Database       │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Google Cloud Project (for deployment)
- Retell AI API Key
- Google OAuth credentials

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd admin_backend_new
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 5. Database Setup
```bash
# Create database
createdb voiceai

# Run migrations
alembic upgrade head
```

### 6. Start Development Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET_KEY` | JWT signing secret | ✅ |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | ✅ |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | ✅ |
| `RETELL_API_KEY` | Retell AI API key | ✅ |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | ❌ |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | ❌ |
| `PLIVO_AUTH_ID` | Plivo auth ID | ❌ |
| `PLIVO_AUTH_TOKEN` | Plivo auth token | ❌ |

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/google-login` - Google OAuth login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/company` - Create company
- `GET /api/v1/auth/company` - Get user's company

### Agents
- `GET /api/v1/agents/` - List agents
- `POST /api/v1/agents/` - Create agent
- `GET /api/v1/agents/{id}` - Get agent details
- `PUT /api/v1/agents/{id}` - Update agent
- `PATCH /api/v1/agents/{id}/status` - Toggle agent status
- `DELETE /api/v1/agents/{id}` - Delete agent
- `GET /api/v1/agents/voices/` - List available voices

### Templates
- `GET /api/v1/templates/` - List templates
- `GET /api/v1/templates/industries` - Group by industry
- `GET /api/v1/templates/{id}` - Get template details

### Leads
- `GET /api/v1/leads/` - List leads
- `POST /api/v1/leads/` - Create lead
- `GET /api/v1/leads/{id}` - Get lead details
- `PUT /api/v1/leads/{id}` - Update lead
- `DELETE /api/v1/leads/{id}` - Delete lead
- `POST /api/v1/leads/csv-import` - Import leads from CSV

### Calls
- `GET /api/v1/calls/history` - Call history
- `GET /api/v1/calls/metrics` - Call analytics
- `POST /api/v1/calls/schedule` - Schedule immediate call
- `POST /api/v1/calls/run-scheduler` - Trigger scheduler
- `POST /api/v1/calls/webhook` - Retell webhook endpoint

## 🗃️ Database Schema

### Core Tables
- **users** - User accounts with Google OAuth
- **companies** - Multi-tenant company structure
- **agents** - Voice AI agents with Retell integration
- **leads** - Contact lists with custom fields
- **interaction_attempts** - Call history and outcomes
- **templates** - Industry-specific agent templates
- **voices** - Available voice options

### Key Features
- UUID primary keys throughout
- Soft delete with `is_deleted` flags
- JSONB fields for flexible data storage
- Comprehensive indexing for performance
- Foreign key relationships with cascading

## 🤖 Call Scheduling System

### Automated Scheduling
- Runs every minute via Google Cloud Scheduler
- Respects business hours and retry delays
- Enforces concurrent call limits per company
- Prioritizes new leads over retries

### Business Logic
1. **Eligibility Check**: `schedule_at <= now()`
2. **Business Hours**: Agent-specific time windows
3. **Retry Logic**: Configurable delays between attempts
4. **Attempt Limits**: Maximum attempts per lead
5. **Concurrent Limits**: Company-wide call restrictions

### Call Flow
```
Schedule Trigger → Eligible Leads → Business Hours Check → 
Concurrent Limit → Create Attempt → Call Retell API → 
Update Status → Process Webhook → Update Lead Status
```

## 🎯 Template System

### Industry Coverage
- Healthcare (Lead Qualification, Appointment Setting)
- Real Estate (Property Viewings, Lead Qualification)
- Insurance (Coverage Assessment)
- E-commerce (Cart Recovery)
- Education (Enrollment)
- SaaS (Demo Scheduling)

### Template Components
- **Prompt**: AI conversation instructions
- **Variables**: Dynamic placeholders (e.g., `{{company_name}}`)
- **Functions**: Available actions (end_call, transfer_call, etc.)
- **Welcome Message**: Call opening script
- **Call Flow Settings**: Industry-optimized configurations

## 🚀 Deployment

### Google Cloud Run
```bash
# Build and deploy
./deploy.sh production

# Manual deployment
docker build -t gcr.io/PROJECT_ID/voice-ai-admin-api .
docker push gcr.io/PROJECT_ID/voice-ai-admin-api
gcloud run deploy voice-ai-admin-api --image gcr.io/PROJECT_ID/voice-ai-admin-api
```

### Required Cloud Services
- **Cloud SQL**: PostgreSQL database
- **Cloud Run**: API hosting
- **Cloud Scheduler**: Automated calling
- **Secret Manager**: Credential storage
- **Container Registry**: Docker images

## 🔒 Security

### Authentication
- Google OAuth 2.0 integration
- JWT tokens with 60-day expiry
- Stateless authentication

### Data Protection
- Company-scoped data access
- Soft delete for recovery
- Encrypted credential storage
- Input validation and sanitization

### API Security
- CORS configuration
- Rate limiting (basic)
- Webhook signature verification
- SQL injection prevention via ORM

## 📊 Monitoring & Analytics

### Call Metrics
- Total calls made
- Pickup rate percentage
- Average attempts per lead
- Call duration statistics
- Agent performance tracking

### System Health
- Database connection monitoring
- Retell API integration status
- Call scheduler performance
- Error rate tracking

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Type checking
mypy app/

# Code formatting
black app/
isort app/

# Linting
flake8 app/
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Retell AI**