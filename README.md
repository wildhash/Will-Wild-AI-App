# Crisis Support & Mental Health Agent MVP

A comprehensive AI-powered mental health support system built with Google Gemini, featuring crisis detection, therapeutic interventions, and safety protocols.

## 🏗️ Architecture Overview

### Core Components

1. **TherapyAgent** (`src/agents/therapy_agent.py`)
   - Main orchestrator for therapeutic interactions
   - Integrates all services for comprehensive mental health support
   - Implements evidence-based therapeutic approaches (CBT, grounding techniques)
   - Manages therapy phases from assessment to intervention

2. **GeminiService** (`src/services/gemini_service.py`)
   - AI-powered conversation engine using Google Gemini
   - Mental health-focused prompt engineering
   - Risk assessment combining rule-based and AI analysis
   - Session management with conversation memory

3. **SafetyService** (`src/services/safety_service.py`)
   - Crisis detection and escalation protocols
   - Safety assessment with multiple risk levels
   - Crisis resource management
   - Emergency contact integration

4. **MemoryService** (`src/services/memory_service.py`)
   - Conversation history and session persistence
   - User profile management
   - Therapeutic progress tracking
   - Memory search and analytics

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Will-Wild-AI-App
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the Demo

**Interactive Demo:**
```bash
export GEMINI_API_KEY="your_api_key_here"
python demo.py --interactive
```

**Scripted Demo:**
```bash
export GEMINI_API_KEY="your_api_key_here"
python demo.py
```

**FastAPI Web Service:**
```bash
export GEMINI_API_KEY="your_api_key_here"
uvicorn fastapi_example:app --reload
```

### Running Tests

```bash
python -m pytest tests/test_core_functionality.py -v
```

## 🧠 Features

### AI-Powered Conversation
- **Gemini Integration**: Advanced AI conversation with mental health specialization
- **Context Awareness**: Maintains conversation history and user context
- **Personalized Responses**: Adapts based on user profile and therapeutic progress

### Risk Assessment & Safety
- **Multi-layered Assessment**: Combines rule-based keywords and AI analysis
- **Four Risk Levels**: Low, Moderate, High, Crisis
- **Automatic Escalation**: Immediate crisis resource provision
- **Safety Planning**: Personalized safety plan development

### Therapeutic Interventions
- **CBT Techniques**: Cognitive restructuring and behavioral activation
- **Grounding Exercises**: 5-4-3-2-1 technique, breathing exercises, body scans
- **Crisis Management**: De-escalation and immediate safety protocols
- **Progress Tracking**: Session outcomes and therapeutic improvement metrics

### Session Management
- **Persistent Memory**: Conversation history across sessions
- **User Profiles**: Therapeutic goals, coping strategies, trigger awareness
- **Session Analytics**: Progress metrics and intervention effectiveness
- **Cleanup Automation**: Automatic cleanup of expired sessions

## 📊 Risk Assessment System

### Risk Levels

| Level | Score Range | Characteristics | Response |
|-------|-------------|----------------|----------|
| **Low** | 0.0 - 0.3 | General support seeking | Supportive conversation |
| **Moderate** | 0.3 - 0.6 | Mild to moderate distress | Coping strategies, CBT |
| **High** | 0.6 - 0.8 | Significant mental health concerns | Professional referral + support |
| **Crisis** | 0.8 - 1.0 | Immediate danger indicators | Emergency resources + escalation |

### Detection Methods

1. **Rule-based Keywords**: Immediate detection of crisis language
2. **AI Analysis**: Nuanced understanding of context and intent
3. **Historical Patterns**: Trend analysis from previous interactions
4. **Combined Scoring**: Weighted combination of all assessment methods

## 🎯 Therapeutic Interventions

### CBT (Cognitive Behavioral Therapy)
- **Thought Challenging**: Evidence-based cognitive restructuring
- **Behavioral Activation**: Activity scheduling and mood improvement
- **Homework Assignments**: Practice exercises and skill development

