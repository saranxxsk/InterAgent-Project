from django.db import models
from django.contrib.auth.models import User

class AgentRegistry(models.Model):
    agent_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    endpoint = models.URLField()
    capabilities = models.JSONField(default=list)
    auth_token = models.CharField(max_length=200, blank=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.agent_id})"

class ChatMonitoring(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Monitoring for {self.user.username} from {self.start_time}"
        
    class Meta:
        get_latest_by = 'start_time'

class ChatLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.CharField(max_length=50)  # 'user', 'assistant', 'search', 'decision'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    monitoring_session = models.ForeignKey(ChatMonitoring, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.sender} to {self.user.username} at {self.timestamp}"

class FlightSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date = models.DateField()
    search_results = models.JSONField(null=True, blank=True)
    recommendations = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} to {self.destination} on {self.date}"
