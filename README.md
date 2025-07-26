# Crisis Support AI Agent - Will Wild AI App

Welcome! This is an AI-powered crisis support system with advanced mood tracking and analytics capabilities, developed for the **Agentic AI App Hackathon**.

## 🌟 Key Features

### Crisis Support & Safety
- **Real-time Crisis Detection**: Advanced keyword-based risk assessment (low, medium, high, critical)
- **Automated Crisis Response**: Immediate escalation protocols with hotline resources
- **Safety Monitoring**: Continuous risk tracking with crisis event logging

### Mood Tracking & Analytics
- **Advanced Mood Detection**: Rule-based sentiment analysis with 10+ mood categories
- **Negation Handling**: Intelligent parsing of "not happy" → negative mood
- **Confidence Scoring**: Accuracy ratings for mood detection (0.0-1.0)
- **Trend Analysis**: Mood progression tracking (improving, declining, stable)
- **Privacy-First Design**: Anonymized session IDs and data minimization

### Session Management
- **Memory Limits**: Max 100 mood entries per session to prevent bloat
- **Automatic Cleanup**: Periodic removal of expired sessions (24h default)
- **Privacy Protection**: Hashed user identifiers, no raw message storage in logs

### User Experience
- **Mood Feedback**: "Did we get your mood right?" confirmation system
- **Analytics Dashboard**: Personal mood trends and distribution via API
- **Enhanced Responses**: Mood-aware AI responses with validation prompts

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Will-Wild-AI-App

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the API server
cd src
python main.py

# Server will run on http://localhost:8000
# API documentation available at http://localhost:8000/docs
```

### Testing

```bash
# Test basic functionality
python test_api.py

