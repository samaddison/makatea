from typing import Any, TypeVar, Generic, Type, Callable, Optional, List
from pydantic import BaseModel
from tinydb import TinyDB, Query
from tinydb.table import Table
from datetime import datetime, timedelta, timezone
import dateutil.parser  # pip install python-dateutil

T = TypeVar('T', bound=BaseModel)

class TinyRepo(Generic[T]):
    def __init__(self, db: TinyDB, table_name: str, model: Type[T]):
        self.table: Table = db.table(table_name)
        self.model = model
        self.query = Query()

    def add(self, item: T) -> int:
        data = item.model_dump() 
        data['created_at'] = datetime.utcnow().isoformat()  # Add timestamp
        return self.table.insert(data)

    def get_all(self) -> List[T]:
        return [self.model.parse_obj(doc) for doc in self.table.all()]

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
            created = dateutil.parser.isoparse(doc['created_at'])
            return start <= created <= end
        return [self.model.model_validate(doc) for doc in self.table.all() if 'created_at' in doc and in_range(doc)]

    def get_field_values(self, field: str) -> List[Any]:
        return [getattr(item, field) for item in self.get_all() if hasattr(item, field)]
    
    def delete_older_than_x_minutes(self, minutes: int) -> None:
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)  # Timezone-aware
        records_to_delete = [doc for doc in self.table.all() if 'created_at' in doc and 
                             dateutil.parser.isoparse(doc['created_at']) < cutoff_time]
        
        # Delete the records
        for record in records_to_delete:
            self.table.remove(doc_ids=[self.table.all().index(record)])
        print(f"Deleted {len(records_to_delete)} records older than {minutes} minutes.")


"""
from pydantic import BaseModel
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from datetime import datetime, timedelta

class User(BaseModel):
    name: str
    age: int

db = TinyDB(storage=MemoryStorage)
user_repo = TinyRepo(db, 'users', User)

# Add users
user_repo.add(User(name="Alice", age=30))
user_repo.add(User(name="Bob", age=25))

# Filter by date
now = datetime.utcnow()
past = now - timedelta(minutes=5)
future = now + timedelta(minutes=5)

recent_users = user_repo.filter_by_date_range(past, future)
print("Users added recently:", recent_users)

"""