### Grounding Techniques
- **5-4-3-2-1 Technique**: Sensory grounding for anxiety and panic
- **Box Breathing**: Regulated breathing for stress reduction
- **Body Scan**: Mindfulness-based anxiety management

### Crisis Intervention
- **De-escalation**: Calm, supportive crisis communication
- **Safety Planning**: Immediate safety protocol development
- **Resource Connection**: Crisis hotlines and emergency services

## 🔧 API Endpoints (FastAPI)

### Core Chat
- `POST /chat` - Main conversation endpoint
- `GET /session/{id}/summary` - Session analytics
- `POST /session/{id}/end` - End therapy session

### User Management
- `GET /user/{id}/profile` - User profile and progress
- `POST /user/{id}/profile` - Update user preferences

### Safety & Resources
- `GET /crisis-resources` - Emergency contact information
- `GET /health` - Service health check

## 🔒 Safety & Compliance

### Crisis Detection
- Immediate identification of suicidal ideation
- Self-harm risk assessment
- Escalation to human professionals
- Emergency service integration

### Privacy & Security
- No persistent storage of sensitive data (in current stub implementation)
- Secure session management
- Audit logging for compliance
- Data encryption ready (TODO)

### Ethical AI
- Transparent limitations acknowledgment
- Human professional referral recommendations
- Non-diagnostic approach
- Cultural sensitivity considerations

## 🧪 Testing

The project includes comprehensive tests covering:

- **SafetyService**: Crisis detection, escalation protocols
- **MemoryService**: Session persistence, user profiles
- **Configuration**: Validation and resource management
- **Integration**: Multi-service workflow testing

Run tests with:
```bash
python -m pytest tests/ -v --cov=src
```

## 📝 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional - Safety
CRISIS_HOTLINE=988
EMERGENCY_CONTACT=911
HIGH_RISK_THRESHOLD=0.6
CRISIS_THRESHOLD=0.8

# Optional - Performance
MAX_REQUESTS_PER_MINUTE=60
SESSION_TIMEOUT=30
MAX_SESSIONS_PER_USER=5

# Optional - Features
ENABLE_CRISIS_DETECTION=true
ENABLE_MEMORY_PERSISTENCE=false
LOG_LEVEL=INFO
```

## 🚧 Production Deployment TODOs

### High Priority
1. **Database Integration**: Replace in-memory storage with PostgreSQL/MongoDB
2. **Security Implementation**: Add authentication, encryption, audit logging
3. **Crisis System Integration**: Connect to professional crisis intervention services
4. **Rate Limiting**: Implement comprehensive API rate limiting
5. **Monitoring**: Add comprehensive logging and analytics

### Medium Priority
1. **Vector Search**: Implement semantic memory search with embeddings
2. **Multi-language Support**: Expand to support multiple languages
3. **Mobile API**: Optimize for mobile app integration
4. **Compliance**: HIPAA compliance and healthcare regulations
5. **Performance**: Caching, optimization, and scaling

### Low Priority
1. **Group Therapy**: Multi-user session support
2. **Wearable Integration**: Connect to health monitoring devices
3. **Professional Dashboard**: Interface for human therapists
4. **Advanced Analytics**: ML-based insights and recommendations

## 🆘 Crisis Resources

If you or someone you know is in mental health crisis:

- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: 911
- **Online Chat**: suicidepreventionlifeline.org/chat

## ⚠️ Important Disclaimers

- This is an AI assistant and **NOT a replacement for professional mental health care**
- In case of emergency, always contact emergency services (911) or crisis hotlines (988)
- The AI provides support and resources but does not diagnose or treat mental health conditions
- Always consult with qualified mental health professionals for serious concerns

## 🏅 Judging Criteria

- **Technical Excellence**: Robust, functional implementation with efficient code and core feature execution
- **Solution Architecture & Documentation**: Clear, maintainable design with comprehensive documentation
- **Innovative Gemini Integration**: Creative and effective use of Google Gemini API capabilities
- **Societal Impact & Novelty**: Addresses meaningful mental health challenges with innovative solutions

---

**Built with ❤️ for mental health awareness and crisis support**


