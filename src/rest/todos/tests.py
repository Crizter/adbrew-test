from datetime import datetime, timezone
from unittest.mock import MagicMock

from bson import ObjectId
from django.test import SimpleTestCase
from pymongo.errors import ServerSelectionTimeoutError
from rest_framework.test import APIClient

from rest.errors import InvalidInputError
from todos.repository import Todo, TodoRepository
from todos.service import MAX_DESCRIPTION_LENGTH, TodoService
from todos.views import TodoListView

CREATED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)


class InMemoryTodoRepository:
    def __init__(self):
        self.todos = []

    def list_all(self):
        return list(reversed(self.todos))

    def create(self, description):
        todo = Todo(id=str(len(self.todos) + 1), description=description, created_at=CREATED_AT)
        self.todos.append(todo)
        return todo


class TodoServiceTests(SimpleTestCase):
    def setUp(self):
        self.repository = InMemoryTodoRepository()
        self.service = TodoService(self.repository)

    def test_create_trims_and_persists_description(self):
        todo = self.service.create_todo("  Learn Docker  ")

        self.assertEqual(todo.description, "Learn Docker")
        self.assertEqual(self.repository.todos, [todo])

    def test_create_rejects_invalid_descriptions(self):
        for description in [None, "", "   ", 42, "x" * (MAX_DESCRIPTION_LENGTH + 1)]:
            with self.subTest(description=description), self.assertRaises(InvalidInputError):
                self.service.create_todo(description)

        self.assertEqual(self.repository.todos, [])

    def test_list_returns_newest_first(self):
        self.service.create_todo("first")
        self.service.create_todo("second")

        self.assertEqual([t.description for t in self.service.list_todos()], ["second", "first"])


class TodoRepositoryTests(SimpleTestCase):
    def test_create_returns_todo_with_string_id(self):
        collection = MagicMock()
        inserted_id = ObjectId()
        collection.insert_one.return_value.inserted_id = inserted_id

        todo = TodoRepository(collection).create("Learn Mongo")

        self.assertEqual(todo.id, str(inserted_id))
        self.assertEqual(todo.description, "Learn Mongo")

    def test_list_all_maps_documents_to_todos(self):
        collection = MagicMock()
        document = {"_id": ObjectId(), "description": "Learn Mongo", "created_at": CREATED_AT}
        collection.find.return_value.sort.return_value = [document]

        todos = TodoRepository(collection).list_all()

        self.assertEqual(todos, [Todo(id=str(document["_id"]), description="Learn Mongo", created_at=CREATED_AT)])


class TodoListViewTests(SimpleTestCase):
    def setUp(self):
        self.repository = InMemoryTodoRepository()
        self.client = APIClient()
        original_factory = TodoListView.service_factory
        TodoListView.service_factory = staticmethod(lambda: TodoService(self.repository))
        self.addCleanup(setattr, TodoListView, "service_factory", original_factory)

    def test_post_creates_todo(self):
        response = self.client.post("/todos", {"description": "Learn React"}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["description"], "Learn React")

    def test_get_lists_todos(self):
        self.repository.create("Learn React")

        response = self.client.get("/todos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([t["description"] for t in response.json()], ["Learn React"])

    def test_post_with_invalid_description_returns_400(self):
        response = self.client.post("/todos", {"description": " "}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "description is required"})

    def test_post_with_non_object_body_returns_400(self):
        response = self.client.post("/todos", ["Learn React"], format="json")

        self.assertEqual(response.status_code, 400)

    def test_database_error_returns_503(self):
        failing_service = MagicMock()
        failing_service.list_todos.side_effect = ServerSelectionTimeoutError("mongo down")
        TodoListView.service_factory = staticmethod(lambda: failing_service)

        with self.assertLogs("rest.errors", level="ERROR"):
            response = self.client.get("/todos")

        self.assertEqual(response.status_code, 503)
        self.assertIn("error", response.json())
