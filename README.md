# Agentic AI App Hackathon Template

Welcome! This repository is your starting point for the **Agentic AI App Hackathon**. It includes:

- A consistent folder structure  
- An environment spec (`environment.yml` or `Dockerfile`)  
- Documentation placeholders to explain your design and demo

## 🤝 Crisis Support AI Agent - MVP Resource Matching Engine

This project implements an **MVP Resource Matching Engine** that provides personalized mental health resource recommendations based on conversation context, mood analysis, and risk assessment. Built for hackathon demo impact with clear extensibility for production deployment.

### ✨ Key Features

- **💬 Contextual Chat Support**: AI-powered mental health conversations with crisis detection
- **🔍 Smart Resource Matching**: Personalized recommendations based on conversation analysis
- **⚡ Real-time Risk Assessment**: Automatic detection of crisis situations with appropriate escalation
- **🎯 Keyword-Based Matching**: MVP algorithm matching resources to user concerns (anxiety, depression, etc.)
- **📱 Mobile-Friendly UI**: Clean, accessible interface optimized for mental health support

### 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   cd src
   python main.py
   ```

3. **Access the Application**
   - **Frontend**: http://localhost:8000/static/index.html
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/health

### 🎮 Demo Usage

1. **Start a Conversation**:
   - Enter a user ID (or use default "demo_user")
   - Type your message about how you're feeling
   - Click "Send" to get AI support response

2. **View Personalized Resources**:
   - Click "🔍 Show Resources" button
   - View contextually matched mental health resources
   - Resources are personalized based on your conversation keywords and risk level

3. **Interactive Resources**:
   - Click any resource to visit their website
   - Resources include crisis hotlines, therapy platforms, educational content
   - Resource matching improves with more conversation context

### 🛠 API Endpoints

- `POST /api/chat` - Send messages and receive AI responses
- `POST /api/resources` - Get personalized resource recommendations
- `GET /api/health` - Check system status
- `GET /api/conversation/{user_id}/summary` - Get conversation analytics

### 📋 Submission Checklist

- [x] All code in `src/` runs without errors  
- [x] `ARCHITECTURE.md` contains a clear diagram sketch and explanation  
- [x] `EXPLANATION.md` covers planning, tool use, memory, and limitations  
- [x] `DEMO.md` links to a 3–5 min video with timestamped highlights  


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