# Test enhanced mood tracking
python test_mood_api.py
```

## 📋 API Endpoints

### Core Chat
- `POST /api/chat` - Main conversation endpoint with mood tracking
- `GET /api/health` - System health check with service status
- `GET /api/conversation/{user_id}/summary` - Session summary with mood analytics

### Mood Tracking
- `GET /api/mood/{user_id}/analytics` - Mood trends and distribution
- `GET /api/mood/{user_id}/history` - Recent mood history (privacy-safe)
- `POST /api/mood/{user_id}/feedback` - Submit mood detection feedback

### Administration
- `POST /api/admin/cleanup` - Manual session cleanup
- `POST /api/conversation/{user_id}/end` - End conversation session

## 🔒 Privacy & Data Handling

### Current Approach
- **Session Anonymization**: User IDs hashed using SHA-256 (first 16 chars)
- **Data Minimization**: Raw messages not stored in mood logs
- **Memory Limits**: Automatic cleanup prevents indefinite data retention
- **Privacy-Safe Logging**: No personally identifiable information in logs

### Session Management
- **Conversation Limit**: Maximum 1000 active conversations
- **Message Limit**: Maximum 100 messages per conversation
- **Mood Limit**: Maximum 100 mood entries per session
- **Auto-Cleanup**: Sessions expire after 24 hours of inactivity

### Future Privacy Enhancements (TODOs)
- End-to-end encryption for message storage
- User-controlled data retention periods
- GDPR-compliant data deletion workflows
- Advanced anonymization techniques
- Audit logging for data access

## 🧠 Mood Detection Logic

### Supported Mood Categories
- **Positive**: happy, joyful, excited, great, amazing, wonderful
- **Negative**: sad, upset, angry, frustrated, disappointed, terrible
- **Anxious**: anxious, worried, nervous, stressed, panic, overwhelmed
- **Depressed**: depressed, hopeless, empty, numb, worthless, lonely
- **Excited**: excited, thrilled, pumped, energetic, enthusiastic
- **Calm**: calm, peaceful, relaxed, serene, tranquil, composed
- **Frustrated**: frustrated, annoyed, irritated, aggravated, fed up
- **Hopeful**: hopeful, optimistic, confident, encouraged, motivated

### Detection Features
- **Keyword Matching**: Confidence-weighted mood detection
- **Negation Handling**: "not happy" correctly identified as negative
- **Mixed Emotions**: Multiple moods detected as "mixed" category
- **Ambiguous Input**: Defaults to "neutral" when uncertain
- **Context Awareness**: AI responses adapt to detected mood

### Limitations
- Rule-based system (not ML-powered)
- English language only
- Limited context understanding
- No emotion intensity scaling
- Basic negation patterns only

## 🛠 Architecture

### Core Services
- **TherapyAgent**: Main orchestration layer
- **MoodService**: Advanced mood detection and analytics
- **SafetyService**: Crisis detection and escalation
- **MemoryService**: Session management with privacy controls
- **GeminiService**: AI response generation (mock mode for demo)

### Technology Stack
- **Backend**: FastAPI with async support
- **AI Integration**: Google Gemini API (configured for mock responses)
- **Storage**: In-memory (Redis/PostgreSQL planned for production)
- **Privacy**: SHA-256 hashing, data minimization principles

## 📊 Demo Instructions

### Basic Conversation Flow
1. Start with a greeting: "Hello, I'm having a tough day"
2. Express different moods: "I feel anxious about tomorrow"
3. Test negation: "I'm not happy about this situation"
4. Check analytics: GET `/api/mood/{user_id}/analytics`

### Crisis Detection Demo
1. Medium risk: "I feel overwhelmed and can't cope"
2. High risk: "I feel hopeless and don't know what to do"
3. Critical risk: "I want to hurt myself, I can't take this anymore"

### Mood Tracking Demo
1. Multiple emotions: "I'm excited but also nervous about my presentation"
2. Trend analysis: Send 5+ messages with different moods
3. Feedback system: Use mood feedback endpoint to correct detection

## 🔄 Session Cleanup & Memory Management

### Automatic Cleanup
- Runs on every chat request (background task)
- Removes sessions older than 24 hours
- Trims conversations exceeding message limits
- Cleans up orphaned mood tracking data

### Manual Cleanup
```bash
curl -X POST http://localhost:8000/api/admin/cleanup
```

## 🏅 Hackathon Requirements

### Technical Excellence
- ✅ Robust error handling and graceful degradation
- ✅ Comprehensive logging and monitoring
- ✅ Memory management and cleanup procedures
- ✅ Privacy-by-design implementation

### Solution Architecture
- ✅ Clean, modular service-oriented design
- ✅ Comprehensive API documentation
- ✅ Privacy and security considerations
- ✅ Scalable session management

### Innovative Integration
- ✅ Google Gemini API integration (mock mode)
- ✅ Advanced mood-aware AI responses
- ✅ Context-sensitive crisis intervention
- ✅ Real-time mood analytics

### Societal Impact
- ✅ Mental health crisis support system
- ✅ Privacy-focused approach to sensitive data
- ✅ Accessible API design for integration
- ✅ Comprehensive safety protocols

## 📝 Development Notes

### Known Issues
- Negation detection needs refinement for complex sentences
- Mood confidence scoring could be more sophisticated  
- Limited to English language mood keywords
- Mock AI responses for demo (real Gemini integration requires API key)

### Future Improvements
- Machine learning-based mood detection
- Multi-language support
- Voice/audio mood analysis integration
- Real-time crisis team notifications
- Advanced therapy conversation patterns

## 📚 Additional Documentation

- **ARCHITECTURE.md**: Detailed system architecture and design decisions
- **EXPLANATION.md**: Development process, tool usage, and technical decisions
- **DEMO.md**: Video demonstration with timestamped feature highlights
- **Crisis_Support_README.md**: Detailed crisis intervention protocols

## 🤝 Contributing

This is a hackathon project, but future contributions are welcome. Please ensure:
- Privacy and security best practices
- Comprehensive testing of new features
- Documentation updates for any API changes
- Consideration of mental health sensitivity

---

**⚠️ Important**: This is a demo system for educational/hackathon purposes. For real mental health crises, always contact professional services: 988 (Suicide & Crisis Lifeline) or 911.