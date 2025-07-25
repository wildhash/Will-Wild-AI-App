# Crisis Support & Mental Health Agent

An AI-powered mental health support agent using Google Gemini API, designed with safety-first principles for crisis intervention and therapeutic conversation support.

## 🎯 Project Overview

This agent provides empathetic, evidence-based mental health support through conversational AI, incorporating cognitive-behavioral therapy (CBT) techniques, crisis detection, and comprehensive safety protocols. Built for the **Agentic AI App Hackathon**, it demonstrates innovative integration of Google Gemini API with specialized mental health support capabilities.

## 🌟 Key Features

### 🔒 **Safety-First Architecture**
- **Multi-layer crisis detection** with pattern matching and context analysis
- **Immediate intervention protocols** for suicide risk and self-harm
- **Automated resource matching** with 988 Lifeline and crisis services
- **Privacy-compliant logging** with audit trails

### 🧠 **Therapeutic AI Integration**
- **Google Gemini API** for empathetic, context-aware responses
- **Evidence-based CBT techniques** automatically applied based on mood
- **Mood analysis and tracking** across conversation sessions
- **Personalized therapeutic interventions**

### 🎛️ **Comprehensive Support System**
- **Crisis hotline integration** (988, Crisis Text Line, specialized services)
- **Mental health provider directory** with location-based matching
- **Therapy technique library** with guided exercises
- **Resource recommendation engine** for ongoing support

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Google Gemini API key
- Conda or virtual environment

### Installation

#### Option 1: Conda Environment (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd Will-Wild-AI-App

# Create conda environment
conda env create -f environment.yml
conda activate agentic-hackathon

# Set up environment variables
cp .env.example .env
# Edit .env with your Gemini API key
```

#### Option 2: Pip Installation
```bash
# Clone and set up virtual environment
git clone <repository-url>
cd Will-Wild-AI-App
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Gemini API key
```

### Configuration

Edit `.env` file with your configuration:
```bash
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Application settings
DEBUG=True
HOST=localhost
PORT=8000

# Privacy and safety settings
ANONYMIZE_LOGS=True
DATA_RETENTION_DAYS=30
```

### Running the Application

```bash
# Start the server
python src/main.py

# Or using uvicorn directly
uvicorn src.main:app --host localhost --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## 🔧 API Usage

### Health Check
```bash
curl http://localhost:8000/
```

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am feeling very anxious about my job interview tomorrow",
    "session_id": "optional_session_id"
  }'
```

### Resource Search
```bash
curl -X POST http://localhost:8000/resources/search \
  -H "Content-Type: application/json" \
  -d '{
    "location": "New York, NY",
    "resource_type": "crisis"
  }'
```

## 📂 Project Structure

```
src/
├── main.py                     # FastAPI application entry point
├── agents/
│   ├── therapy_agent.py        # Main therapeutic conversation orchestrator
│   ├── crisis_detector.py      # Pattern-based crisis detection
│   ├── resource_matcher.py     # Location-based resource matching
│   └── mood_analyzer.py        # Mood and sentiment analysis
├── services/
│   ├── gemini_service.py       # Google Gemini API integration
│   ├── safety_service.py       # Safety assessment and protocols
│   └── memory_service.py       # Conversation context management
├── utils/
│   ├── safety_protocols.py     # Crisis response procedures
│   ├── privacy_handler.py      # PII detection and data protection
│   └── conversation_logger.py  # Secure audit logging
└── data/
    ├── crisis_patterns.json    # Crisis detection patterns
    ├── cbt_techniques.json     # CBT therapy techniques
    ├── safety_resources.json   # Crisis support resources
    └── therapy_providers.json  # Mental health providers

