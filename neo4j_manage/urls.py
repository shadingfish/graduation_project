from django.urls import path
from .views import (
    CropView,
    FetchAndUpdateView,
    UpdateNeo4jView,
    CropUpdateView,
    CropDeleteView,
)

urlpatterns = [
    path("", CropView.as_view(), name="neo4j-manage"),
    path("fetch_and_update/", FetchAndUpdateView.as_view(), name="fetch-and-update"),
    path("update_neo4j/", UpdateNeo4jView.as_view(), name="update-neo4j"),
    path("crop/update/<str:latin_name>/", CropUpdateView.as_view(), name="crop_update"),
    path("crop/delete/<str:latin_name>/", CropDeleteView.as_view(), name="crop_delete"),
]
