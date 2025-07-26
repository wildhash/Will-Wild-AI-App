# Crisis Support AI Agent with Mood Tracking

Welcome! This repository is your starting point for the **Agentic AI App Hackathon**. It includes:

- A consistent folder structure  
- An environment spec (`environment.yml` or `Dockerfile`)  
- Documentation placeholders to explain your design and demo
- **🆕 Mood Tracking & Analytics** - Real-time mood analysis and visualization

## 📋 Submission Checklist

- [ ] All code in `src/` runs without errors  
- [ ] `ARCHITECTURE.md` contains a clear diagram sketch and explanation  
- [ ] `EXPLANATION.md` covers planning, tool use, memory, and limitations  
- [ ] `DEMO.md` links to a 3–5 min video with timestamped highlights  

## 🎭 Mood Tracking Features

This app includes comprehensive mood tracking and analytics capabilities:

### **Mood Detection**
- **Rule-based keyword analysis** for MVP implementation
- **5 mood categories**: happy, sad, anxious, angry, neutral
- **Confidence scoring** (0.0-1.0) for each detection
- **Keyword extraction** showing which words influenced the mood detection
- **Real-time analysis** of every user message

### **Mood Analytics**
- **Timeline tracking** - Complete mood history for each session
- **Session summaries** - Dominant mood, distribution, and changes
- **Trend analysis** - Track mood transitions over time
- **Confidence averaging** - Overall reliability of mood detections

### **API Endpoints**
- `POST /api/chat` - Enhanced chat with mood analysis included
- `GET /api/mood/{user_id}` - Retrieve complete mood timeline and analytics
- `GET /api/conversation/{user_id}/summary` - Session overview including mood data

### **Testing Mood Tracking**
Run the enhanced test suite to see mood tracking in action:

```bash
python test_api.py
```

The test includes:
- ✅ Happy mood detection ("excited", "wonderful", "amazing")
- ✅ Sad mood detection ("sad", "down", "terrible")  
- ✅ Anxious mood detection ("anxious", "worried", "stressed")
- ✅ Angry mood detection ("angry", "frustrated", "furious")
- ✅ Neutral mood detection (no emotional keywords)
- ✅ Mood timeline tracking across multiple messages
- ✅ Session analytics and trend summaries

### **Example Usage**

1. **Send a message with mood content:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "I am so happy and excited today!"}'
```

2. **Get mood analytics:**
```bash
curl http://localhost:8000/api/mood/user123
```

**Response includes:**
```json
{
  "user_id": "user123",
  "session_start_time": "2025-07-26T03:44:15.165884",
  "mood_timeline": [
    {
      "mood": "happy",
      "confidence": 0.95,
      "keywords": ["happy", "excited"],
      "timestamp": "2025-07-26T03:44:15.169743"
    }
  ],
  "session_mood_summary": {
    "dominant_mood": "happy",
    "mood_distribution": {"happy": 1.0},
    "mood_changes": 0,
    "average_confidence": 0.95
  }
}
```

### **Future Enhancements (TODOs)**
- Replace rule-based analysis with AI/NLP models (Google Gemini integration)
- Add more granular mood states and emotions
- Implement persistent storage for historical mood analysis
- Add mood visualization components for UI
- Include context and conversation history in mood analysis


## 🚀 Getting Started

1. **Clone / Fork** this template.  Very Important. Fork Name MUST be the same name as the teamn name
2. **Install dependencies**  
   ```bash
   # Conda
   conda env create -f environment.yml
   conda activate agentic-hackathon

   #—or Docker—
   docker build -t agentic-agent .
   docker run --rm -it agentic-agent bash

## 📂 Folder Layout

![Folder Layout Diagram](images/folder-githb.png)



## 🏅 Judging Criteria

- **Technical Excellence **  
  This criterion evaluates the robustness, functionality, and overall quality of the technical implementation. Judges will assess the code's efficiency, the absence of critical bugs, and the successful execution of the project's core features.

- **Solution Architecture & Documentation **  
  This focuses on the clarity, maintainability, and thoughtful design of the project's architecture. This includes assessing the organization and readability of the codebase, as well as the comprehensiveness and conciseness of documentation (e.g., GitHub README, inline comments) that enables others to understand and potentially reproduce or extend the solution.

- **Innovative Gemini Integration **  
  This criterion specifically assesses how effectively and creatively the Google Gemini API has been incorporated into the solution. Judges will look for novel applications, efficient use of Gemini's capabilities, and the impact it has on the project's functionality or user experience. You are welcome to use additional Google products.

- **Societal Impact & Novelty **  
  This evaluates the project's potential to address a meaningful problem, contribute positively to society, or offer a genuinely innovative and unique solution. Judges will consider the originality of the idea, its potential real‑world applicability, and its ability to solve a challenge in a new or impactful way.


