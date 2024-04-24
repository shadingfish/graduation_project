from django.urls import path
from . import views
from .views import QueryView

urlpatterns = [
    path("", QueryView.as_view(), name="query-page"),
    path("chatbot/", views.chatbot, name="chatbot-page"),
    path("path-to-query-neo4j-view/", views.query_neo4j, name="query-neo4j"),
]
