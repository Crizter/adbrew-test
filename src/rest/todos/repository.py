from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from pymongo import DESCENDING
from pymongo.collection import Collection


@dataclass(frozen=True)
class Todo:
    id: str
    description: str
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


class TodoRepository:
    def __init__(self, collection: Collection):
        self._collection = collection

    def list_all(self) -> List[Todo]:
        documents = self._collection.find().sort("created_at", DESCENDING)
        return [self._to_todo(document) for document in documents]

    def create(self, description: str) -> Todo:
        now = datetime.now(timezone.utc)
        # Mongo stores datetimes with millisecond precision
        created_at = now.replace(microsecond=now.microsecond // 1000 * 1000)
        document = {"description": description, "created_at": created_at}
        result = self._collection.insert_one(document)
        return self._to_todo({**document, "_id": result.inserted_id})

    @staticmethod
    def _to_todo(document: dict) -> Todo:
        return Todo(
            id=str(document["_id"]),
            description=document["description"],
            created_at=document["created_at"],
        )
