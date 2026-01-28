from peewee import *
import datetime

# Create database instance - will be initialized with path
db = SqliteDatabase(None)

class BaseModel(Model):
    """Base model class for all Peewee models"""
    class Meta:
        database = db

class Task(BaseModel):
    task_id = AutoField(primary_key=True, unique=True)
    description = TextField(null=False)
    file_path = TextField(null=False)
    priority = CharField(default='normal')  # Can be 'low', 'normal', 'high'
    status = CharField(default='pending')   # Can be 'pending', 'in_progress', 'completed', 'failed'
    created_at = DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    result = TextField(null=True)
    output_directory = TextField(null=True)
    error_message = TextField(null=True)

class TaskHistory(BaseModel):
    history_id = AutoField(primary_key=True)
    task = ForeignKeyField(Task, backref='history', null=False)
    status = CharField(null=False)  # Can be 'pending', 'in_progress', 'completed', 'failed'
    changed_at = DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    result = TextField(null=True)
    error_message = TextField(null=True)