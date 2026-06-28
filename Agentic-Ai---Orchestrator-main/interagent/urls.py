from django.urls import path
from . import views
from .agents.search_agent import display_all_api_data

# Display all API data at startup
print("\n" + "="*100)
print("🚀 STARTING INTERAGENT FLIGHT BOOKING SYSTEM")
print("="*100)
display_all_api_data()

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/chat/history/', views.chat_history, name='chat_history'),
    path('api/chat/monitoring/', views.toggle_monitoring, name='toggle_monitoring'),
    path('admin/chats/', views.admin_chat_view, name='admin_chat_view'),
]