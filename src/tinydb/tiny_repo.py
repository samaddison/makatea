from typing import TypeVar, Generic, Type, Callable, Optional, List, Any
from pydantic import BaseModel
from tinydb import TinyDB, Query
from tinydb.table import Table
from datetime import datetime, timedelta, timezone
import dateutil.parser  # pip install python-dateutil
import threading

T = TypeVar("T", bound=BaseModel)


class TinyRepo(Generic[T]):
    def __init__(
        self,
        db: TinyDB,
        table_name: str,
        model: Type[T],
        max_size: Optional[int] = None,
    ):
        """Initialize a new TinyRepo instance.

        Args:
            db: The TinyDB database instance
            table_name: The name of the table to use
            model: The Pydantic model class
            max_size: Optional maximum number of items to store (default: None, no limit)
        """
        self.table: Table = db.table(table_name)
        self.model = model
        self.query = Query()
        self.max_size = max_size
        self._lock = threading.RLock()  # Use RLock for reentrant locking

    def add(self, item: T) -> int:
        """Add an item to the repository.

        If a max_size is set and the table would exceed this size,
        the oldest item (by created_at timestamp) will be removed first.

        Args:
            item: The item to add

        Returns:
            The document ID of the inserted item
        """
        with self._lock:
            # Check if we need to remove an old record to make room
            if self.max_size is not None and len(self.table) >= self.max_size:
                self._remove_oldest_record()

            data = item.model_dump()
            data["created_at"] = datetime.now(timezone.utc).isoformat()
            return self.table.insert(data)

    def _remove_oldest_record(self) -> None:
        """Remove the oldest record based on created_at timestamp."""
        # Note: This is an internal method called from add() which already holds the lock,
        # so we don't need to acquire the lock again here.
        if len(self.table) == 0:
            return

        # Find the oldest record based on created_at timestamp
        def is_oldest(record):
            """Query function to identify the oldest record."""
            if len(self.table) <= 1:
                # If there's only one record, it's the oldest
                return True

            # Compare against all other records
            created_at = dateutil.parser.isoparse(record["created_at"])
            for doc in self.table.all():
                if doc != record and "created_at" in doc:
                    other_date = dateutil.parser.isoparse(doc["created_at"])
                    if other_date < created_at:
                        return False
            return True

        # Remove the oldest record directly using the query
        self.table.remove(is_oldest)

    def get_all(self) -> List[T]:
        with self._lock:
            return [self.model.model_validate(doc) for doc in self.table.all()]

    def filter(self, condition: Callable[[T], bool]) -> List[T]:
        with self._lock:
            # Get items while holding the lock to ensure a consistent snapshot
            docs = self.table.all()
            items = [self.model.model_validate(doc) for doc in docs]
        # Apply filter outside the lock to minimize lock time
        return [item for item in items if condition(item)]

    def count(self, condition: Optional[Callable[[T], bool]] = None) -> int:
        if condition:
            return len(self.filter(condition))
        else:
            with self._lock:
                return len(self.table)

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

        with self._lock:
            return [
                self.model.model_validate(doc)
                for doc in self.table.all()
                if "created_at" in doc and in_range(doc)
            ]

    def get_field_values(self, field: str) -> List[Any]:
        # get_all() already has a lock
        return [getattr(item, field) for item in self.get_all() if hasattr(item, field)]

    def get_field_values_by_date_range(
        self, field: str, start: datetime, end: datetime
    ) -> List[Any]:
        def in_range(doc) -> bool:
            created = dateutil.parser.isoparse(doc["created_at"])
            return start <= created <= end

        with self._lock:
            return [
                doc[field]
                for doc in self.table.all()
                if "created_at" in doc and field in doc and in_range(doc)
            ]

    def delete_older_than_x_minutes(self, minutes: int) -> None:
        with self._lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

            def is_old_record(record):
                if "created_at" not in record:
                    return False
                created_at = dateutil.parser.isoparse(record["created_at"])
                return created_at < cutoff_time

            deleted_count = len(self.table.search(is_old_record))
            self.table.remove(is_old_record)
            print(f"Deleted {deleted_count} records older than {minutes} minutes.")

    def get_most_recent(self) -> Optional[T]:
        """Get the most recently added item based on created_at timestamp.

        Returns:
            The most recently added item, or None if the repository is empty.
        """
        with self._lock:
            if len(self.table) == 0:
                return None

            docs = self.table.all()
            if not docs:
                return None

            # Find the record with the most recent created_at timestamp
            most_recent_doc = max(
                [doc for doc in docs if "created_at" in doc],
                key=lambda doc: dateutil.parser.isoparse(doc["created_at"]),
                default=None,
            )

            if most_recent_doc is None:
                return None

            return self.model.model_validate(most_recent_doc)