config.py                       # Central configuration management
environment.yml                 # Conda environment specification
requirements.txt                # Python dependencies
.env.example                    # Environment configuration template
```

## 🎨 Example Interactions

### Crisis Support Example
```json
{
  "user_message": "I don't want to live anymore",
  "agent_response": "I'm very concerned about what you've shared. Your safety is the most important thing right now. Please reach out to the 988 Suicide & Crisis Lifeline at 988 or text 'HELLO' to 741741 for immediate support.",
  "safety_level": "critical",
  "resources": [
    {
      "name": "988 Suicide & Crisis Lifeline",
      "phone": "988",
      "availability": "24/7"
    }
  ],
  "escalation_triggered": true
}
```

### Therapeutic Support Example
```json
{
  "user_message": "I'm feeling really anxious about my presentation tomorrow",
  "agent_response": "I can hear that you're feeling anxious about your presentation. That's a very common feeling, and it shows that this presentation matters to you. Let's try a grounding technique together - can you tell me 5 things you can see around you right now?",
  "mood_analysis": {
    "primary_emotion": "anxious",
    "intensity": 6,
    "confidence": 0.85
  },
  "cbt_techniques": ["grounding_5_4_3_2_1"]
}
```

## 🛡️ Safety Features

### Crisis Detection
- **Keyword Pattern Matching**: Advanced regex patterns for crisis indicators
- **Context Analysis**: Considers surrounding text and conversation history
- **Severity Scoring**: Multi-level risk assessment (safe → critical)
- **False Positive Filtering**: Reduces incorrect crisis detections

### Emergency Response
- **Immediate Resources**: 988 Lifeline, Crisis Text Line, Emergency Services
- **Specialized Support**: LGBTQ+ youth, veterans, domestic violence
- **Automated Escalation**: Configurable crisis response protocols
- **Audit Logging**: Complete documentation of crisis interventions

## 🔐 Privacy & Compliance

### Data Protection
- **PII Detection**: Automatic identification and redaction of personal information
- **Data Anonymization**: Configurable privacy levels for data storage
- **Retention Policies**: Automated data lifecycle management
- **Audit Trails**: Complete logging for compliance requirements

### Security Features
- **Privacy by Design**: Data protection integrated at every level
- **Configurable Anonymization**: Balance between utility and privacy
- **Secure Logging**: Encrypted storage options for sensitive data
- **Compliance Reporting**: HIPAA-ready privacy controls

## 🧪 Testing & Development

### Running Tests
```bash
# Install development dependencies
pip install pytest pytest-asyncio

# Run tests (when implemented)
pytest tests/

# Test crisis detection patterns
python -m src.agents.crisis_detector --test

# Test safety protocols
python -m src.utils.safety_protocols --test
```

### Development Setup
```bash
# Enable debug mode
export DEBUG=True

# Use development configuration
cp .env.example .env.dev

# Run with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Deployment

### Environment Variables for Production
```bash
DEBUG=False
HOST=0.0.0.0
PORT=8000
GEMINI_API_KEY=your_production_api_key
ANONYMIZE_LOGS=True
LOG_LEVEL=INFO
```

### Docker Deployment (Future Enhancement)
```dockerfile
# Dockerfile template for future use
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

### For Hackathon Team Members
1. **Review Architecture**: Read `ARCHITECTURE.md` for system overview
2. **Check TODOs**: Look for `TODO` comments throughout the codebase
3. **Safety First**: Always prioritize user safety in any modifications
4. **Test Changes**: Validate safety protocols with any updates

### Key Areas for Enhancement
- **Gemini Prompt Engineering**: Improve therapeutic response quality
- **Crisis Detection**: Enhance pattern matching with ML approaches
- **Resource Integration**: Connect with real-time provider APIs
- **Privacy Enhancement**: Implement end-to-end encryption
- **Multi-language Support**: Expand beyond English

## 📋 Submission Checklist

- [x] All code in `src/` runs without errors
- [x] `ARCHITECTURE.md` contains clear diagram and explanation
- [x] `EXPLANATION.md` covers planning, tool use, memory, and limitations
- [x] Comprehensive safety protocols implemented
- [x] Google Gemini API integration functional
- [x] Crisis detection and resource matching operational
- [x] Privacy-compliant data handling
- [ ] `DEMO.md` links to demonstration video (pending)

## ⚠️ Important Disclaimers

- **Not a Replacement for Professional Care**: This agent is designed to provide support and resources, not replace professional mental health treatment
- **Crisis Limitations**: While comprehensive, the system cannot guarantee detection of all crisis situations
- **Data Sensitivity**: Handles sensitive mental health information - review privacy settings carefully
- **API Dependencies**: Requires active Google Gemini API key and internet connectivity

## 📞 Crisis Resources

If you or someone you know is in crisis:
- **988 Suicide & Crisis Lifeline**: Call or text 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: Call 911 for immediate danger

## 📄 License

This project is developed for educational and humanitarian purposes. See LICENSE file for details.

---

*Built with ❤️ for the Agentic AI App Hackathon - Demonstrating the power of AI for social good*


