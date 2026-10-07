from collections.abc import Mapping

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest.errors import InvalidInputError
from rest.mongo import get_database
from todos.repository import TodoRepository
from todos.service import TodoService

TODOS_COLLECTION = "todos"


def build_todo_service() -> TodoService:
    return TodoService(TodoRepository(get_database()[TODOS_COLLECTION]))


class TodoListView(APIView):
    service_factory = staticmethod(build_todo_service)

    def get(self, request):
        todos = self.service_factory().list_todos()
        return Response([todo.to_dict() for todo in todos])

    def post(self, request):
        if not isinstance(request.data, Mapping):
            raise InvalidInputError("Request body must be a JSON object")

        todo = self.service_factory().create_todo(request.data.get("description"))
        return Response(todo.to_dict(), status=status.HTTP_201_CREATED)
