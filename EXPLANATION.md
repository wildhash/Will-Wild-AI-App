# Crisis Support & Mental Health Agent - Technical Explanation

## 1. Agent Workflow

The Crisis Support & Mental Health Agent follows a safety-first workflow designed to prioritize user well-being at every step:

### Core Processing Flow:
1. **Receive User Input**: Accept chat messages through FastAPI endpoints
2. **Immediate Safety Assessment**: Priority screening for crisis indicators
3. **Crisis Response Protocol**: If crisis detected, activate emergency procedures
4. **Context Retrieval**: Load conversation history and session context
5. **Mood Analysis**: Analyze emotional state and sentiment
6. **Therapeutic Response Generation**: Use Google Gemini for empathetic responses
7. **CBT Enhancement**: Apply relevant cognitive behavioral therapy techniques
8. **Resource Matching**: Recommend appropriate mental health resources
9. **Memory Storage**: Store interaction with privacy protection
10. **Audit Logging**: Record for compliance and safety review

### Crisis Detection Priority:
```python
# Crisis detection takes absolute priority
safety_assessment = safety_service.assess_message(user_message)
if safety_assessment["crisis_detected"]:
    return crisis_response_protocol(assessment)
```

## 2. Key Modules

### **Therapy Agent** (`src/agents/therapy_agent.py`)
- **Purpose**: Central orchestrator for therapeutic conversations
- **Key Functions**:
  - `generate_response()`: Main response generation with safety integration
  - `handle_crisis_response()`: Specialized crisis intervention
  - `apply_cbt_techniques()`: Therapeutic enhancement of responses
- **Integration Points**: Connects all services for comprehensive support

### **Crisis Detector** (`src/agents/crisis_detector.py`)
- **Purpose**: Specialized pattern-based crisis identification
- **Key Functions**:
  - `detect_crisis_patterns()`: Multi-pattern crisis analysis
  - `apply_context_modifiers()`: Context-aware confidence adjustment
- **Safety Features**: False positive filtering, severity scoring

### **Gemini Service** (`src/services/gemini_service.py`)
- **Purpose**: Google Gemini API integration for AI responses
- **Key Functions**:
  - `generate_therapeutic_response()`: Specialized therapeutic prompts
  - `analyze_sentiment()`: Emotional content analysis
  - `generate_cbt_exercise()`: Personalized therapy exercises
- **Safety Integration**: Therapeutic boundary validation

### **Safety Service** (`src/services/safety_service.py`)
- **Purpose**: Comprehensive safety assessment and crisis management
- **Key Functions**:
  - `assess_message()`: Multi-factor safety evaluation
  - `get_crisis_patterns()`: Dynamic pattern management
- **Escalation**: Automatic crisis response triggering

### **Memory Service** (`src/services/memory_service.py`)
- **Purpose**: Privacy-compliant conversation context management
- **Key Functions**:
  - `store_interaction()`: Secure conversation storage
  - `get_session_context()`: Context-aware history retrieval
- **Privacy**: Automatic anonymization and data retention

## 3. Tool Integration

### **Google Gemini API Integration**
```python
# Therapeutic prompt engineering
prompt = build_therapeutic_prompt(message, context)
response = gemini_service.generate_therapeutic_response(prompt)
```

### **Crisis Pattern Matching**
```python
# Multi-layer pattern detection
crisis_patterns = load_crisis_patterns("src/data/crisis_patterns.json")
matches = detect_patterns(message, patterns)
```

### **Resource Matching Engine**
```python
# Location-based resource finding
resources = resource_matcher.find_relevant_resources(
    message, emotion, user_location
)
```

### **CBT Technique Application**
```python
# Evidence-based therapeutic techniques
techniques = load_cbt_techniques("src/data/cbt_techniques.json")
enhanced_response = apply_techniques(response, user_mood)
```

## 4. Observability & Testing

### **Comprehensive Logging System**
- **Conversation Logs**: Privacy-compliant interaction recording
- **Crisis Incident Logs**: High-priority safety event tracking
- **Audit Trails**: Compliance and review logging
- **Privacy Events**: Data protection operation logging

```python
# Structured logging example
conversation_logger.log_crisis_incident(
    session_id=session_id,
    crisis_type="suicide_risk",
    severity="critical",
    response_actions=["988_lifeline", "emergency_services"]
)
```

### **Safety Protocol Testing**
- **Pattern Testing**: Crisis detection accuracy validation
- **Response Testing**: Therapeutic boundary compliance
- **Resource Testing**: Availability and accuracy verification

### **Privacy Compliance Monitoring**
- **PII Detection**: Automatic personally identifiable information scanning
- **Data Retention**: Automated compliance with retention policies
- **Anonymization**: Privacy-preserving data handling

## 5. Known Limitations

### **Current Technical Limitations**
- **In-Memory Storage**: Session data not persisted between restarts
- **Pattern-Based Detection**: Limited to keyword/regex crisis detection
- **Single Language**: Currently English-only support
- **API Dependencies**: Requires Google Gemini API availability

### **Clinical Limitations**
- **Not a Replacement**: Cannot replace professional therapy or medical care
- **Crisis Scope**: Limited to text-based crisis assessment
- **Diagnostic Restrictions**: Cannot provide medical diagnoses
- **Medication Limitations**: Cannot advise on psychiatric medications

### **Scalability Considerations**
- **Memory Growth**: Conversation storage grows linearly with usage
- **API Rate Limits**: Bounded by Gemini API quotas
- **Processing Latency**: Sequential safety checks add response time
- **Resource Updates**: Manual updates required for resource databases

### **Privacy and Security Notes**
- **Data Sensitivity**: Handles highly sensitive mental health information
- **Encryption**: TODO - implement end-to-end encryption for storage
- **Audit Requirements**: Mental health data requires extensive audit trails
- **Compliance**: Must comply with HIPAA-like privacy regulations

## 6. Safety Architecture

### **Multi-Layer Safety System**
1. **Input Validation**: Immediate message safety screening
2. **Pattern Matching**: Keyword and context-based crisis detection
3. **Confidence Scoring**: Multi-factor risk assessment
4. **Protocol Activation**: Automated crisis response procedures
5. **Human Escalation**: Integration points for human counselors

### **Crisis Response Priorities**
1. **Immediate Danger**: 911/Emergency services
2. **Suicide Risk**: 988 Lifeline priority contact
3. **Self-Harm**: Safety planning and resource provision
4. **Substance Crisis**: Specialized addiction resources
5. **General Support**: Mental health professional referrals

### **Privacy-by-Design Implementation**
- **Data Minimization**: Only store necessary conversation data
- **Purpose Limitation**: Data used only for therapeutic support
- **Storage Limitation**: Automatic data retention policy enforcement
- **Security**: Privacy handler with PII detection and redaction
- **Transparency**: Clear logging of all data processing operations  

