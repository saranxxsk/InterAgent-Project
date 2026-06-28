from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import json
import xml.etree.ElementTree as ET

# Sample flight data
json_flights_data = {
    "flights": [
        {"flight_no": "AI101", "flight_name": "Delhi Express", "company": "Air India", "date": "2025-11-10", "remaining_seats": 45, "source": "Delhi", "destination": "Mumbai", "price": 4500},
        {"flight_no": "6E202", "flight_name": "Indigo Swift", "company": "IndiGo", "date": "2025-11-10", "remaining_seats": 32, "source": "Delhi", "destination": "Mumbai", "price": 3800},
        {"flight_no": "AI111", "flight_name": "Chennai Express", "company": "Air India", "date": "2025-11-12", "remaining_seats": 30, "source": "Delhi", "destination": "Chennai", "price": 5000},
    ]
}

xml_flights_data = """<?xml version="1.0" encoding="UTF-8"?>
<flights>
    <flight>
        <flight_no>XML001</flight_no>
        <flight_name>XML Airliner 1</flight_name>
        <company>XML Airways</company>
        <date>2025-11-11</date>
        <remaining_seats>21</remaining_seats>
        <source>Mumbai</source>
        <destination>Chennai</destination>
        <price>3125</price>
    </flight>
    <flight>
        <flight_no>XML002</flight_no>
        <flight_name>XML Airliner 2</flight_name>
        <company>XML Airways</company>
        <date>2025-11-11</date>
        <remaining_seats>22</remaining_seats>
        <source>Delhi</source>
        <destination>Bangalore</destination>
        <price>3150</price>
    </flight>
    <flight>
        <flight_no>XML003</flight_no>
        <flight_name>XML Airliner 3</flight_name>
        <company>XML Airways</company>
        <date>2025-11-12</date>
        <remaining_seats>23</remaining_seats>
        <source>Mumbai</source>
        <destination>Bangalore</destination>
        <price>3175</price>
    </flight>
    <flight>
        <flight_no>XML004</flight_no>
        <flight_name>XML Airliner 4</flight_name>
        <company>XML Airways</company>
        <date>2025-11-12</date>
        <remaining_seats>24</remaining_seats>
        <source>Delhi</source>
        <destination>Chennai</destination>
        <price>3200</price>
    </flight>
    <flight>
        <flight_no>XML005</flight_no>
        <flight_name>XML Airliner 5</flight_name>
        <company>XML Airways</company>
        <date>2025-11-13</date>
        <remaining_seats>25</remaining_seats>
        <source>Mumbai</source>
        <destination>Delhi</destination>
        <price>3225</price>
    </flight>
    <flight>
        <flight_no>XML006</flight_no>
        <flight_name>XML Airliner 6</flight_name>
        <company>XML Airways</company>
        <date>2025-11-13</date>
        <remaining_seats>26</remaining_seats>
        <source>Chennai</source>
        <destination>Mumbai</destination>
        <price>3250</price>
    </flight>
    <flight>
        <flight_no>XML007</flight_no>
        <flight_name>XML Airliner 7</flight_name>
        <company>XML Airways</company>
        <date>2025-11-14</date>
        <remaining_seats>27</remaining_seats>
        <source>Bangalore</source>
        <destination>Delhi</destination>
        <price>3275</price>
    </flight>
    <flight>
        <flight_no>XML008</flight_no>
        <flight_name>XML Airliner 8</flight_name>
        <company>XML Airways</company>
        <date>2025-11-14</date>
        <remaining_seats>28</remaining_seats>
        <source>Chennai</source>
        <destination>Bangalore</destination>
        <price>3300</price>
    </flight>
    <flight>
        <flight_no>XML009</flight_no>
        <flight_name>XML Airliner 9</flight_name>
        <company>XML Airways</company>
        <date>2025-11-15</date>
        <remaining_seats>29</remaining_seats>
        <source>Delhi</source>
        <destination>Mumbai</destination>
        <price>3325</price>
    </flight>
    <flight>
        <flight_no>XML010</flight_no>
        <flight_name>XML Airliner 10</flight_name>
        <company>XML Airways</company>
        <date>2025-11-15</date>
        <remaining_seats>30</remaining_seats>
        <source>Bangalore</source>
        <destination>Chennai</destination>
        <price>3350</price>
    </flight>
</flights>"""

