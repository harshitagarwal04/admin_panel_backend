# WhatsApp Integration PRD
## Voice AI Sales Agent Admin Panel - WhatsApp Messaging Extension

### Document Information
- **Version**: 1.0
- **Date**: 2025-01-24
- **Status**: Draft
- **Stakeholders**: Development Team, Product Management

---

## 1. Executive Summary

### 1.1 Project Overview
This PRD outlines the integration of WhatsApp Business API messaging capabilities into the existing Voice AI Sales Agent Admin Panel. The goal is to extend our current voice-based lead qualification and appointment setting system to include WhatsApp messaging as an additional communication channel.

### 1.2 Business Objectives
- **Multi-Channel Outreach**: Provide businesses with both voice and WhatsApp messaging options for lead engagement
- **Higher Engagement Rates**: WhatsApp typically has 90%+ open rates compared to ~20% for email
- **Global Reach**: Support international markets where WhatsApp is the primary communication channel
- **Cost Efficiency**: WhatsApp messaging is more cost-effective than voice calls for certain use cases
- **Enhanced User Experience**: Allow leads to choose their preferred communication method

### 1.3 Success Metrics
- **Adoption Rate**: 60% of existing agents enable WhatsApp within 3 months
- **Engagement Improvement**: 25% increase in overall lead response rates
- **Cost Reduction**: 30% reduction in communication costs for businesses using mixed channels
- **Customer Satisfaction**: 4.5+ rating for WhatsApp interactions

---

## 2. Current State Analysis

### 2.1 Existing Voice Architecture
The current system supports:
- **Voice Agents**: AI-powered voice agents using Retell AI integration
- **Lead Management**: Comprehensive lead tracking and scheduling
- **Call Scheduling**: Automated calling with business hours and retry logic
- **Template System**: 30+ industry-specific agent templates
- **Multi-Tenancy**: Company-scoped agents and data isolation
- **Phone Providers**: Twilio and Plivo integration for phone services

### 2.2 Architecture Strengths for WhatsApp Extension
- **Proven Agent Model**: Existing agent configuration with prompts and variables
- **Lead Management System**: Robust lead tracking and attempt management
- **Scheduling Infrastructure**: Business hours, retry logic, and attempt limits
- **Template Framework**: Industry-specific configurations ready for adaptation
- **Webhook Integration**: Established patterns for external API callbacks
- **Multi-Provider Support**: Existing abstraction for communication providers

---

## 3. WhatsApp Integration Requirements

### 3.1 Functional Requirements

#### 3.1.1 WhatsApp Agent Configuration
- **Channel Selection**: Agents can be configured for Voice, WhatsApp, or both channels
- **Message Templates**: WhatsApp-specific message templates with dynamic variables
- **Business Hours**: Separate business hours for WhatsApp messaging
- **Message Limits**: Respect WhatsApp's 24-hour session and rate limits
- **Opt-in Management**: Track user consent for WhatsApp messaging

#### 3.1.2 Lead Communication Flow
- **Channel Preference**: Leads can specify preferred communication channel
- **Fallback Strategy**: Automatic fallback between channels (e.g., WhatsApp → Voice)
- **Session Management**: Track WhatsApp conversation sessions and windows
- **Message Sequencing**: Intelligent message timing and follow-up sequences

#### 3.1.3 WhatsApp Business API Integration
- **Provider Support**: Initial integration with Twilio WhatsApp API
- **Template Management**: Create, approve, and manage WhatsApp message templates
- **Interactive Messages**: Support for buttons, quick replies, and media
- **Webhook Processing**: Handle inbound messages and delivery status updates

#### 3.1.4 Campaign Management
- **Mixed Campaigns**: Campaigns supporting both voice and WhatsApp
- **A/B Testing**: Test message effectiveness across channels
- **Scheduling**: Intelligent scheduling based on channel and timezone
- **Analytics**: Comprehensive reporting across all communication channels

