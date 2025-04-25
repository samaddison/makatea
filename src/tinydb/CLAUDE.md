# TinyRepo

## Overview
TinyRepo is a generic wrapper around TinyDB tables that provides type-safe operations for storing and retrieving Pydantic models.

## Features
- Generic typing with Pydantic models
- Automatic timestamps for all stored objects
- Filtering by date ranges
- Statistical operations (count, sum, average)
- Time-based record expiration
- Thread-safe operations
- Size-limited collections with automatic pruning

## Usage

### Initialization
```python
from tinydb import TinyDB
from src.tinydb.tiny_repo import TinyRepo
from your_app import YourPydanticModel

# Create a TinyDB instance
db = TinyDB("path/to/db.json")  # Or use MemoryStorage for testing

# Create a repository for your model
repo = TinyRepo[YourPydanticModel](
    db=db,
    table_name="your_models",
    model=YourPydanticModel
)

# Create a size-limited repository (keeps only the most recent N items)
limited_repo = TinyRepo[YourPydanticModel](
    db=db,
    table_name="limited_models",
    model=YourPydanticModel,
    max_size=100  # Will automatically remove oldest items when exceeding this limit
)
```

### Basic Operations

#### Adding Items
```python
# Add an item to the repository
model = YourPydanticModel(field1="value", field2=123)
doc_id = repo.add(model)  # Returns the document ID
```

#### Retrieving Items
```python
# Get all items
all_items = repo.get_all()  # Returns List[YourPydanticModel]

# Filter items by a condition
filtered_items = repo.filter(lambda x: x.field2 > 100)

# Get the most recently added item
latest_item = repo.get_most_recent()  # Returns the most recent item or None if empty
```

### Statistical Operations

```python
# Count items
total_count = repo.count()
filtered_count = repo.count(lambda x: x.field1 == "value")

# Sum a field across items
total_sum = repo.sum("field2")
filtered_sum = repo.sum("field2", lambda x: x.field1 == "value")

# Calculate average of a field
avg_value = repo.avg("field2")
filtered_avg = repo.avg("field2", lambda x: x.field1 == "value")
```

### Time-Based Operations

Items are automatically timestamped with a `created_at` field when added.

```python
from datetime import datetime, timedelta, timezone

# Filter by date range
now = datetime.now(timezone.utc)
yesterday = now - timedelta(days=1)
items = repo.filter_by_date_range(yesterday, now)

# Get field values within a date range
values = repo.get_field_values_by_date_range("field2", yesterday, now)

# Delete old records
repo.delete_older_than_x_minutes(60)  # Deletes records older than 1 hour
```

## Implementation Details

### Timestamp Management
Each document is automatically timestamped with an ISO-formatted UTC datetime string in the `created_at` field. This enables filtering and retrieval by time ranges.

### Type Safety
The repository is generic over a type parameter `T` that must be a Pydantic model. This ensures type safety when adding and retrieving items from the database.

### Data Transformation
- When adding items: Pydantic models are converted to dictionaries using `model_dump()`
- When retrieving items: Dictionary documents are converted back to Pydantic models using `model_validate()`

### Deletion Strategy
The `delete_older_than_x_minutes` method uses a predicate function to identify and remove records that are older than the specified time threshold.

### Size Limitation
When initialized with a `max_size` parameter, the repository automatically manages the number of items:
- When adding a new item that would exceed the limit, the oldest item (based on created_at timestamp) is automatically removed
- This creates a "sliding window" of the most recent N items
- Useful for maintaining time-series data with a fixed storage budget

### Thread Safety
The TinyRepo class is completely thread-safe:
- All operations are protected by an internal reentrant lock
- Multiple threads can safely call any repository methods concurrently
- Thread safety is implemented as an internal detail - clients don't need to add their own synchronization
- Locking is optimized to minimize contention:
  - The lock scope is kept as narrow as possible
  - Some operations release the lock while processing data to improve concurrency
  - Care is taken to avoid nested lock acquisition that could cause deadlocks