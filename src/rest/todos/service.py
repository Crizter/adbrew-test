from typing import Any, List

from rest.errors import InvalidInputError
from todos.repository import Todo, TodoRepository

MAX_DESCRIPTION_LENGTH = 500


class TodoService:
    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def list_todos(self) -> List[Todo]:
        return self._repository.list_all()

    def create_todo(self, description: Any) -> Todo:
        return self._repository.create(self._validate_description(description))

    @staticmethod
    def _validate_description(description: Any) -> str:
        if not isinstance(description, str) or not description.strip():
            raise InvalidInputError("description is required")

        description = description.strip()
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise InvalidInputError(f"description must be at most {MAX_DESCRIPTION_LENGTH} characters")
        return description
