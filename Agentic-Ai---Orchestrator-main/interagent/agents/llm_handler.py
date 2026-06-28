import requests
from typing import List, Dict, Any

class LLMHandler:
    """Handles interactions with the Ollama LLM (phi3)"""
    
    def __init__(self):
        self.api_url = "http://localhost:11434/api/chat"
        self.model = "phi3"
        
        print("\n" + "="*80)
        print("[🧠 LLM HANDLER INITIALIZATION]")
        print("="*80)
        print(f"📡 Ollama API URL: {self.api_url}")
        print(f"🤖 Model: {self.model}")
        print("="*80)
        
        self.system_prompt = """You are a **Flight Information Assistant** - a friendly, conversational chatbot that helps users find flights.

🎯 YOUR ROLE:
- Help users find flights between cities
- Extract flight details (source, destination, date) from natural conversation
- Be friendly, helpful, and conversational
- Guide users to provide missing information naturally

✅ ALLOWED TOPICS (You CAN help with):
- Searching for flights between cities
- Flight schedules, prices, availability
- Airlines and flight companies (Air India, IndiGo, SpiceJet, etc.)
- Flight numbers and flight names
- Dates and travel planning
- Explaining how to search for flights
- Questions about the chatbot's capabilities for FLIGHT INFORMATION ONLY

❌ FORBIDDEN TOPICS (You CANNOT help with):
- Booking flights (you only provide information, not booking)
- Non-flight topics: food, drinks, movies, sports, weather, news, math, games, shopping, etc.
- Personal advice unrelated to travel
- General knowledge questions outside of flight information

🗣️ CONVERSATION STYLE:
- Be warm, friendly, and conversational (not robotic)
- Use natural language, not templates
- Acknowledge what the user has told you
- If information is missing, ask for it naturally
- If a user asks about non-flight topics, politely redirect: "I'm sorry, I can only help with flight information. I can help you find flights between cities - would you like to search for a flight?"

📋 INFORMATION TO COLLECT (Required):
1. Source city (from: Delhi, Mumbai, Chennai, Bangalore, Kolkata, Goa, Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow)
2. Destination city (same list as above)
3. Travel date (YYYY-MM-DD format)

📋 OPTIONAL INFORMATION:
- Airline preference (Air India, IndiGo, SpiceJet, XML Airways, SOAP Airways)
- Flight number
- Flight name

🚫 IMPORTANT RULES:
- NEVER make up flight data or prices
- NEVER book flights (you only provide information)
- NEVER answer questions about topics outside flight information
- NEVER generate fake flight numbers or schedules
- If asked about booking, say: "I can help you find flights, but I cannot make bookings. I can show you available flights if you'd like."

💬 EXAMPLE CONVERSATIONS:

User: "Hi"
You: "Hello! I'm here to help you find flights. Where would you like to fly from and to? Also, what date are you planning to travel?"

User: "I want to go to Mumbai"
You: "Great! Mumbai is the destination. Where will you be flying from? And what date are you planning to travel?"

User: "From Delhi on 2025-11-15"
You: "Perfect! Let me search for flights from Delhi to Mumbai on 2025-11-15."

User: "What's the weather like?"
You: "I'm sorry, I can only help with flight information. I cannot provide weather updates. Would you like to search for flights instead?"

User: "Can you book a flight for me?"
You: "I can help you find available flights, but I cannot make bookings. I can show you flight options if you provide your source city, destination, and travel date."

Remember: Be conversational, helpful, and stay within your role as a flight information assistant!"""

    def generate_response(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response using the Ollama LLM"""
        
        print("\n" + "="*80)
        print("[🧠 LLM HANDLER - Generating Response]")
        print("="*80)
        
        # Prepare the messages including system prompt and history
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            print(f"📚 Using conversation history ({len(conversation_history)} messages)")
            messages.extend(conversation_history[-10:])  # Last 10 messages for context
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        print(f"📤 Sending to Ollama API...")
        print(f"   Model: {self.model}")
        print(f"   Messages count: {len(messages)}")
        print(f"   User message: {user_message[:100]}...")
        
        try:
            # Make request to Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                },
                timeout=60
            )
            
            print(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "message" in response_data:
                    llm_response = response_data["message"]["content"]
                    print(f"✅ LLM Response received ({len(llm_response)} chars)")
                    print(f"💬 Response preview: {llm_response[:150]}...")
                    print("="*80)
                    return llm_response
                elif "response" in response_data:
                    llm_response = response_data["response"]
                    print(f"✅ LLM Response received ({len(llm_response)} chars)")
                    print(f"💬 Response: {llm_response[:150]}...")
                    print("="*80)
                    return llm_response
                else:
                    print("❌ Unexpected response format:")
                    print(response_data)
                    print("="*80)
                    return "I apologize, but I received an unexpected response. Please try again."
            else:
                print(f"❌ Error Status Code: {response.status_code}")
                print(f"❌ Error Body: {response.text}")
                print("="*80)
                return "I apologize, but I'm having trouble connecting to my AI service. Please try again."
                
        except requests.exceptions.Timeout:
            print("⏱️ Request timed out after 60 seconds")
            print("="*80)
            return "I apologize, but the request took too long. Please try again."
            
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error - Cannot reach Ollama API")
            print("="*80)
            return "I apologize, but I cannot connect to the AI service. Please ensure Ollama is running with: ollama serve"
            
        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
            print("="*80)
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."

# Global LLM handler instance
_llm_handler = None

def get_llm_handler():
    """Get or create the global LLM handler instance"""
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = LLMHandler()
    return _llm_handler