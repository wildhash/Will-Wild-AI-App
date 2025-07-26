# Agentic AI App Hackathon Template

Welcome! This repository is your starting point for the **Agentic AI App Hackathon**. It includes:

- A consistent folder structure  
- An environment spec (`environment.yml` or `Dockerfile`)  
- Documentation placeholders to explain your design and demo

## 📋 Submission Checklist

- [ ] All code in `src/` runs without errors  
- [ ] `ARCHITECTURE.md` contains a clear diagram sketch and explanation  
- [ ] `EXPLANATION.md` covers planning, tool use, memory, and limitations  
- [ ] `DEMO.md` links to a 3–5 min video with timestamped highlights  


## 🚀 Getting Started

### Backend Setup

1. **Clone / Fork** this template.  Very Important. Fork Name MUST be the same name as the teamn name
2. **Install dependencies**  
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Start the FastAPI backend
   cd src
   python main.py
   ```

### Frontend Setup

3. **Setup React frontend**
   ```bash
   # Install frontend dependencies
   cd frontend
   npm install
   
   # Start the development server
   npm run dev
   ```

4. **Access the application**
   - **Chat Interface:** http://localhost:5173
   - **Backend API:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs

> **Note:** Make sure both backend (port 8000) and frontend (port 5173) are running for full functionality.

## 📂 Folder Layout

![Folder Layout Diagram](images/folder-githb.png)

### Project Structure

```
├── src/                    # Backend FastAPI application
│   ├── api/               # API endpoints
│   ├── agents/            # AI agent logic
│   ├── models/            # Data models
│   └── services/          # Core services
├── frontend/              # React chat interface
│   ├── src/               
│   │   ├── components/    # React components
│   │   └── ...           
│   └── README.md          # Frontend-specific setup
├── requirements.txt       # Python dependencies
└── README.md             # This file
```



## 🏅 Judging Criteria

- **Technical Excellence **  
  This criterion evaluates the robustness, functionality, and overall quality of the technical implementation. Judges will assess the code's efficiency, the absence of critical bugs, and the successful execution of the project's core features.

- **Solution Architecture & Documentation **  
  This focuses on the clarity, maintainability, and thoughtful design of the project's architecture. This includes assessing the organization and readability of the codebase, as well as the comprehensiveness and conciseness of documentation (e.g., GitHub README, inline comments) that enables others to understand and potentially reproduce or extend the solution.

- **Innovative Gemini Integration **  
  This criterion specifically assesses how effectively and creatively the Google Gemini API has been incorporated into the solution. Judges will look for novel applications, efficient use of Gemini's capabilities, and the impact it has on the project's functionality or user experience. You are welcome to use additional Google products.

- **Societal Impact & Novelty **  
  This evaluates the project's potential to address a meaningful problem, contribute positively to society, or offer a genuinely innovative and unique solution. Judges will consider the originality of the idea, its potential real‑world applicability, and its ability to solve a challenge in a new or impactful way.


