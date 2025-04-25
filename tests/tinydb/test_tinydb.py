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


@pytest.fixture
def limited_repo():
    db = TinyDB(storage=MemoryStorage)
    return TinyRepo[Item](db=db, table_name="limited_items", model=Item, max_size=3)


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


def test_max_size_limit(limited_repo):
    # Add items up to the limit
    limited_repo.add(Item(name="A", value=10))
    limited_repo.add(Item(name="B", value=20))
    limited_repo.add(Item(name="C", value=30))

    assert limited_repo.count() == 3

    # Names of items should be A, B, C
    items = limited_repo.get_all()
    item_names = [item.name for item in items]
    assert sorted(item_names) == ["A", "B", "C"]

    # Add one more item, which should cause the oldest to be removed
    limited_repo.add(Item(name="D", value=40))

    # Count should still be 3 (max_size)
    assert limited_repo.count() == 3

    # The oldest item (A) should have been removed
    items = limited_repo.get_all()
    item_names = [item.name for item in items]
    assert "A" not in item_names
    assert sorted(item_names) == ["B", "C", "D"]


def test_max_size_with_backdated_items(limited_repo):
    # Add three items with the middle one backdated to be the oldest
    limited_repo.add(Item(name="A", value=10))

    # Add B but backdate it to be the oldest
    b_id = limited_repo.add(Item(name="B", value=20))
    record = limited_repo.table.get(doc_id=b_id)
    record["created_at"] = (
        datetime.now(timezone.utc) - timedelta(minutes=10)
    ).isoformat()
    limited_repo.table.update(record, doc_ids=[b_id])

    limited_repo.add(Item(name="C", value=30))

    # Add a fourth item, which should cause B (the oldest) to be removed
    limited_repo.add(Item(name="D", value=40))

    # Check that B was removed
    items = limited_repo.get_all()
    item_names = [item.name for item in items]
    assert "B" not in item_names
    assert sorted(item_names) == ["A", "C", "D"]


def test_thread_safety(repo):
    import threading
    import time
    import random

    # Number of items to add from each thread
    n_items = 20
    # Number of threads
    n_threads = 5

    # Track errors that might occur in threads
    errors = []

    def add_items(thread_id):
        try:
            for i in range(n_items):
                # Add items with thread-specific names
                repo.add(Item(name=f"Thread-{thread_id}-Item-{i}", value=i))
                # Small random delay to increase chances of thread interleaving
                if random.random() < 0.3:
                    time.sleep(0.001)
        except Exception as e:
            errors.append(f"Error in thread {thread_id}: {str(e)}")

    # Create and start threads
    threads = []
    for i in range(n_threads):
        t = threading.Thread(target=add_items, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Check for errors
    assert not errors, f"Thread errors occurred: {errors}"

    # Verify all items were added correctly
    all_items = repo.get_all()
    assert len(all_items) == n_items * n_threads

    # Check that each thread's items are present
    for thread_id in range(n_threads):
        for i in range(n_items):
            item_name = f"Thread-{thread_id}-Item-{i}"
            matching_items = [item for item in all_items if item.name == item_name]
            assert len(matching_items) == 1, f"Item {item_name} not found or duplicated"
            assert matching_items[0].value == i