### 3.2 Technical Requirements

#### 3.2.1 Database Schema Extensions
- **WhatsApp Provider**: Store WhatsApp Business API credentials
- **Message Templates**: WhatsApp-specific templates with approval status
- **Channel Preferences**: Lead-level channel preferences
- **Session Tracking**: WhatsApp conversation session management
- **Message History**: Store sent/received WhatsApp messages

#### 3.2.2 API Extensions
- **WhatsApp Endpoints**: Create, manage, and send WhatsApp messages
- **Template Endpoints**: Manage WhatsApp message templates
- **Channel Analytics**: Reporting endpoints for WhatsApp metrics
- **Webhook Endpoints**: Handle WhatsApp API callbacks

#### 3.2.3 Service Layer
- **WhatsApp Service**: Core service for WhatsApp API operations
- **Message Scheduler**: Extended scheduler supporting multiple channels
- **Template Engine**: Enhanced template processing for WhatsApp
- **Channel Router**: Intelligent routing between voice and WhatsApp

### 3.3 Business Logic Requirements

#### 3.3.1 WhatsApp Compliance
- **Opt-in Requirements**: Explicit user consent for WhatsApp messaging
- **24-Hour Rule**: Free messaging within 24-hour sessions
- **Template Approval**: WhatsApp template approval workflow
- **Rate Limiting**: Respect WhatsApp API rate limits

#### 3.3.2 Intelligent Channel Selection
- **Lead Preferences**: Honor lead's preferred communication channel
- **Fallback Logic**: Automatic fallback when primary channel fails
- **Optimal Timing**: Send messages at optimal times per channel
- **Cost Optimization**: Choose most cost-effective channel when appropriate

---

## 4. User Experience Design

### 4.1 Admin Panel Updates

#### 4.1.1 Agent Configuration
- **Channel Toggle**: Enable/disable WhatsApp for each agent
- **WhatsApp Settings**: Configure WhatsApp-specific parameters
- **Message Preview**: Preview WhatsApp messages with dynamic variables
- **Template Library**: Browse and select WhatsApp message templates

#### 4.1.2 Lead Management
- **Channel Indicators**: Visual indicators for communication channels
- **Conversation History**: Unified view of voice calls and WhatsApp messages
- **Channel Preferences**: Set and update lead communication preferences
- **Bulk Operations**: Bulk channel updates and message sending

#### 4.1.3 Campaign Dashboard
- **Multi-Channel Metrics**: Combined reporting for voice and WhatsApp
- **Channel Performance**: Compare effectiveness across channels
- **Cost Analysis**: Track costs per channel and per lead
- **Engagement Funnel**: Visualize lead journey across channels

### 4.2 End-User Experience (Leads)

#### 4.2.1 WhatsApp Interactions
- **Professional Messaging**: Business-appropriate WhatsApp messages
- **Interactive Elements**: Quick reply buttons and call-to-action buttons
- **Media Support**: Images, documents, and location sharing
- **Conversation Flow**: Natural conversation flow with AI responses

#### 4.2.2 Opt-in Experience
- **Clear Consent**: Transparent opt-in process for WhatsApp messaging
- **Preference Management**: Easy way to change communication preferences
- **Opt-out Mechanism**: Simple opt-out process with immediate effect

---

## 5. Technical Architecture

### 5.1 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Retell AI     │
│   (React)       │◄──►│   Backend       │◄──►│   Voice API     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  PostgreSQL     │    │  WhatsApp API   │
                       │  Database       │    │  (Twilio)       │
                       └─────────────────┘    └─────────────────┘
```

### 5.2 Database Schema Updates

#### 5.2.1 New Tables
```sql
-- WhatsApp Provider Configuration
CREATE TABLE whatsapp_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    provider_name VARCHAR(50) NOT NULL, -- 'twilio', 'meta', etc.
    phone_number_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    webhook_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(company_id, provider_name)
);

