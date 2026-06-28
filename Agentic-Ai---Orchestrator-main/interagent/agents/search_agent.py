import json
import xml.etree.ElementTree as ET
import requests
from typing import Dict, Any

# API endpoints
API_BASE_URL = "http://localhost:8000/api"
JSON_API_URL = f"{API_BASE_URL}/flights/json/"
XML_API_URL = f"{API_BASE_URL}/flights/xml/"
SOAP_API_URL = f"{API_BASE_URL}/flights/soap/"


# =================================================================
# FUNCTION: DISPLAY ALL API DATA AT STARTUP (REAL FETCH)
# =================================================================
def display_all_api_data():
    """Fetch and display all flight data from the three real API endpoints."""
    print("\n" + "=" * 100)
    print("📊 STARTUP: DISPLAYING LIVE DATA FROM ALL APIs")
    print("=" * 100)

    try:
        # JSON API
        print("\n" + "🔵 JSON API DATA".center(100, "="))
        json_response = requests.get(JSON_API_URL)
        json_response.raise_for_status()
        json_flights_data = json_response.json()
        json_flights = json_flights_data.get("flights", [])
        print(f"\nTotal Flights: {len(json_flights)}\n")
        print(f"{'Flight No':<12}{'Name':<20}{'Company':<15}{'Date':<12}{'Source':<10}{'Destination':<12}{'Price':<10}{'Seats'}")
        print("-" * 100)
        for flight in json_flights:
            print(f"{flight['flight_no']:<12}{flight['flight_name']:<20}{flight['company']:<15}"
                  f"{flight['date']:<12}{flight['source']:<10}{flight['destination']:<12}"
                  f"₹{flight['price']:<9}{flight['remaining_seats']}")
    except Exception as e:
        print(f"✗ Error fetching JSON API: {e}")

    # XML API
    try:
        print("\n" + "🟢 XML API DATA (Raw)".center(100, "="))
        xml_response = requests.get(XML_API_URL)
        xml_response.raise_for_status()
        xml_data = xml_response.text
        print(xml_data)
    except Exception as e:
        print(f"✗ Error fetching XML API: {e}")

    # SOAP API
    try:
        print("\n" + "🟡 SOAP API DATA (Raw)".center(100, "="))
        soap_response = requests.get(SOAP_API_URL)
        soap_response.raise_for_status()
        soap_data = soap_response.text
        print(soap_data)
    except Exception as e:
        print(f"✗ Error fetching SOAP API: {e}")

    print("\n" + "=" * 100)
    print("📈 LIVE API SUMMARY")
    print("=" * 100)
    try:
        xml_root = ET.fromstring(xml_data)
        soap_root = ET.fromstring(soap_data)
        ns = {'flight': 'http://flightservice.example.com'}
        print(f" 	JSON API: 	{len(json_flights)} flights")
        print(f" 	XML API: 	 {len(xml_root.findall('flight'))} flights")
        print(f" 	SOAP API: 	{len(soap_root.findall('.//flight:Flight', ns))} flights")
    except Exception:
        print("⚠️ Could not count flights due to parse error.")
    print("=" * 100 + "\n")


