# Architecture Overview

## System Design

The Crisis Support & Mental Health Agent MVP follows a layered, service-oriented architecture designed for scalability, safety, and therapeutic effectiveness.

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                        │
│              (FastAPI / Web / Mobile)                   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                 TherapyAgent                            │
│            (Core Orchestrator)                          │
│  • Therapy phase management                             │
│  • Intervention selection                               │
│  • Crisis workflow coordination                         │
└─┬─────────────────┬─────────────────┬───────────────────┘
  │                 │                 │
┌─┴─────────────┐ ┌─┴─────────────┐ ┌─┴─────────────────────┐
│ GeminiService │ │ SafetyService │ │   MemoryService       │
│               │ │               │ │                       │
│ • AI Chat     │ │ • Risk Assess │ │ • Session Memory      │
│ • Risk Score  │ │ • Crisis Esc  │ │ • User Profiles       │
│ • Prompts     │ │ • Resources   │ │ • Progress Track      │
└───────────────┘ └───────────────┘ └───────────────────────┘
```

## Components

### 1. **User Interface Layer**
   - **FastAPI REST API**: Production-ready web service
   - **Interactive Demo**: Command-line interface for testing
   - **Web Integration Ready**: Designed for web/mobile app integration

### 2. **TherapyAgent (Core Orchestrator)**
   - **Centralized Logic**: Coordinates all therapeutic workflows
   - **Phase Management**: Guides users through therapy phases
   - **Intervention Engine**: Selects and applies appropriate interventions
   - **Crisis Coordination**: Manages emergency escalation procedures

### 3. **GeminiService (AI Engine)**
   - **Gemini Integration**: Google's advanced language model
   - **Mental Health Prompts**: Specialized prompting for therapeutic contexts
   - **Risk Assessment**: AI-powered analysis of user messages
   - **Session Context**: Maintains conversation continuity

### 4. **SafetyService (Crisis Management)**
   - **Multi-level Assessment**: Low → Moderate → High → Crisis
   - **Escalation Protocols**: Automated crisis intervention
   - **Resource Integration**: Crisis hotlines and emergency services
   - **Safety Planning**: Personalized safety plan development

### 5. **MemoryService (Data Layer)**
   - **Session Persistence**: Conversation history and context
   - **User Profiles**: Therapeutic goals and preferences
   - **Progress Tracking**: Intervention effectiveness metrics
   - **Analytics**: Insights for therapeutic improvement

## Data Flow

```
User Message → TherapyAgent → Risk Assessment → Safety Check
     ↓              ↓              ↓              ↓
Memory Store → AI Processing → Intervention → Response
     ↑              ↑              ↑              ↓
Session Data → Context Build → Therapy Phase → User
```

## Safety Architecture

```
┌─────────────────────────────────────────────────────┐
│                Safety Layers                        │
├─────────────────────────────────────────────────────┤
│ 1. Input Validation: Sanitize user input           │
│ 2. Risk Detection: Multiple assessment methods     │
│ 3. Crisis Escalation: Immediate resource provision │
│ 4. Professional Referral: Human oversight          │
│ 5. Audit Logging: Complete interaction history     │
└─────────────────────────────────────────────────────┘
```

## Therapeutic Workflow

```
Initial Contact → Assessment → Risk Evaluation
      ↓              ↓             ↓
Rapport Building → Intervention → Skill Practice
      ↓              ↓             ↓
Progress Review → Crisis Handle → Session Close
      ↓              ↓             ↓
Follow-up Plan → Resource Connect → Memory Store
```

## Scalability Design

### Horizontal Scaling
- **Stateless Services**: Each service can be independently scaled
- **Session Management**: Externalized to database (planned)
- **Load Balancing**: Ready for multiple instance deployment

### Performance Optimization
- **Async Processing**: Non-blocking I/O operations
- **Caching Strategy**: Planned for session and user data
- **Rate Limiting**: Prevents abuse and ensures fair usage

## Security & Compliance

### Data Protection
- **Encryption**: Data at rest and in transit (planned)
- **Access Control**: User authentication and authorization
- **Audit Trails**: Complete logging for compliance

### Privacy
- **Minimal Data**: Only necessary information stored
- **Data Retention**: Configurable retention policies
- **User Control**: Data export and deletion capabilities

## Integration Points

### External Services
- **Crisis Hotlines**: 988, Crisis Text Line integration
- **Emergency Services**: 911 coordination protocols
- **Healthcare Providers**: Professional referral system (planned)

### Monitoring & Observability
- **Health Checks**: Service availability monitoring
- **Metrics**: Performance and usage analytics
- **Logging**: Structured logging with correlation IDs
- **Alerting**: Crisis event notifications

## Deployment Architecture

```
Internet → Load Balancer → FastAPI Instances
                ↓
        Message Queue → Background Workers
                ↓
Database Cluster ← Redis Cache → Monitoring
                ↓
         External Services (Crisis, Healthcare)
```

## Technology Stack

- **Backend**: Python 3.9+, FastAPI, AsyncIO
- **AI Engine**: Google Gemini API
- **Database**: PostgreSQL (planned), Redis (caching)
- **Monitoring**: Prometheus, Grafana (planned)
- **Deployment**: Docker, Kubernetes (planned)

## Future Enhancements

### Phase 2
- **Persistent Database**: Replace in-memory storage
- **Vector Search**: Semantic memory search
- **Advanced Analytics**: ML-based insights

### Phase 3
- **Multi-language**: International support
- **Group Therapy**: Multi-user sessions
- **Professional Dashboard**: Therapist interface

### Phase 4
- **Mobile Apps**: Native iOS/Android
- **Wearable Integration**: Health monitoring
- **Research Platform**: Academic collaboration

