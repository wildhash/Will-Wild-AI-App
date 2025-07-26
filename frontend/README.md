# Crisis Support AI Chat - Frontend

A minimal React-based chat frontend for the Crisis Support AI Agent, built for hackathon/demo purposes.

## Features

- ✅ Real-time chat interface with message history
- ✅ Connects to FastAPI backend at `/api/chat` endpoint
- ✅ Loading states with typing indicator
- ✅ Error handling and user feedback
- ✅ Risk level visualization (low, medium, high, critical)
- ✅ Responsive design basics
- ✅ Enter key support for sending messages

## Quick Start

### Prerequisites

- Node.js (v18+ recommended)
- FastAPI backend running on `localhost:8000`

### Installation & Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   - Frontend: http://localhost:5173
   - Backend API docs: http://localhost:8000/docs

### Backend Connection

The frontend is configured to proxy API requests to `localhost:8000`. Make sure your FastAPI backend is running:

```bash
# In the project root directory
cd src
python main.py
```

## Usage

1. Type your message in the text area
2. Click "Send" or press Enter to send
3. View AI responses with risk level indicators
4. Chat history is maintained during the session

## Current User Authentication

- **Hardcoded User ID:** `demo_user`
- **TODO:** Implement real user authentication system

## API Integration

The frontend expects the backend to respond with:

```json
{
  "response": "AI response text",
  "risk_level": "low|medium|high|critical",
  "session_id": "optional_session_id"
}
```

## Development Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## TODOs for Future Development

- [ ] User authentication and session management
- [ ] Streaming responses for real-time chat
- [ ] User avatars and enhanced UI/UX
- [ ] Mobile responsiveness and accessibility improvements
- [ ] Message persistence and chat history
- [ ] File upload support
- [ ] Dark mode toggle
- [ ] Keyboard shortcuts and accessibility features

## Technology Stack

- **Framework:** React 19
- **Build Tool:** Vite 7
- **Styling:** Vanilla CSS with modern features
- **HTTP Client:** Fetch API
- **Development:** Hot reload with Vite

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Chat.jsx       # Main chat component
│   │   └── Chat.css       # Chat styling
│   ├── App.jsx            # Root component
│   ├── App.css            # Global styles
│   └── main.jsx           # Entry point
├── public/                # Static assets
├── package.json           # Dependencies and scripts
└── vite.config.js         # Vite configuration with proxy
```

## Troubleshooting

**Frontend not connecting to backend:**
- Ensure backend is running on port 8000
- Check browser developer tools for CORS errors
- Verify proxy configuration in `vite.config.js`

**Build issues:**
- Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
- Check Node.js version compatibility

**Styling issues:**
- Hard refresh browser: Ctrl+F5 or Cmd+Shift+R
- Check browser developer tools for CSS conflicts