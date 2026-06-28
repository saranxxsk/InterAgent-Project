from typing import Dict, List, Any

def decision_agent(current_state: dict) -> dict:
    """Analyze search results and provide recommendations"""
    print("\n[⚖️ Decision Agent]")
    print("📥 Analyzing search results...")
    
    flights = current_state.get('search_results', [])
    
    if not flights:
        msg = ("Unfortunately, no flights are available for your search criteria. "
               "Try different dates or routes.")
        current_state['messages'].append(msg)
        print(f"❌ {msg}")
        return current_state
    
    # Sort by price (cheapest first)
    sorted_flights = sorted(flights, key=lambda x: x['price'])
    top_5 = sorted_flights[:5]
    
    # Display recommendations
    print("\n📋 TOP RECOMMENDATIONS (by price)")
    print(f"{'Rank':<6}{'Flight':<12}{'Company':<15}{'Price':<10}{'Seats':<8}{'API'}")
    print("-" * 55)
    
    for i, flight in enumerate(top_5, 1):
        print(f"{i:<6}{flight['flight_no']:<12}{flight['company']:<15}"
              f"₹{flight['price']:<9}{flight['remaining_seats']:<8}{flight['api_source']}")
    
    # Create recommendation message
    best_flight = top_5[0]
    msg = (
        f"Best option is {best_flight['company']} flight {best_flight['flight_no']} "
        f"at ₹{best_flight['price']} (Source: {best_flight['api_source']} API). "
        f"{best_flight['remaining_seats']} seats remaining."
    )
    
    current_state['messages'].append(msg)
    current_state['final_recommendations'] = top_5
    
    print(f"\n💬 {msg}")
    return current_state