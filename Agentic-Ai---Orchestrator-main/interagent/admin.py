from django.contrib import admin
from .models import ChatLog, ChatMonitoring, AgentRegistry

@admin.register(AgentRegistry)
class AgentRegistryAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'name', 'endpoint', 'last_seen')
    search_fields = ('agent_id', 'name', 'endpoint')
    list_filter = ('last_seen',)

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'timestamp', 'message')
    list_filter = ('user', 'sender', 'timestamp')
    search_fields = ('user__username', 'message', 'sender')
    date_hierarchy = 'timestamp'

@admin.register(ChatMonitoring)
class ChatMonitoringAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'monitoring_active')
    list_filter = ('user', 'start_time')
    search_fields = ('user__username',)
    date_hierarchy = 'start_time'

    def monitoring_active(self, obj):
        return obj.end_time is None
    monitoring_active.boolean = True
    monitoring_active.short_description = 'Active'
