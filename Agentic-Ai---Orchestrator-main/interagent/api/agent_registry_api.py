from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json
from interagent.models import AgentRegistry

@csrf_exempt
def register_agent(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        name = data.get('name')
        endpoint = data.get('endpoint')
        capabilities = data.get('capabilities', [])
        auth_token = data.get('auth_token', '')
        if not agent_id or not name or not endpoint:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        _, created = AgentRegistry.objects.update_or_create(
            agent_id=agent_id,
            defaults={
                'name': name,
                'endpoint': endpoint,
                'capabilities': capabilities,
                'auth_token': auth_token,
                'last_seen': timezone.now()
            }
        )
        print(f"[🌐 Agent Registry] Registered agent: {name}")
        return JsonResponse({'status': 'success', 'message': 'Agent registered', 'created': created})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def list_agents(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    agents = AgentRegistry.objects.all()
    agent_list = [
        {
            'agent_id': a.agent_id,
            'name': a.name,
            'endpoint': a.endpoint,
            'capabilities': a.capabilities,
            'last_seen': a.last_seen
        } for a in agents
    ]
    print(f"[🔎 Agent Registry] Found {len(agent_list)} available agents")
    return JsonResponse({'status': 'success', 'agents': agent_list})
