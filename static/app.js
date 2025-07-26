/**
 * Crisis Support AI Agent - Frontend JavaScript
 * MVP Implementation for Hackathon Demo
 * 
 * TODO: Future enhancements:
 * - WebSocket for real-time chat updates
 * - Offline support with service workers
 * - Advanced resource filtering and sorting
 * - User preference persistence
 * - Voice input/output capabilities
 * - Multi-language support
 * - Analytics and user feedback collection
 */

class CrisisSupportApp {
    constructor() {
        this.apiBaseUrl = window.location.origin + '/api';
        this.currentUserId = '';
        this.isLoading = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.initializeApp();
    }
    
    initializeElements() {
        // Chat elements
        this.userIdInput = document.getElementById('userId');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.showResourcesBtn = document.getElementById('showResourcesBtn');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        
        // Resources elements
        this.resourcesSection = document.getElementById('resourcesSection');
        this.resourcesContent = document.getElementById('resourcesContent');
        this.closeResourcesBtn = document.getElementById('closeResourcesBtn');
        
        // Emergency banner
        this.emergencyBanner = document.getElementById('emergencyBanner');
    }
    
    attachEventListeners() {
        // Chat functionality
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Resource functionality
        this.showResourcesBtn.addEventListener('click', () => this.showResources());
        this.closeResourcesBtn.addEventListener('click', () => this.hideResources());
        
        // Utility functions
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        this.userIdInput.addEventListener('change', () => this.updateUserId());
    }
    
    initializeApp() {
        this.currentUserId = this.userIdInput.value || 'demo_user';
        this.hideResources();
        this.log('Crisis Support AI Agent initialized');
    }
    
    updateUserId() {
        this.currentUserId = this.userIdInput.value || 'demo_user';
        this.log(`User ID updated to: ${this.currentUserId}`);
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        this.currentUserId = this.userIdInput.value || 'demo_user';
        
        // Add user message to chat
        this.addMessageToChat('user', message);
        this.messageInput.value = '';
        this.setLoading(true);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.currentUserId,
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Add assistant response to chat
            this.addMessageToChat('assistant', data.response, data.risk_level);
            
            // Show emergency banner for high risk levels
            if (data.risk_level === 'high' || data.risk_level === 'critical') {
                this.showEmergencyBanner();
            }
            
            this.log(`Message sent successfully. Risk level: ${data.risk_level}`);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToChat('system', 
                '⚠️ Sorry, I encountered an error. If this is an emergency, please call 988 or 911 immediately.',
                'error'
            );
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessageToChat(role, content, riskLevel = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        contentDiv.appendChild(paragraph);
        
        // Add timestamp and risk indicator
        const metaInfo = document.createElement('small');
        const timestamp = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        let metaText = `${role === 'user' ? 'You' : role === 'assistant' ? 'Assistant' : 'System'} • ${timestamp}`;
        
        if (riskLevel && riskLevel !== 'low' && riskLevel !== 'error') {
            const riskSpan = document.createElement('span');
            riskSpan.className = `risk-indicator risk-${riskLevel}`;
            riskSpan.textContent = riskLevel.toUpperCase();
            metaInfo.appendChild(document.createTextNode(metaText));
            metaInfo.appendChild(riskSpan);
        } else {
            metaInfo.textContent = metaText;
        }
        
        contentDiv.appendChild(metaInfo);
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    async showResources() {
        this.currentUserId = this.userIdInput.value || 'demo_user';
        
        // Show the resources section
        this.resourcesSection.classList.remove('hidden');
        
        // Show loading state
        this.resourcesContent.innerHTML = `
            <div class="loading">
                <p>🔄 Finding personalized resources for you...</p>
            </div>
        `;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/resources`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.currentUserId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.displayResources(data.resources, data);
            
            this.log(`Loaded ${data.resources.length} resources for user`);
            
        } catch (error) {
            console.error('Error loading resources:', error);
            this.resourcesContent.innerHTML = `
                <div class="no-resources">
                    <p>⚠️ Unable to load resources at this time.</p>
                    <p>For immediate help, call 988 (Suicide & Crisis Lifeline)</p>
                </div>
            `;
        }
    }
    
    displayResources(resources, metadata = {}) {
        if (!resources || resources.length === 0) {
            this.resourcesContent.innerHTML = `
                <div class="no-resources">
                    <p>🔍 No specific resources found.</p>
                    <p>Try having a conversation first to get personalized recommendations.</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        
        // Add metadata info if available
        if (metadata.risk_level) {
            html += `
                <div class="resource-meta" style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 16px; font-size: 0.9rem; color: #666;">
                    <strong>Personalized for you:</strong> ${metadata.message_count || 0} messages analyzed, 
                    current assessment: ${metadata.risk_level || 'unknown'}
                </div>
            `;
        }
        
        // Add resources
        resources.forEach(resource => {
            html += `
                <div class="resource-item" onclick="window.open('${resource.link}', '_blank')">
                    <h3 class="resource-name">${this.escapeHtml(resource.name)}</h3>
                    <p class="resource-description">${this.escapeHtml(resource.description)}</p>
                    <a href="${resource.link}" target="_blank" class="resource-link" onclick="event.stopPropagation()">
                        🔗 Visit Resource
                    </a>
                </div>
            `;
        });
        
        // Add call-to-action footer
        html += `
            <div style="margin-top: 20px; padding: 16px; background: #e8f5e8; border-radius: 8px; text-align: center;">
                <p style="color: #27ae60; font-weight: 500; margin-bottom: 8px;">
                    💡 Resources are personalized based on your conversation
                </p>
                <p style="color: #666; font-size: 0.9rem;">
                    Continue chatting to get more targeted recommendations
                </p>
            </div>
        `;
        
        this.resourcesContent.innerHTML = html;
    }
    
    hideResources() {
        this.resourcesSection.classList.add('hidden');
    }
    
    showEmergencyBanner() {
        this.emergencyBanner.style.display = 'block';
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            this.emergencyBanner.style.display = 'none';
        }, 10000);
    }
    
    clearChat() {
        // Keep the system welcome message
        const systemMessage = this.chatMessages.querySelector('.system-message');
        this.chatMessages.innerHTML = '';
        if (systemMessage) {
            this.chatMessages.appendChild(systemMessage.cloneNode(true));
        }
        
        this.hideResources();
        this.log('Chat cleared');
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading;
        this.sendButton.textContent = loading ? 'Sending...' : 'Send';
        this.messageInput.disabled = loading;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    log(message) {
        console.log(`[CrisisSupportApp] ${message}`);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.crisisSupportApp = new CrisisSupportApp();
    
    // Add some helpful console messages for demo purposes
    console.log('%c🤝 Crisis Support AI Agent - MVP Demo', 'font-size: 16px; font-weight: bold; color: #3498db;');
    console.log('%cThis is a hackathon demonstration of a mental health support system.', 'color: #666;');
    console.log('%cFeatures: Context-aware chat, personalized resource matching, crisis detection', 'color: #666;');
    console.log('%c\nTODO for production:', 'font-weight: bold; color: #e74c3c;');
    console.log('- Real-time WebSocket communication');
    console.log('- Advanced AI-powered resource ranking');
    console.log('- Geo-location based resource filtering');
    console.log('- User authentication and data persistence');
    console.log('- Professional mental health provider integration');
    console.log('- Comprehensive privacy and security measures');
});

// Export for potential testing or extension
window.CrisisSupportApp = CrisisSupportApp;