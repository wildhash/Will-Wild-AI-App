import { useState } from 'react'
import './Chat.css'

const USER_ID = 'demo_user' // Hardcoded for now - TODO: Add real authentication

function Chat() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setError('')
    setIsLoading(true)

    // Add user message to chat
    const newUserMessage = {
      id: Date.now(),
      content: userMessage,
      sender: 'user',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newUserMessage])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: USER_ID,
          message: userMessage
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Add AI response to chat
      const aiMessage = {
        id: Date.now() + 1,
        content: data.response,
        sender: 'ai',
        timestamp: new Date(),
        riskLevel: data.risk_level
      }
      setMessages(prev => [...prev, aiMessage])

    } catch (err) {
      console.error('Error sending message:', err)
      setError('Failed to send message. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getRiskLevelClass = (riskLevel) => {
    switch(riskLevel) {
      case 'critical': return 'risk-critical'
      case 'high': return 'risk-high'
      case 'medium': return 'risk-medium'
      default: return 'risk-low'
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Crisis Support AI Chat</h1>
        <p>Connected as: {USER_ID}</p>
        {/* TODO: Add user authentication */}
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>Welcome! I'm here to provide support and assistance. How are you feeling today?</p>
          </div>
        )}
        
        {messages.map(message => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              {message.content}
              {message.riskLevel && (
                <div className={`risk-indicator ${getRiskLevelClass(message.riskLevel)}`}>
                  Risk Level: {message.riskLevel}
                </div>
              )}
            </div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message ai loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              AI is thinking...
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="chat-input">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here... (Press Enter to send)"
          disabled={isLoading}
          rows="3"
        />
        <button 
          onClick={sendMessage} 
          disabled={isLoading || !inputMessage.trim()}
          className="send-button"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>

      <div className="chat-footer">
        <p><em>TODO: Add streaming responses, avatars, mobile responsiveness</em></p>
      </div>
    </div>
  )
}

export default Chat