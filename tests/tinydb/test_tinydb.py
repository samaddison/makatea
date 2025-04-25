import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from src.tinydb.tiny_repo import TinyRepo


class Item(BaseModel):
    name: str
    value: int


@pytest.fixture
def repo():
    db = TinyDB(storage=MemoryStorage)
    return TinyRepo[Item](db=db, table_name="test_items", model=Item)


def test_add_and_get_all(repo):
    repo.add(Item(name="A", value=10))
    repo.add(Item(name="B", value=20))
    all_items = repo.get_all()
    assert len(all_items) == 2
    assert all_items[0].name == "A"
    assert all_items[1].value == 20


def test_count(repo):
    repo.add(Item(name="A", value=10))
    repo.add(Item(name="B", value=20))
    assert repo.count() == 2
    assert repo.count(lambda x: x.value > 10) == 1


def test_sum_and_avg(repo):
    repo.add(Item(name="A", value=10))
    repo.add(Item(name="B", value=30))
    assert repo.sum("value") == 40
    assert repo.avg("value") == 20


def test_filter_by_date_range(repo):
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(minutes=10)

    item1 = Item(name="A", value=10)
    item2 = Item(name="B", value=20)

    repo.add(item1)
    repo.add(item2)

    results = repo.filter_by_date_range(old_time, now + timedelta(seconds=1))
    assert len(results) == 2

    results = repo.filter_by_date_range(
        now + timedelta(seconds=1), now + timedelta(minutes=5)
    )
    assert len(results) == 0


def test_get_field_values(repo):
    repo.add(Item(name="A", value=10))
    repo.add(Item(name="B", value=20))
    values = repo.get_field_values("value")
    assert sorted(values) == [10, 20]


def test_get_field_values_by_date_range(repo):
    now = datetime.now(timezone.utc)
    repo.add(Item(name="A", value=10))
    repo.add(Item(name="B", value=20))

    start = now - timedelta(minutes=1)
    end = now + timedelta(minutes=1)

    values = repo.get_field_values_by_date_range("value", start, end)
    assert sorted(values) == [10, 20]


def test_delete_older_than_x_minutes(repo):
    repo.add(Item(name="A", value=10))
    repo.add(Item(name="B", value=20))

    # Manually backdate one record to simulate older entry
    record = repo.table.all()[0]
    record["created_at"] = (
        datetime.now(timezone.utc) - timedelta(minutes=5)
    ).isoformat()
    repo.table.update(record, doc_ids=[repo.table.all()[0].doc_id])

    repo.delete_older_than_x_minutes(3)
    assert repo.count() == 1
