"""
Demo script for Crisis Support & Mental Health Agent

This script demonstrates how to use the TherapyAgent with GeminiService,
SafetyService, and MemoryService for mental health support conversations.

Usage:
    python demo.py

Note: You need to set GEMINI_API_KEY in your environment or .env file
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import get_config
from src.services.gemini_service import GeminiService
from src.services.safety_service import SafetyService
from src.services.memory_service import MemoryService
from src.agents.therapy_agent import TherapyAgent


class MentalHealthAgentDemo:
    """
    Demo class showing the complete mental health agent workflow
    """
    
    def __init__(self):
        """Initialize the demo with all required services"""
        self.config = get_config()
        
        # Validate configuration
        validation = self.config.validate()
        if not validation["valid"]:
            print("❌ Configuration validation failed:")
            for error in validation["errors"]:
                print(f"  - {error}")
            sys.exit(1)
        
        if validation["warnings"]:
            print("⚠️  Configuration warnings:")
            for warning in validation["warnings"]:
                print(f"  - {warning}")
            print()
        
        # Initialize services
        print("🔧 Initializing services...")
        self.gemini_service = GeminiService(
            api_key=self.config.gemini.api_key,
            model_name=self.config.gemini.model_name
        )
        self.safety_service = SafetyService()
        self.memory_service = MemoryService()
        
        # Initialize therapy agent
        self.therapy_agent = TherapyAgent(
            gemini_service=self.gemini_service,
            safety_service=self.safety_service,
            memory_service=self.memory_service
        )
        
        print("✅ All services initialized successfully!")
        print()
    
    async def run_demo_conversation(self):
        """Run a complete demo conversation showing different scenarios"""
        print("🧠 Crisis Support & Mental Health Agent Demo")
        print("=" * 50)
        print()
        
        # Demo user
        user_id = "demo_user_001"
        session_id = None  # Will be created automatically
        
        # Scenario 1: Initial support-seeking conversation
        print("📝 Scenario 1: User seeking initial support")
        print("-" * 40)
        
        response1 = await self.process_message(
            "I've been feeling really down lately and I don't know what to do. Everything feels overwhelming.",
            user_id,
            session_id
        )
        session_id = response1["session_id"]  # Get session ID for continuity
        
        # Scenario 2: Moderate risk conversation
        print("\n📝 Scenario 2: User expressing moderate distress")
        print("-" * 40)
        
        response2 = await self.process_message(
            "I feel like nothing I do matters anymore. I'm having trouble sleeping and I just feel hopeless about the future.",
            user_id,
            session_id
        )
        
        # Scenario 3: Testing CBT intervention
        print("\n📝 Scenario 3: CBT intervention demonstration")
        print("-" * 40)
        
        response3 = await self.process_message(
            "I keep thinking that I'm a failure and that I'll never succeed at anything. These thoughts won't stop.",
            user_id,
            session_id
        )
        
        # Scenario 4: Grounding technique request
        print("\n📝 Scenario 4: User requesting coping strategies")
        print("-" * 40)
        
        response4 = await self.process_message(
            "I'm feeling really anxious right now and my heart is racing. Can you help me calm down?",
            user_id,
            session_id
        )
        
        # Show session summary
        print("\n📊 Session Summary")
        print("-" * 40)
        summary = await self.therapy_agent.get_session_summary(session_id)
        if summary:
            self.display_session_summary(summary)
        
        print("\n✅ Demo completed successfully!")
        print("\n💡 This demonstrates the core capabilities of the Crisis Support & Mental Health Agent:")
        print("   • AI-powered risk assessment and response generation")
        print("   • CBT and grounding technique interventions")
        print("   • Session memory and therapeutic progress tracking")
        print("   • Safety protocols and crisis resource provision")
        print("   • Evidence-based mental health support")
    
    async def process_message(self, message: str, user_id: str, session_id: str = None) -> Dict[str, Any]:
        """Process a user message and display the results"""
        print(f"👤 User: {message}")
        print()
        
        try:
            response = await self.therapy_agent.process_user_message(
                message=message,
                user_id=user_id,
                session_id=session_id
            )
            
            # Display response
            print(f"🤖 Agent: {response['message']}")
            print()
            
            # Display risk assessment
            risk = response.get("risk_assessment", {})
            risk_level = risk.get("level", "unknown")
            risk_score = risk.get("score", 0.0)
            
            risk_emoji = {
                "low": "🟢",
                "moderate": "🟡", 
                "high": "🟠",
                "crisis": "🔴"
            }.get(risk_level, "⚪")
            
            print(f"📊 Risk Assessment: {risk_emoji} {risk_level.upper()} (Score: {risk_score:.2f})")
            
            if risk.get("indicators"):
                print(f"   Indicators: {', '.join(risk['indicators'])}")
            
            # Display interventions
            interventions = response.get("interventions", [])
            if interventions:
                print(f"🎯 Interventions Applied:")
                for intervention in interventions:
                    intervention_type = intervention.get("type", "unknown")
                    effectiveness = intervention.get("effectiveness", 0.0)
                    print(f"   • {intervention_type.replace('_', ' ').title()} (Effectiveness: {effectiveness:.1f})")
            
            # Display crisis resources if needed
            if response.get("crisis_resources"):
                print(f"🚨 Crisis Resources Available:")
                resources = response["crisis_resources"]
                if isinstance(resources, dict):
                    for resource_type, contact in resources.items():
                        if isinstance(contact, dict):
                            contact_info = contact.get("phone", contact.get("text", str(contact)))
                            description = contact.get("description", "")
                            print(f"   • {resource_type.replace('_', ' ').title()}: {contact_info}")
                            if description:
                                print(f"     {description}")
                        else:
                            print(f"   • {resource_type.replace('_', ' ').title()}: {contact}")
            
            print()
            return response
            
        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")
            print()
            return {"error": str(e)}
    
    def display_session_summary(self, summary: Dict[str, Any]):
        """Display a formatted session summary"""
        print(f"Session ID: {summary.get('session_id', 'Unknown')}")
        print(f"Duration: {summary.get('duration_minutes', 0)} minutes")
        print(f"Total Interactions: {summary.get('total_interactions', 0)}")
        print(f"Current Phase: {summary.get('therapy_phase', 'Unknown')}")
        print(f"Average Risk Score: {summary.get('average_risk_score', 0.0)}")
        
        interventions = summary.get("interventions_applied", {})
        if interventions:
            print("Interventions Applied:")
            for intervention_type, data in interventions.items():
                print(f"  • {intervention_type.replace('_', ' ').title()}: {data.get('count', 0)} times")
                print(f"    Avg Effectiveness: {data.get('avg_effectiveness', 0.0):.1f}")
    
    async def run_interactive_demo(self):
        """Run an interactive demo where user can input messages"""
        print("🧠 Interactive Crisis Support & Mental Health Agent Demo")
        print("=" * 55)
        print("Type 'quit' to exit, 'help' for commands")
        print()
        
        user_id = "interactive_user"
        session_id = None
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    if session_id:
                        await self.therapy_agent.end_session(session_id, "User ended session")
                    print("👋 Thank you for using the Mental Health Agent. Take care!")
                    break
                
                if user_input.lower() in ['help', 'h']:
                    self.show_help()
                    continue
                
                if user_input.lower() == 'summary':
                    if session_id:
                        summary = await self.therapy_agent.get_session_summary(session_id)
                        if summary:
                            print("\n📊 Current Session Summary:")
                            print("-" * 30)
                            self.display_session_summary(summary)
                            print()
                    else:
                        print("No active session to summarize.")
                    continue
                
                if not user_input:
                    continue
                
                response = await self.process_message(user_input, user_id, session_id)
                if not session_id and "session_id" in response:
                    session_id = response["session_id"]
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Take care!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def show_help(self):
        """Show help information"""
        print("\n📖 Available Commands:")
        print("  help, h     - Show this help message")
        print("  summary     - Show current session summary") 
        print("  quit, exit  - End the session and exit")
        print("\n💡 Tips:")
        print("  • Share how you're feeling or what's on your mind")
        print("  • The agent can help with anxiety, depression, stress, and crisis situations")
        print("  • All conversations are handled with care and confidentiality")
        print("  • If you're in crisis, the agent will provide immediate resources")
        print()


async def main():
    """Main demo function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Run interactive demo
        demo = MentalHealthAgentDemo()
        await demo.run_interactive_demo()
    else:
        # Run scripted demo
        demo = MentalHealthAgentDemo()
        await demo.run_demo_conversation()


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("  export GEMINI_API_KEY='your_api_key_here'")
        print("Or create a .env file with GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        sys.exit(1)