# =================================================================
# FUNCTION: SEARCH AGENT (REAL ENDPOINT FETCH + FILTER)
# =================================================================
def search_agent(current_state: dict) -> dict:
    """
    Fetch from all APIs and filter results based on criteria.
    Sends the filtered raw data to Orchestrator.
    """
    print("\n" + "=" * 80)
    print("[🔍 Search Agent: Starting Search]")
    print("=" * 80)
    print(f"📥 Received search request for {current_state['source']} → {current_state['destination']} on {current_state['date']}")

    if current_state.get('missing_info'):
        print("❌ Missing required information. Skipping search.")
        return {'json_results': [], 'xml_results': [], 'soap_results': []}

    src = current_state['source']
    dst = current_state['destination']
    date = current_state['date']
    optional_info = current_state.get('optional_info', {})

    print("\n[🔄 Starting API Filtering]")
    filtered_raw_json, filtered_raw_xml, filtered_raw_soap = [], [], []

    # --- JSON API ---
    try:
        print(f"\n 	→ Fetching and filtering JSON API data... ({JSON_API_URL})")
        response = requests.get(JSON_API_URL)
        response.raise_for_status()
        flights_json = response.json().get("flights", [])

        for flight in flights_json:
            if (flight['source'].lower() == src.lower() and
                flight['destination'].lower() == dst.lower() and
                flight['date'] == date):

                if optional_info.get('flight_number') and flight['flight_no'] != optional_info['flight_number']:
                    continue
                if optional_info.get('flight_name') and flight['flight_name'].lower() != optional_info['flight_name'].lower():
                    continue
                if optional_info.get('company') and flight['company'].lower() != optional_info['company'].lower():
                    continue

                filtered_raw_json.append(flight)

        print(f" 	 	✓ Found {len(filtered_raw_json)} matching JSON flights.")
        print(" 	 	RAW FILTERED JSON:\n", json.dumps(filtered_raw_json, indent=2))
        print(" 	 	[➡️ 	Sending raw JSON to Orchestrator...]")
    except Exception as e:
        print(f" 	 	✗ JSON API Error: {e}")

    # --- XML API ---
    try:
        print(f"\n 	→ Fetching and filtering XML API data... ({XML_API_URL})")
        response = requests.get(XML_API_URL)
        response.raise_for_status()
        xml_root = ET.fromstring(response.text)

        for f in xml_root.findall('flight'):
            if (f.find('source').text.lower() == src.lower() and
                f.find('destination').text.lower() == dst.lower() and
                f.find('date').text == date):

                if optional_info.get('flight_number') and f.find('flight_no').text != optional_info['flight_number']:
                    continue
                if optional_info.get('flight_name') and f.find('flight_name').text.lower() != optional_info['flight_name'].lower():
                    continue
                if optional_info.get('company') and f.find('company').text.lower() != optional_info['company'].lower():
                    continue

                filtered_raw_xml.append(f)

        print(f" 	 	✓ Found {len(filtered_raw_xml)} matching XML flights.")
        print(" 	 	RAW FILTERED XML:\n", [ET.tostring(el, encoding='unicode').strip() for el in filtered_raw_xml])
        print(" 	 	[➡️ 	Sending raw XML to Orchestrator...]")
    except Exception as e:
        print(f" 	 	✗ XML API Error: {e}")

    # --- SOAP API ---
    try:
        print(f"\n 	→ Fetching and filtering SOAP API data... ({SOAP_API_URL})")
        response = requests.get(SOAP_API_URL)
        response.raise_for_status()
        soap_root = ET.fromstring(response.text)
        ns = {'flight': 'http://flightservice.example.com'}

        for f in soap_root.findall('.//flight:Flight', ns):
            if (f.find('flight:Source', ns).text.lower() == src.lower() and
                f.find('flight:Destination', ns).text.lower() == dst.lower() and
                f.find('flight:Date', ns).text == date):

                if optional_info.get('flight_number') and f.find('flight:FlightNo', ns).text != optional_info['flight_number']:
                    continue
                if optional_info.get('flight_name') and f.find('flight:FlightName', ns).text.lower() != optional_info['flight_name'].lower():
                    continue
                if optional_info.get('company') and f.find('flight:Company', ns).text.lower() != optional_info['company'].lower():
                    continue

                filtered_raw_soap.append(f)

        print(f" 	 	✓ Found {len(filtered_raw_soap)} matching SOAP flights.")
        print(" 	 	RAW FILTERED SOAP:\n", [ET.tostring(el, encoding='unicode').strip() for el in filtered_raw_soap])
        print(" 	 	[➡️ 	Sending raw SOAP to Orchestrator...]")
    except Exception as e:
        print(f" 	 	✗ SOAP API Error: {e}")

    print("=" * 80)
    print("[🔍 Search Agent: Filtering Complete]")
    print("=" * 80)

    return {
        'json_results': filtered_raw_json,
        'xml_results': filtered_raw_xml,
        'soap_results': filtered_raw_soap
    }
