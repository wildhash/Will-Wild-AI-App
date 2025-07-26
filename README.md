# Agentic AI App Hackathon Template

Welcome! This repository is your starting point for the **Agentic AI App Hackathon**. It includes:

- A consistent folder structure  
- An environment spec (`environment.yml` or `Dockerfile`)  
- Documentation placeholders to explain your design and demo
- **Session persistence and conversation memory** for continuous, intelligent chat experiences

## 📋 Submission Checklist

- [x] All code in `src/` runs without errors  
- [ ] `ARCHITECTURE.md` contains a clear diagram sketch and explanation  
- [ ] `EXPLANATION.md` covers planning, tool use, memory, and limitations  
- [ ] `DEMO.md` links to a 3–5 min video with timestamped highlights  


## 🚀 Getting Started

1. **Clone / Fork** this template.  Very Important. Fork Name MUST be the same name as the teamn name
2. **Install dependencies**  
   ```bash
   # Using pip
   pip install -r requirements.txt

   # Or using Conda
   conda env create -f environment.yml
   conda activate agentic-hackathon

   #—or Docker—
   docker build -t agentic-agent .
   docker run --rm -it agentic-agent bash
   ```

3. **Start the backend server**
   ```bash
   cd src
   python main.py
   ```

4. **Test the API** (optional)
   ```bash
   python test_api.py
   ```

5. **Open the frontend demo**
   ```bash
   # In a new terminal
   cd frontend
   python -m http.server 3000
   # Open http://localhost:3000 in your browser
   ```

## 💬 Session Persistence & Conversation Memory

This app now supports **continuous, intelligent chat experiences** with:

### ✨ Features
- **Session Management**: Create and manage conversation sessions with unique IDs
- **Conversation Memory**: Persistent chat history that survives page refreshes
- **Risk Assessment**: Dynamic risk level tracking (LOW, MEDIUM, HIGH, CRITICAL)
- **Personalized Resources**: Context-aware mental health resource recommendations
- **Real-time Updates**: Live session state updates and message counting

### 🔗 API Endpoints

#### Session Management
- `POST /api/sessions` - Create a new session
- `GET /api/sessions/{session_id}` - Retrieve session info and chat history
- `DELETE /api/sessions/{session_id}` - Clear/delete a session

#### Chat & Resources
- `POST /api/chat` - Send messages (supports both session-based and legacy user-based)
- `GET /api/resources` - Get mental health resources (personalized when session_id provided)
- `GET /api/health` - Health check endpoint

### 🧪 Testing Session Persistence

1. **Start the servers** (backend on :8000, frontend on :3000)

2. **Create a new session**:
   ```bash
   curl -X POST http://localhost:8000/api/sessions \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_user"}'
   ```

3. **Send messages**:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "message": "I am feeling overwhelmed",
       "session_id": "YOUR_SESSION_ID"
     }'
   ```

4. **Retrieve session history**:
   ```bash
   curl http://localhost:8000/api/sessions/YOUR_SESSION_ID
   ```

5. **Test persistence**: Refresh the frontend page - your conversation should automatically restore!

### 🎯 Demo Workflow

1. **Open** http://localhost:3000
2. **Click "New Session"** - creates a unique session ID stored in localStorage
3. **Send multiple messages** - watch the message count and risk level update
4. **Click "Get Resources"** - see personalized recommendations based on conversation context
5. **Refresh the page** - conversation history automatically restores from the session
6. **Test different risk levels** with keywords like "stressed", "overwhelmed", "hopeless"

### 🏗️ Architecture

The session persistence system uses:
- **Backend**: FastAPI with in-memory session storage (MVP)
- **Frontend**: Vanilla JavaScript with localStorage for session persistence
- **Memory Service**: Enhanced to support both session-based and user-based storage
- **Safety Service**: Risk assessment with session-aware logging
- **Error Handling**: Graceful handling of missing/expired sessions

### 🔮 Future Enhancements (TODOs)

- [ ] Persistent database storage (Redis, PostgreSQL)
- [ ] Session expiration and cleanup
- [ ] Advanced analytics and conversation insights
- [ ] Multi-user session sharing
- [ ] Enhanced crisis intervention workflows

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


