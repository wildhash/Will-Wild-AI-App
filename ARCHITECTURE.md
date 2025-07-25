# Crisis Support & Mental Health Agent - Architecture Overview

## High-Level System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   FastAPI App   │───▶│  Safety Service │
│   (Chat/Web)    │    │   (src/main.py) │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Therapy Agent   │    │ Crisis Detector │
                       │    (Core AI)    │    │                 │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Gemini Service  │    │ Resource Matcher│
                       │   (AI Engine)   │    │                 │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Memory Service  │    │  Mood Analyzer  │
                       │                 │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. **API Layer** (`src/main.py`)
- **FastAPI Application**: RESTful API with structured endpoints
- **Request/Response Models**: Pydantic models for data validation
- **CORS & Middleware**: Security and cross-origin support
- **Health Checks**: Service status monitoring

### 2. **Agent Core** (`src/agents/`)
- **Therapy Agent**: Main therapeutic conversation orchestrator
  - Integrates all services for comprehensive support
  - Applies CBT techniques and safety protocols
  - Manages conversation flow and context
- **Crisis Detector**: Specialized pattern-based crisis identification
- **Resource Matcher**: Location-based resource recommendation
- **Mood Analyzer**: Emotional state assessment and tracking

### 3. **Services Layer** (`src/services/`)
- **Gemini Service**: Google Gemini API integration
  - Therapeutic response generation
  - Sentiment analysis capabilities
  - CBT exercise generation
- **Safety Service**: Crisis detection and assessment
  - Multi-level safety protocols
  - Escalation management
- **Memory Service**: Conversation context and persistence
  - Session management
  - Privacy-compliant storage

### 4. **Utilities Layer** (`src/utils/`)
- **Safety Protocols**: Crisis response procedures
- **Privacy Handler**: PII detection and data protection
- **Conversation Logger**: Secure audit logging

### 5. **Data Layer** (`src/data/`)
- **Crisis Patterns**: Keyword and pattern definitions
- **CBT Techniques**: Evidence-based therapeutic interventions
- **Safety Resources**: Crisis hotlines and support services
- **Therapy Providers**: Mental health professional directory

### 6. **Configuration Management** (`config.py`)
- Environment variable management
- API key configuration
- Application settings
- Privacy and retention policies

## Data Flow Architecture

```
User Message
     │
     ▼
┌─────────────────┐
│ Safety Check    │──── Crisis Detected? ───▶ Emergency Response
│ (Priority #1)   │                           │
└─────────────────┘                           ▼
     │                                   ┌─────────────────┐
     ▼                                   │ Crisis Protocol │
┌─────────────────┐                     │ Resource Sharing│
│ Mood Analysis   │                     │ Escalation      │
│                 │                     └─────────────────┘
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Context Retrieval│
│ (Memory Service)│
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Gemini Response │
│ Generation      │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ CBT Enhancement │
│ Resource Matching│
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Response + Logs │
│ + Memory Store  │
└─────────────────┘
```

## Safety-First Design Principles

1. **Layered Safety Checks**: Multiple validation points throughout the pipeline
2. **Crisis Prioritization**: Crisis detection takes precedence over conversational flow
3. **Privacy by Design**: Data protection integrated at every level
4. **Audit Trail**: Complete logging for compliance and safety review
5. **Fail-Safe Defaults**: System defaults to safety resources when uncertain

## Technology Stack

- **Backend Framework**: FastAPI with Python 3.11+
- **AI/ML**: Google Gemini API for conversational AI
- **Data Storage**: JSON files (MVP), extensible to databases
- **Logging**: Python logging with structured JSON output
- **Security**: Pydantic validation, privacy handlers, data anonymization
- **Configuration**: Environment-based configuration management

## Scalability Considerations

- **Modular Design**: Each component can be scaled independently
- **Service Interfaces**: Clear contracts between components
- **Data Abstraction**: Storage layer can be replaced (JSON → Database)
- **API-First**: RESTful design enables frontend flexibility
- **Configuration-Driven**: Environment-based deployment options
