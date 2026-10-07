from django.urls import include, path

urlpatterns = [
    path("", include("todos.urls")),
]
