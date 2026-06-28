from django.urls import path

from .flight_api import json_flights, xml_flights, soap_flights
from .agent_registry_api import register_agent, list_agents

urlpatterns = [
    path('flights/json/', json_flights, name='json_flights'),
    path('flights/xml/', xml_flights, name='xml_flights'),
    path('flights/soap/', soap_flights, name='soap_flights'),
    path('agents/register/', register_agent, name='register_agent'),
    path('agents/', list_agents, name='list_agents'),
]