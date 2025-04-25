from typing import TypeVar, Generic, Type, Callable, Optional, List, Any
from pydantic import BaseModel
from tinydb import TinyDB, Query
from tinydb.table import Table
from datetime import datetime, timedelta, timezone
import dateutil.parser  # pip install python-dateutil

T = TypeVar("T", bound=BaseModel)


class TinyRepo(Generic[T]):
    def __init__(self, db: TinyDB, table_name: str, model: Type[T]):
        self.table: Table = db.table(table_name)
        self.model = model
        self.query = Query()

    def add(self, item: T) -> int:
        data = item.model_dump()
        data["created_at"] = datetime.now(timezone.utc).isoformat()
        return self.table.insert(data)

    def get_all(self) -> List[T]:
        return [self.model.model_validate(doc) for doc in self.table.all()]

    def filter(self, condition: Callable[[T], bool]) -> List[T]:
        return [item for item in self.get_all() if condition(item)]

    def count(self, condition: Optional[Callable[[T], bool]] = None) -> int:
        return len(self.filter(condition)) if condition else len(self.table)

    def sum(self, field: str, condition: Optional[Callable[[T], bool]] = None) -> float:
        items = self.filter(condition) if condition else self.get_all()
        return sum(getattr(item, field) for item in items)

    def avg(self, field: str, condition: Optional[Callable[[T], bool]] = None) -> float:
        items = self.filter(condition) if condition else self.get_all()
        return self.sum(field, lambda x: True) / len(items) if items else 0.0

    def filter_by_date_range(self, start: datetime, end: datetime) -> List[T]:
        def in_range(doc) -> bool:
            created = dateutil.parser.isoparse(doc["created_at"])
            return start <= created <= end

        return [
            self.model.model_validate(doc)
            for doc in self.table.all()
            if "created_at" in doc and in_range(doc)
        ]

    def get_field_values(self, field: str) -> List[Any]:
        return [getattr(item, field) for item in self.get_all() if hasattr(item, field)]

    def get_field_values_by_date_range(
        self, field: str, start: datetime, end: datetime
    ) -> List[Any]:
        def in_range(doc) -> bool:
            created = dateutil.parser.isoparse(doc["created_at"])
            return start <= created <= end

        return [
            doc[field]
            for doc in self.table.all()
            if "created_at" in doc and field in doc and in_range(doc)
        ]

    def delete_older_than_x_minutes(self, minutes: int) -> None:
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        def is_old_record(record):
            if "created_at" not in record:
                return False
            created_at = dateutil.parser.isoparse(record["created_at"])
            return created_at < cutoff_time

        deleted_count = len(self.table.search(is_old_record))
        self.table.remove(is_old_record)
        print(f"Deleted {deleted_count} records older than {minutes} minutes.")