-- WhatsApp Message Templates
CREATE TABLE whatsapp_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    category VARCHAR(50) NOT NULL, -- 'marketing', 'utility', 'authentication'
    template_body TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    buttons JSONB DEFAULT '[]',
    approval_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    whatsapp_template_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(company_id, name, language)
);

-- WhatsApp Sessions
CREATE TABLE whatsapp_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id),
    phone_number VARCHAR(20) NOT NULL,
    session_start TIMESTAMP NOT NULL,
    session_end TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- WhatsApp Messages
CREATE TABLE whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES whatsapp_sessions(id),
    message_id VARCHAR(255) NOT NULL, -- WhatsApp message ID
    direction VARCHAR(10) NOT NULL, -- 'inbound', 'outbound'
    message_type VARCHAR(20) NOT NULL, -- 'text', 'template', 'image', etc.
    content TEXT,
    template_id UUID REFERENCES whatsapp_templates(id),
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'delivered', 'read', 'failed'
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.2.2 Extended Tables
```sql
-- Extend agents table
ALTER TABLE agents ADD COLUMN whatsapp_enabled BOOLEAN DEFAULT false;
ALTER TABLE agents ADD COLUMN whatsapp_template_id UUID REFERENCES whatsapp_templates(id);
ALTER TABLE agents ADD COLUMN whatsapp_business_hours_start TIME;
ALTER TABLE agents ADD COLUMN whatsapp_business_hours_end TIME;

-- Extend leads table
ALTER TABLE leads ADD COLUMN preferred_channel VARCHAR(20) DEFAULT 'voice'; -- 'voice', 'whatsapp', 'both'
ALTER TABLE leads ADD COLUMN whatsapp_opt_in BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN whatsapp_opt_in_date TIMESTAMP;

-- Extend interaction_attempts table
ALTER TABLE interaction_attempts ADD COLUMN channel VARCHAR(20) DEFAULT 'voice'; -- 'voice', 'whatsapp'
ALTER TABLE interaction_attempts ADD COLUMN whatsapp_session_id UUID REFERENCES whatsapp_sessions(id);
```

### 5.3 Service Layer Architecture

#### 5.3.1 WhatsApp Service
```python
class WhatsAppService:
    def __init__(self, provider_config: WhatsAppProvider):
        self.provider = provider_config
        self.client = self._initialize_client()
    
    async def send_template_message(self, phone: str, template: WhatsAppTemplate, variables: dict)
    async def send_text_message(self, phone: str, message: str)
    async def create_session(self, lead_id: UUID, phone: str)
    async def handle_webhook(self, webhook_data: dict)
    async def get_message_status(self, message_id: str)
```

#### 5.3.2 Extended Call Scheduler
```python
class MultiChannelScheduler:
    async def schedule_whatsapp_messages(self, agent_id: UUID)
    async def schedule_voice_calls(self, agent_id: UUID)
    async def determine_optimal_channel(self, lead: Lead, agent: Agent)
    async def execute_fallback_strategy(self, lead: Lead, failed_channel: str)
```

---

## 6. Implementation Plan

### 6.1 Phase 1: Foundation (Weeks 1-3)
- **Database Schema**: Implement WhatsApp-specific tables
- **Basic Models**: Create WhatsApp models and schemas
- **Twilio Integration**: Basic WhatsApp API integration
- **Template Management**: Simple template CRUD operations

### 6.2 Phase 2: Core Features (Weeks 4-6)
- **WhatsApp Service**: Complete service layer implementation
- **Message Sending**: Template and text message sending
- **Webhook Processing**: Handle inbound messages and status updates
- **Session Management**: WhatsApp conversation session tracking

### 6.3 Phase 3: Scheduler Integration (Weeks 7-9)
- **Multi-Channel Scheduler**: Extend scheduler for WhatsApp
- **Channel Routing**: Intelligent channel selection logic
- **Business Hours**: WhatsApp-specific business hours
- **Rate Limiting**: Implement WhatsApp API rate limiting

