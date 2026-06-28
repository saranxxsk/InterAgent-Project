import re
from datetime import datetime
from typing import Tuple, Optional, Dict, List, Any
from .llm_handler import get_llm_handler

class AssistantAgent:
    """Assistant Agent that handles user interactions with real-time LLM conversation"""
    
    FLIGHT_CITIES = {
        'delhi', 'mumbai', 'chennai', 'bangalore', 'kolkata', 'goa', 
        'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'lucknow'
    }
    
    FLIGHT_COMPANIES = {
        'air india', 'indigo', 'spicejet', 'xml airways', 'soap airways'
    }
    
    FLIGHT_NAMES_MAP = {
        'delhi express': 'air india',
        'indigo swift': 'indigo', 
        'chennai express': 'air india', 
        'indigo south': 'indigo',
        'spicejet south': 'spicejet', 
        'xml airliner': 'xml airways', 
        'soap express': 'soap airways'
    }

    def __init__(self):
        self.required_info = {'source': None, 'destination': None, 'date': None}
        self.optional_info = {
            'flight_number': None, 
            'flight_name': None,
            'company': None
        }
        self.llm_handler = get_llm_handler()
        self.conversation_history = []
        self.last_search_completed = False
        
    def process_message(self, user_message: str) -> dict:
        """Process user message with real-time LLM conversation"""
        print("\n" + "="*80)
        print("[🤖 ASSISTANT AGENT - Processing Message]")
        print("="*80)
        print(f"📥 User Message: {user_message}")
        
        try:
            user_message_lower = user_message.lower().strip()
            
            # Reset conversation if user starts fresh or changes search criteria
            reset_keywords = ['hi', 'hello', 'hey', 'new search', 'start over', 'reset']
            if any(keyword in user_message_lower for keyword in reset_keywords) and len(user_message_lower.split()) <= 3:
                print("🔄 Detected greeting/reset - Starting fresh conversation")
                self.reset()
                llm_response = self.llm_handler.generate_response(user_message, self.conversation_history)
                self._update_history(user_message, llm_response)
                return {
                    'messages': [llm_response],
                    'missing_info': True,
                    'optional_info': self.optional_info.copy()
                }
            
            # Check if user is modifying previous search
            modification_detected = self._detect_search_modification(user_message_lower)
            if modification_detected:
                print("🔄 Search modification/filter detected - marking search as incomplete")
                self.last_search_completed = False
            
            # Generate LLM response for natural conversation
            print("\n[🧠 Calling LLM for natural conversation]")
            
            # Build context for LLM
            context = self._build_llm_context()
            full_prompt = f"{context}\n\nUser: {user_message}"
            
            print(f"📝 LLM Context:\n{context}")
            print(f"📤 Sending to LLM: {full_prompt[:200]}...")
            
            llm_response = self.llm_handler.generate_response(full_prompt, self.conversation_history)
            print(f"📨 LLM Response: {llm_response}")
            
            # Update conversation history
            self._update_history(user_message, llm_response)
            
            # Extract flight details from user message
            print("\n[🔍 Extracting Flight Details]")
            source, destination, date, new_optional_info = self._extract_flight_details(user_message)
            
            print(f"Extracted - Source: {source}, Destination: {destination}, Date: {date}")
            print(f"Optional - Flight#: {new_optional_info['flight_number']}, Name: {new_optional_info['flight_name']}, Company: {new_optional_info['company']}")
            
            # Update required info with new information (overwrites if new)
            if source:
                print(f"✓ Updating source: {self.required_info['source']} → {source}")
                self.required_info['source'] = source
            if destination:
                print(f"✓ Updating destination: {self.required_info['destination']} → {destination}")
                self.required_info['destination'] = destination
            if date:
                print(f"✓ Updating date: {self.required_info['date']} → {date}")
                self.required_info['date'] = date
            
            # Update optional info (overwrites if new)
            if new_optional_info['flight_number']:
                print(f"✓ Updating flight number: {new_optional_info['flight_number']}")
                self.optional_info['flight_number'] = new_optional_info['flight_number']
            if new_optional_info['flight_name']:
                print(f"✓ Updating flight name: {new_optional_info['flight_name']}")
                self.optional_info['flight_name'] = new_optional_info['flight_name']
            if new_optional_info['company']:
                print(f"✓ Updating company: {new_optional_info['company']}")
                self.optional_info['company'] = new_optional_info['company']
            
            # Check what information is still missing
            missing = self._check_missing_info()
            print(f"\n📋 Missing information: {missing if missing else 'None - All required info collected!'}")
            
            if missing:
                # Missing required information
                print("❌ Cannot proceed to search - missing required info")
                return {
                    'messages': [llm_response],
                    'missing_info': True,
                    'optional_info': self.optional_info.copy(),
                    'source': self.required_info['source'],
                    'destination': self.required_info['destination'],
                    'date': self.required_info['date']
                }
            
            # All required info collected - proceed to search
            print("\n✅ All required information collected!")
            print(f"📍 Source: {self.required_info['source']}")
            print(f"📍 Destination: {self.required_info['destination']}")
            print(f"📅 Date: {self.required_info['date']}")
            if self.optional_info['flight_number']:
                print(f"✈️ Flight Number: {self.optional_info['flight_number']}")
            if self.optional_info['company']:
                print(f"🏢 Company: {self.optional_info['company']}")
            if self.optional_info['flight_name']:
                print(f"📛 Flight Name: {self.optional_info['flight_name']}")
            
            search_msg = self._create_search_message()
            self.last_search_completed = True
            
            print(f"\n🔍 Search Message: {search_msg}")
            print("="*80)
            
            return {
                'messages': [llm_response, search_msg],
                'missing_info': False,
                'optional_info': self.optional_info.copy(),
                'source': self.required_info['source'],
                'destination': self.required_info['destination'],
                'date': self.required_info['date']
            }
            
        except Exception as e:
            print(f"\n❌ ERROR in Assistant Agent: {str(e)}")
            error_msg = "I apologize, but I encountered an error. Could you please rephrase your request?"
            return {
                'messages': [error_msg],
                'missing_info': True,
                'optional_info': self.optional_info.copy()
            }

    def _detect_search_modification(self, user_message: str) -> bool:
        """
        Detect if user is modifying a previous search.
        This logic NO LONGER resets the state. It just signals that
        a modification is happening so the Orchestrator knows to re-search.
        """
        if not self.last_search_completed:
            return False
            
        modification_keywords = [
            'change', 'modify', 'update', 'instead', 'different', 'another',
            'try', 'check', 'look for', 'search for', 'find', 'show me'
        ]
        
        # Check if any modification keyword is present
        has_modification_keyword = any(keyword in user_message for keyword in modification_keywords)
        
        # Check if new details (required or optional) are being specified
        has_new_details = (
            any(city in user_message for city in self.FLIGHT_CITIES) or
            any(company in user_message for company in self.FLIGHT_COMPANIES) or
            any(name in user_message for name in self.FLIGHT_NAMES_MAP) or
            bool(re.search(r'(\d{4}-\d{1,2}-\d{1,2})', user_message)) or # <--- FIX IS HERE TOO
            any(month in user_message for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']) or
            bool(re.search(r'([A-Z]{2,3}\d{3})', user_message.upper()))
        )
        
        # If new details or keywords are found, signal a modification.
        # We DO NOT reset the state here.
        if has_modification_keyword or has_new_details:
            print(f"🔄 Search modification/filter detected. State will be updated, not reset.")
            return True
            
        return False

    def _build_llm_context(self) -> str:
        """Build context for LLM about current state"""
        context = "Current conversation context:\n"
        
        if self.required_info['source']:
            context += f"- Source city: {self.required_info['source'].title()}\n"
        if self.required_info['destination']:
            context += f"- Destination city: {self.required_info['destination'].title()}\n"
        if self.required_info['date']:
            context += f"- Travel date: {self.required_info['date']}\n"
        if self.optional_info['company']:
            context += f"- Preferred airline: {self.optional_info['company'].title()}\n"
        if self.optional_info['flight_number']:
            context += f"- Flight number: {self.optional_info['flight_number']}\n"
        
        missing = self._check_missing_info()
        if missing:
            context += f"\nStill need: {', '.join(missing)}\n"
        
        return context

    def _update_history(self, user_msg: str, assistant_msg: str):
        """Update conversation history for LLM"""
        self.conversation_history.append({"role": "user", "content": user_msg})
        self.conversation_history.append({"role": "assistant", "content": assistant_msg})
        
        # Keep only last 10 exchanges to avoid context overflow
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def _extract_flight_details(self, user_input: str) -> Tuple[Optional[str], Optional[str], Optional[str], Dict[str, Optional[str]]]:
        """Extract source, destination, date and optional flight details from natural language input"""
        user_input_lower = user_input.lower()
        
        source = None
        destination = None
        date = None
        flight_number = None
        flight_name = None
        company = None
        
        # Extract flight number (format: XXXnnn)
        flight_number_match = re.search(r'(?:flight\s+(?:number\s+)?|flight\s*#?\s*|number\s+)([A-Z]{2,3}\d{3})', user_input.upper())
        if flight_number_match:
            flight_number = flight_number_match.group(1)
            print(f" 	→ Found flight number: {flight_number}")
        
        # Extract company
        company_match = re.search(r'(?:by|with|company\s+(?:is|should\s+be))\s+([A-Za-z\s]+)', user_input_lower)
        if company_match:
            potential_company = company_match.group(1).strip()
            if potential_company in self.FLIGHT_COMPANIES:
                company = potential_company
                print(f" 	→ Found company: {company}")
        
        if not company:
            for comp in self.FLIGHT_COMPANIES:
                if comp in user_input_lower:
                    company = comp
                    print(f" 	→ Found company: {company}")
                    break
        
        # Extract flight name
        for name, associated_company in self.FLIGHT_NAMES_MAP.items():
            if name in user_input_lower:
                flight_name = name
                if not company:
                    company = associated_company
                print(f" 	→ Found flight name: {flight_name} (company: {company})")
                break
        
        # Extract cities - Pattern 1: "from X to Y"
        match = re.search(r'from\s+(\w+)\s+to\s+(\w+)', user_input_lower)
        if match:
            src, dst = match.group(1), match.group(2)
            if src in self.FLIGHT_CITIES:
                source = src
                print(f" 	→ Found source (from-to): {source}")
            if dst in self.FLIGHT_CITIES:
                destination = dst
                print(f" 	→ Found destination (from-to): {destination}")
        
        # Pattern 2: "X to Y" (without 'from')
        if not (source and destination): # Only run if we don't have both
            match = re.search(r'(\w+)\s+to\s+(\w+)', user_input_lower)
            if match:
                src, dst = match.group(1), match.group(2)
                if src in self.FLIGHT_CITIES and not source:
                    source = src
                    print(f" 	→ Found source (to): {source}")
                if dst in self.FLIGHT_CITIES and not destination:
                    destination = dst
                    print(f" 	→ Found destination (to): {destination}")

        # Pattern 3: "to Y" (destination only)
        if not destination:
             match = re.search(r'to\s+(\w+)', user_input_lower)
             if match and match.group(1) in self.FLIGHT_CITIES:
                 destination = match.group(1)
                 print(f" 	→ Found destination (to Y): {destination}")

        # Pattern 4: "from X" (source only)
        if not source:
             match = re.search(r'from\s+(\w+)', user_input_lower)
             if match and match.group(1) in self.FLIGHT_CITIES:
                 source = match.group(1)
                 print(f" 	→ Found source (from X): {source}")

        # Pattern 5: Individual cities (if still missing)
        if not source or not destination:
            found_cities = [city for city in self.FLIGHT_CITIES if city in user_input_lower]
            if len(found_cities) == 1:
                # If one city found, and we still need a source, assume it's the source
                if not source and 'from' in user_input_lower:
                     source = found_cities[0]
                     print(f" 	→ Found source (single city): {source}")
                # If one city found, and we still need a dest, assume it's the dest
                elif not destination:
                     destination = found_cities[0]
                     print(f" 	→ Found destination (single city): {destination}")

        
        # =================================================================
        #
        # ⬇️ *** START OF DATE REGEX FIX *** ⬇️
        #
        # =================================================================

        # Date extraction: YYYY-MM-DD format
        # FIX: Use \d{1,2} to match non-zero-padded month/day (e.g., 2025-2-10)
        date_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', user_input)
        if date_match:
            try:
                date_str = date_match.group(1)
                # Parse the potentially non-padded date
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # FIX: Re-format it as a zero-padded string to match API/dummy data
                date = date_obj.strftime('%Y-%m-%d')
                print(f" 	→ Found date: {date} (normalized from {date_str})")
            except ValueError:
                pass # Invalid date like 2025-2-30
        
        # =================================================================
        #
        # ⬆️ *** END OF DATE REGEX FIX *** ⬆️
        #
        # =================================================================

        
        # Month name patterns
        if not date:
            months = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12'
            }
            
            # Create a single regex pattern string from all month keys
            month_pattern_string = '|'.join(months.keys())
            
            # Match "Month Day"
            pattern_month_day = rf'on\s+({month_pattern_string})\s+(\d{{1,2}})'
            match_month_day = re.search(pattern_month_day, user_input_lower)
            
            if match_month_day:
                month_name = match_month_day.group(1)
                day = match_month_day.group(2).zfill(2)
                date = f"2025-{months[month_name]}-{day}" # Hardcoding 2025 for demo
                print(f" 	→ Found date (month name): {date}")
            else:
                 # Match "Day of Month"
                pattern_day_month = rf'on\s+(\d{{1,2}})(?:st|nd|rd|th)?\s+of\s+({month_pattern_string})'
                match_day_month = re.search(pattern_day_month, user_input_lower)
                
                if match_day_month:
                    day = match_day_month.group(1).zfill(2)
                    month_name = match_day_month.group(2)
                    date = f"2025-{months[month_name]}-{day}" # Hardcoding 2025 for demo
                    print(f" 	→ Found date (day of month): {date}")

        optional_info = {
            'flight_number': flight_number,
            'flight_name': flight_name,
            'company': company
        }
        return source, destination, date, optional_info

    def _check_missing_info(self) -> List[str]:
        """Check what information is still needed"""
        missing = []
        if not self.required_info['source']:
            missing.append('source city')
        if not self.required_info['destination']:
            missing.append('destination city')
        if not self.required_info['date']:
            missing.append('date (YYYY-MM-DD)')
        return missing

    def _create_search_message(self) -> str:
        """Create a search message including all search criteria"""
        search_msg = f"Searching for flights from {self.required_info['source'].title()} to {self.required_info['destination'].title()} on {self.required_info['date']}"
        
        optional_constraints = []
        if self.optional_info['flight_number']:
            optional_constraints.append(f"Flight #{self.optional_info['flight_number']}")
        if self.optional_info['company']:
            optional_constraints.append(f"operated by {self.optional_info['company'].title()}")
        if self.optional_info['flight_name']:
            optional_constraints.append(f"name '{self.optional_info['flight_name']}'")
        
        if optional_constraints:
            search_msg += f" ({' | '.join(optional_constraints)})"
            
        return search_msg

    def reset(self) -> None:
        """Reset the conversation state"""
        print("\n🔄 Resetting Assistant Agent state")
        self.required_info = {'source': None, 'destination': None, 'date': None}
        self.optional_info = {'flight_number': None, 'flight_name': None, 'company': None}
        self.conversation_history = []
        self.last_search_completed = False