from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from .agents.assistant_agent import assistant_agent
from .agents.search_agent import search_agent
from .agents.decision_agent import decision_agent
from .models import FlightSearch, AgentRegistry
def discover_agents():
    agents = AgentRegistry.objects.all()
    print(f"[🔎 Agent Registry] Found {agents.count()} available agents")
    for agent in agents:
        print(f"  - {agent.name} (ID: {agent.agent_id}) | Endpoint: {agent.endpoint} | Capabilities: {agent.capabilities}")
    return agents

def generate_task_id():
    return f"TID-{str(uuid.uuid4())[:8]}"

def generate_conversation_id():
    return f"CID-{str(uuid.uuid4())[:8]}"

class Orchestrator:
    def __init__(self, user):
        self.state = {
            'user': user,
            'source': '',
            'destination': '',
            'date': '',
            'missing_info': ['source', 'destination', 'date'],
            'search_results': [],
            'final_recommendations': [],
            'messages': []
        }

    def validate_date(self, date_str: str) -> bool:
        """Validate date is in YYYY-MM-DD format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def validate_state(self) -> bool:
        """Validate that all required information is present"""
        print("\n[🔍 Orchestrator: Validating State]")
        
        # Check required fields
        for field in ['source', 'destination', 'date']:
            if not self.state.get(field):
                print(f"  ✗ Missing {field}")
                return False
            print(f"  ✓ {field.capitalize()}: {self.state[field]}")
        
        # Validate date format
        if not self.validate_date(self.state['date']):
            print("  ✗ Invalid date format")
            self.state['messages'].append("Invalid date format. Please enter in YYYY-MM-DD format.")
            return False
        
        print("  ✓ All validations passed")
        return True

    def process_message(self, message: str) -> Dict[str, Any]:
        # Discover agents before starting workflow
        discover_agents()
        """Process a user message through the agent pipeline"""
        print("\n" + "="*80)
        print("[🎯 Orchestrator: Starting Message Processing]")
        print(f"📥 User Input: {message}")
        
        # Initialize task and conversation IDs
        task_id = generate_task_id()
        conversation_id = generate_conversation_id()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Note: persistence of ChatLog entries is handled by the view layer
        # so we do not write ChatLog records here. This ensures monitoring
        # sessions (created/ended by the toggle endpoint) are respected.
        
        # Prepare message for Assistant Agent with standardized schema
        assistant_request = {
            "protocol_version": "1.0",
            "timestamp": timestamp,
            "task_id": task_id,
            "sender": "Orchestrator",
            "receiver": "AssistantAgent",
            "conversation_id": conversation_id,
            "payload": {
                "user_message": message,
                "context": {
                    "user_id": f"U-{self.state['user'].id}",
                    "session_active": True,
                    "missing_info": self.state.get('missing_info', []),
                    "current_state": "awaiting_details"
                }
            },
            "metadata": {
                "priority": "normal",
                "intent": "flight_search",
                "language": "en",
                "message_type": "user_query"
            }
        }
        
        print("\n📤 Orchestrator sending JSON to Assistant Agent:")
        print(json.dumps(assistant_request, indent=2))
        
        # Step 1: Assistant Agent
        print("\n[1/4] → Sending to Assistant Agent")
        self.state = assistant_agent(message, self.state)
        
        # Assistant messages are returned in state['messages'] and persisted
        # by the caller (views) so they can attach monitoring_session when needed.
        
        # If we're missing info, return early
        if self.state.get('missing_info'):
            print("\n[⏸️ Orchestrator: Waiting for more information]")
            return {'status': 'waiting', 'messages': self.state['messages']}
        
        # Step 2: Validate State
        print("\n[2/4] → Validating Information")
        if not self.validate_state():
            print("\n[⚠️ Orchestrator: Validation Failed]")
            return {'status': 'invalid', 'messages': self.state['messages']}
        
        # Step 3: Search Agent
        print("\n[3/4] → Sending to Search Agent")
        self.state = search_agent(self.state)
        
        # Search agent messages are included in state and persisted by the view.
        
        # If no results found, return early
        if not self.state.get('search_results'):
            print("\n[⚠️ Orchestrator: No Results Found]")
            return {'status': 'no_results', 'messages': self.state['messages']}
        
        # Step 4: Decision Agent with standardized schema
        print("\n[4/4] → Sending to Decision Agent")
        
        # Prepare normalized data for Decision Agent
        decision_request = {
            "protocol_version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "sender": "Orchestrator",
            "receiver": "DecisionAgent",
            "conversation_id": conversation_id,
            "payload": {
                "search_query": {
                    "source": self.state['source'],
                    "destination": self.state['destination'],
                    "date": self.state['date']
                },
                "aggregated_results": [
                    {
                        "api_source": flight.get('api_source', 'unknown'),
                        "flight_no": flight['flight_no'],
                        "flight_name": flight['flight_name'],
                        "company": flight['company'],
                        "date": flight['date'],
                        "source": flight['source'],
                        "destination": flight['destination'],
                        "price": {
                            "amount": flight['price'],
                            "currency": "INR"
                        },
                        "remaining_seats": flight['remaining_seats']
                    }
                    for flight in self.state.get('search_results', [])
                ]
            },
            "metadata": {
                "intent": "flight_recommendation",
                "schema_validated": True,
                "data_sources": ["JSON", "XML", "SOAP"],
                "conversion_status": "normalized",
                "message_type": "data_package"
            }
        }
        
        print("\n📤 Orchestrator sending JSON to Decision Agent:")
        print(json.dumps(decision_request, indent=2))
        
        # Process through Decision Agent
        self.state = decision_agent(self.state)
        
        # Decision agent messages are included in state and persisted by the view.
            
        print("\n📥 Decision Agent received and processed the request")
        
        # Store the complete search in database
        FlightSearch.objects.create(
            user=self.state['user'],
            source=self.state['source'],
            destination=self.state['destination'],
            date=self.state['date'],
            search_results=self.state['search_results'],
            recommendations=self.state['final_recommendations']
        )
        
        print("\n[✅ Orchestrator: Processing Complete]")
        print("="*80 + "\n")
        
        # Store all messages before resetting state
        messages = self.state['messages']
        
        # Reset state for next search but keep user
        user = self.state['user']
        self.state = {
            'user': user,
            'source': '',
            'destination': '',
            'date': '',
            'missing_info': ['source', 'destination', 'date'],
            'search_results': [],
            'final_recommendations': [],
            'messages': []
        }
        
        return {'status': 'complete', 'messages': messages}