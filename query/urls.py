from django.urls import path
from . import views

urlpatterns = [
    path("", views.query_page, name="query-page"),
    path("chatbot/", views.chatbot, name="chatbot-page"),
    path("path-to-query-neo4j-view/", views.query_neo4j, name="query-neo4j"),
]