soap_flights_data = """<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:flight="http://flightservice.example.com">
  <soap:Body>
    <flight:GetFlightsResponse>
      <flight:Flight>
        <flight:FlightNo>SOAP001</flight:FlightNo>
        <flight:FlightName>SOAP Express 1</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-11</flight:Date>
        <flight:RemainingSeats>26</flight:RemainingSeats>
        <flight:Source>Bangalore</flight:Source>
        <flight:Destination>Goa</flight:Destination>
        <flight:Price>2930</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP002</flight:FlightNo>
        <flight:FlightName>SOAP Express 2</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-11</flight:Date>
        <flight:RemainingSeats>27</flight:RemainingSeats>
        <flight:Source>Delhi</flight:Source>
        <flight:Destination>Chennai</flight:Destination>
        <flight:Price>2960</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP003</flight:FlightNo>
        <flight:FlightName>SOAP Express 3</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-12</flight:Date>
        <flight:RemainingSeats>28</flight:RemainingSeats>
        <flight:Source>Goa</flight:Source>
        <flight:Destination>Mumbai</flight:Destination>
        <flight:Price>2990</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP004</flight:FlightNo>
        <flight:FlightName>SOAP Express 4</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-12</flight:Date>
        <flight:RemainingSeats>29</flight:RemainingSeats>
        <flight:Source>Chennai</flight:Source>
        <flight:Destination>Delhi</flight:Destination>
        <flight:Price>3020</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP005</flight:FlightNo>
        <flight:FlightName>SOAP Express 5</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-13</flight:Date>
        <flight:RemainingSeats>30</flight:RemainingSeats>
        <flight:Source>Mumbai</flight:Source>
        <flight:Destination>Bangalore</flight:Destination>
        <flight:Price>3050</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP006</flight:FlightNo>
        <flight:FlightName>SOAP Express 6</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-13</flight:Date>
        <flight:RemainingSeats>31</flight:RemainingSeats>
        <flight:Source>Delhi</flight:Source>
        <flight:Destination>Goa</flight:Destination>
        <flight:Price>3080</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP007</flight:FlightNo>
        <flight:FlightName>SOAP Express 7</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-14</flight:Date>
        <flight:RemainingSeats>32</flight:RemainingSeats>
        <flight:Source>Bangalore</flight:Source>
        <flight:Destination>Chennai</flight:Destination>
        <flight:Price>3110</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP008</flight:FlightNo>
        <flight:FlightName>SOAP Express 8</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-14</flight:Date>
        <flight:RemainingSeats>33</flight:RemainingSeats>
        <flight:Source>Goa</flight:Source>
        <flight:Destination>Delhi</flight:Destination>
        <flight:Price>3140</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP009</flight:FlightNo>
        <flight:FlightName>SOAP Express 9</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-15</flight:Date>
        <flight:RemainingSeats>34</flight:RemainingSeats>
        <flight:Source>Chennai</flight:Source>
        <flight:Destination>Mumbai</flight:Destination>
        <flight:Price>3170</flight:Price>
      </flight:Flight>
      <flight:Flight>
        <flight:FlightNo>SOAP010</flight:FlightNo>
        <flight:FlightName>SOAP Express 10</flight:FlightName>
        <flight:Company>SOAP Airways</flight:Company>
        <flight:Date>2025-11-15</flight:Date>
        <flight:RemainingSeats>35</flight:RemainingSeats>
        <flight:Source>Mumbai</flight:Source>
        <flight:Destination>Goa</flight:Destination>
        <flight:Price>3200</flight:Price>
      </flight:Flight>
    </flight:GetFlightsResponse>
  </soap:Body>
</soap:Envelope>
"""

@require_http_methods(["GET"])
def json_flights(request):
    """Return flights in JSON format"""
    return JsonResponse(json_flights_data)

@require_http_methods(["GET"])
def xml_flights(request):
    """Return flights in XML format"""
    return HttpResponse(xml_flights_data, content_type='application/xml')

@require_http_methods(["GET"])
def soap_flights(request):
    """Return flights in SOAP format"""
    return HttpResponse(soap_flights_data, content_type='application/xml')