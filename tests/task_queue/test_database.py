import pytest
import sqlite3
from datetime import datetime
from sokrates.task_queue.database import TaskQueueDatabase

# Test setup: Create a temporary in-memory database for all tests
@pytest.fixture(scope="function")
def db():
    """Fixture to create and clean up a fresh in-memory database instance."""
    db = TaskQueueDatabase(":memory:")
    yield db
    db.close()

def test_database_initialization(db):
    """Verify the database initializes with tables created without errors."""
    # Check if tasks table exists by querying sqlite_master
    cursor = db.connection().cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    assert cursor.fetchone() is not None, "Tasks table was not created"
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_history'")
    assert cursor.fetchone() is not None, "Task history table was not created"

def test_add_task_success(db):
    """Test adding a new task successfully."""
    db.add_task(
        task_id="test1",
        description="Test task",
        file_path="/path/to/file"
    )
    
    # Verify the task exists in the database
    tasks = db.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0]["task_id"] == "test1"
    assert tasks[0]["description"] == "Test task"
    assert tasks[0]["file_path"] == "/path/to/file"
    assert tasks[0]["priority"] == "normal"
    assert tasks[0]["status"] == "pending"

def test_add_task_duplicate_raises_error(db):
    """Test adding a duplicate task_id raises ValueError."""
    db.add_task("duplicate", "test", "/path/to/file")
    
    with pytest.raises(ValueError, match="Task already exists"):
        db.add_task("duplicate", "another desc", "/path/to/another")

def test_get_all_tasks(db):
    """Verify get_all_tasks returns all tasks including non-pending."""
    # Add multiple tasks in different states
    db.add_task("task1", "Pending task", "/file1")
    db.update_task_status("task1", "processing")
    
    db.add_task("task2", "Completed task", "/file2")
    db.update_task_status("task2", "completed", result="success")
    
    all_tasks = db.get_all_tasks()
    assert len(all_tasks) == 2
    # Verify both tasks are returned regardless of status

def test_get_pending_tasks(db):
    """Verify get_pending_tasks only returns pending tasks."""
    # Add a task in pending state and one not pending
    db.add_task("pending", "Pending task", "/file1")
    db.update_task_status("pending", "processing")  # Now it's processing
    
    db.add_task("still_pending", "Still pending", "/file2")
    
    pending_tasks = db.get_pending_tasks()
    assert len(pending_tasks) == 1
    assert pending_tasks[0]["task_id"] == "still_pending"
    assert pending_tasks[0]["status"] == "pending"

def test_update_task_status(db):
    """Test updating task status and history logging."""
    # Add a new task to update
    db.add_task("update_test", "Update test", "/file")
    
    # Update status to 'processing'
    db.update_task_status("update_test", "processing")
    
    # Verify tasks table was updated
    updated_task = db.get_all_tasks()[0]
    assert updated_task["status"] == "processing"
    assert updated_task["updated_at"] is not None
    
    # Verify history entry exists
    cursor = db.connection().cursor()
    cursor.execute("SELECT * FROM task_history WHERE task_id='update_test'")
    history_entries = cursor.fetchall()
    assert len(history_entries) == 1
    assert history_entries[0]["status"] == "processing"

def test_update_task_with_result_error(db):
    """Test updating with result and error messages."""
    db.add_task("result_test", "Result test", "/file")
    
    # Update with success result
    db.update_task_status(
        task_id="result_test",
        status="completed",
        result="Success!"
    )
    
    # Verify result was stored correctly
    updated_task = db.get_all_tasks()[0]
    assert updated_task["status"] == "completed"
    assert updated_task["result"] == "Success!"
    assert updated_task["error_message"] is None
    
    # Update with error message
    db.update_task_status(
        task_id="result_test",
        status="failed",
        error="File not found"
    )
    
    updated_task = db.get_all_tasks()[0]
    assert updated_task["status"] == "failed"
    assert updated_task["error_message"] == "File not found"

def test_close_connection(db):
    """Test that closing the connection works without errors."""
    # Verify connection was open initially
    assert db.conn is not None
    
    # Close and verify it's set to None
    db.close()
    assert db.conn is None

def test_get_all_tasks_limit(db):
    """Test get_all_tasks with limit parameter."""
    for i in range(5):
        db.add_task(f"task_{i}", f"Task {i}", f"/file_{i}")
    
    # Get first 3 tasks
    limited_tasks = db.get_all_tasks(limit=3)
    assert len(limited_tasks) == 3
    
    # Verify only the first 3 are returned
    for i in range(3):
        assert limited_tasks[i]["task_id"] == f"task_{i}"

def test_update_task_status_with_nulls(db):
    """Test updating with None values for result/error."""
    db.add_task("null_test", "Null test", "/file")
    
    # Update without providing result/error
    db.update_task_status("null_test", "processing")
    
    updated_task = db.get_all_tasks()[0]
    assert updated_task["result"] is None
    assert updated_task["error_message"] is None