### 6.4 Phase 4: Admin Panel (Weeks 10-12)
- **Agent Configuration**: WhatsApp settings in agent creation/editing
- **Template Management**: UI for creating and managing templates
- **Channel Analytics**: Reporting for WhatsApp metrics
- **Lead Management**: Channel preferences and history

### 6.5 Phase 5: Advanced Features (Weeks 13-16)
- **Interactive Messages**: Buttons and quick replies
- **Media Support**: Images and documents
- **A/B Testing**: Campaign optimization features
- **Advanced Analytics**: Comprehensive reporting

---

## 7. Risk Assessment

### 7.1 Technical Risks
- **WhatsApp API Changes**: WhatsApp frequently updates policies and features
- **Rate Limiting**: WhatsApp has strict rate limits that could impact scaling
- **Template Approval**: WhatsApp template approval process can be slow
- **Webhook Reliability**: Ensuring reliable webhook processing

### 7.2 Business Risks
- **Compliance Issues**: WhatsApp has strict opt-in and spam policies
- **Cost Escalation**: WhatsApp messaging costs can increase with volume
- **User Adoption**: Businesses may be hesitant to adopt new communication channels
- **Support Complexity**: Increased support burden for multi-channel issues

### 7.3 Mitigation Strategies
- **Comprehensive Testing**: Extensive testing of WhatsApp integration
- **Gradual Rollout**: Phased rollout to manage risk
- **Documentation**: Clear documentation for WhatsApp policies
- **Monitoring**: Robust monitoring for WhatsApp API health

---

## 8. Success Criteria

### 8.1 Technical Success
- **API Reliability**: 99.9% uptime for WhatsApp messaging
- **Message Delivery**: 95%+ message delivery rate
- **Response Time**: <2 seconds for message sending
- **Webhook Processing**: <1 second webhook response time

### 8.2 Business Success
- **Feature Adoption**: 60% of agents enable WhatsApp within 3 months
- **Engagement Improvement**: 25% increase in lead response rates
- **Cost Efficiency**: 30% reduction in communication costs
- **Customer Satisfaction**: 4.5+ rating for WhatsApp interactions

### 8.3 User Experience Success
- **Ease of Use**: Agents can configure WhatsApp in <5 minutes
- **Unified Experience**: Seamless experience across voice and WhatsApp
- **Clear Analytics**: Comprehensive reporting across all channels
- **Reliable Delivery**: Consistent message delivery and status updates

---

## 9. Future Enhancements

### 9.1 Advanced WhatsApp Features
- **WhatsApp Flows**: Interactive form-based conversations
- **Catalog Integration**: Product catalog messaging
- **Location Sharing**: Business location and lead location sharing
- **Group Messaging**: WhatsApp group management for campaigns

### 9.2 AI Integration
- **Intelligent Routing**: AI-powered channel selection
- **Sentiment Analysis**: WhatsApp message sentiment tracking
- **Automated Responses**: AI-generated WhatsApp responses
- **Conversation Summarization**: Automatic conversation summaries

### 9.3 Additional Channels
- **SMS Integration**: Extend to SMS messaging
- **Email Integration**: Unified multi-channel approach
- **Social Media**: Instagram and Facebook Messenger integration
- **Live Chat**: Website chat widget integration

---

## 10. Conclusion

The WhatsApp integration represents a significant enhancement to our Voice AI Sales Agent platform, providing businesses with a comprehensive multi-channel communication solution. By leveraging our existing architecture and proven patterns, we can deliver a robust WhatsApp integration that maintains the quality and reliability of our voice-based system while opening new opportunities for customer engagement and business growth.

The phased implementation approach ensures manageable risk while delivering value incrementally. Success will be measured through adoption rates, engagement improvements, and overall customer satisfaction across both voice and WhatsApp channels.