# Crisis Support AI Agent

A FastAPI-based crisis support system with AI-powered conversation analysis, safety monitoring, and therapeutic assistance.

## Features

- **Crisis Detection**: Automated risk assessment based on conversation content
- **Safety Monitoring**: Real-time logging and escalation protocols
- **Therapeutic Support**: AI-powered responses with appropriate crisis resources
- **Memory Management**: Conversation history and context tracking
- **REST API**: Easy integration with frontend applications

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
cd src
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Chat
- `POST /api/chat` - Send a message and receive AI response
  ```json
  {
    "user_id": "string",
    "message": "string"
  }
  ```

### Health Check
- `GET /api/health` - Check service status

### Conversation Management
- `GET /api/conversation/{user_id}/summary` - Get conversation summary
- `POST /api/conversation/{user_id}/end` - End conversation session

### Documentation
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## Testing

Run the test script to verify all functionality:
```bash
# Start the server first
cd src && python main.py

# In another terminal
python test_api.py
```

## Risk Levels

The system automatically detects and responds to different risk levels:

- **Low**: Normal conversation
- **Medium**: Signs of distress (anxiety, depression)
- **High**: Concerning language (hopelessness, despair)
- **Critical**: Immediate danger (suicide ideation, self-harm)

## Crisis Resources

The system provides appropriate resources based on risk level:
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **NAMI Helpline**: 1-800-950-NAMI (6264)

## Architecture

### Components

1. **FastAPI Application** (`src/main.py`)
   - Main server with CORS support
   - Router mounting and lifecycle management

2. **Chat API** (`src/api/chat_api.py`)
   - POST /api/chat endpoint
   - Request validation and error handling
   - Integration with TherapyAgent

3. **Therapy Agent** (`src/agents/therapy_agent.py`)
   - Orchestrates conversation processing
   - Integrates memory, safety, and AI services
   - Provides conversation summaries

4. **Memory Service** (`src/services/memory_service.py`)
   - In-memory conversation storage (MVP)
   - Context management and session tracking
   - TODO: Extend for persistent storage

5. **Safety Service** (`src/services/safety_service.py`)
   - Crisis detection and risk assessment
   - Logging and escalation protocols
   - TODO: Integrate real notification systems

6. **Gemini Service** (`src/services/gemini_service.py`)
   - AI response generation
   - Currently uses mock responses
   - TODO: Implement actual Gemini API integration

7. **Data Models** (`src/models/conversation.py`)
   - Pydantic models for requests/responses
   - Conversation context and message structures

## Future Enhancements

### Memory Service
- [ ] Implement persistent storage (Redis/PostgreSQL)
- [ ] Add conversation archival
- [ ] Session timeout management

### Safety Service
- [ ] SMS/email alerts to crisis team
- [ ] Integration with emergency services
- [ ] Real-time monitoring dashboard
- [ ] Enhanced risk detection algorithms

### Gemini Integration
- [ ] Implement actual Gemini API calls
- [ ] Fine-tune prompts for therapeutic responses
- [ ] Add conversation context optimization

### Monitoring & Observability
- [ ] Structured logging with correlation IDs
- [ ] Metrics and health checks
- [ ] Error tracking integration
- [ ] Performance monitoring

## Contributing

This is an MVP implementation focused on core functionality. All services use in-memory storage and mock implementations where appropriate. Production deployment would require:

1. Database integration for persistent storage
2. Real crisis notification systems
3. Enhanced security and authentication
4. Monitoring and alerting systems
5. Load balancing and scalability considerations

## License

MIT License - see LICENSE file for details.