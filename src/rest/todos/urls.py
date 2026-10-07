from django.urls import re_path

from todos.views import TodoListView

urlpatterns = [
    re_path(r"^todos/?$", TodoListView.as_view(), name="todo-list"),
]
