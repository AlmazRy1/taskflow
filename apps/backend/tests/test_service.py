import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/generated'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import tasks_pb2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import TaskModel
from src.service import TaskServiceImpl

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)

class DummyContext:
    def set_code(self, c): self.code=c
    def set_details(self, d): self.details=d

def get_service():
    return TaskServiceImpl(db_factory=SessionLocal)

def test_create_and_list():
    svc = get_service()
    ctx = DummyContext()
    req = tasks_pb2.CreateTaskRequest(title="Test task", description="desc", status=1, priority=3)
    task = svc.CreateTask(req, ctx)
    assert task.id != ""
    assert task.title == "Test task"
    assert task.priority == 3

    list_resp = svc.ListTasks(tasks_pb2.ListTasksRequest(include_completed=True), ctx)
    assert len(list_resp.tasks) >= 1
    assert any(t.title == "Test task" for t in list_resp.tasks)

def test_toggle_complete():
    svc = get_service()
    ctx = DummyContext()
    task = svc.CreateTask(tasks_pb2.CreateTaskRequest(title="Toggle me"), ctx)
    assert task.completed == False
    toggled = svc.ToggleComplete(tasks_pb2.ToggleCompleteRequest(id=task.id), ctx)
    assert toggled.completed == True
    assert toggled.status == 3
    toggled2 = svc.ToggleComplete(tasks_pb2.ToggleCompleteRequest(id=task.id), ctx)
    assert toggled2.completed == False

def test_update_and_delete():
    svc = get_service()
    ctx = DummyContext()
    task = svc.CreateTask(tasks_pb2.CreateTaskRequest(title="To delete"), ctx)
    updated = svc.UpdateTask(tasks_pb2.UpdateTaskRequest(id=task.id, title="Updated title", status=2), ctx)
    assert updated.title == "Updated title"
    assert updated.status == 2

    del_resp = svc.DeleteTask(tasks_pb2.DeleteTaskRequest(id=task.id), ctx)
    assert del_resp.success == True

    fetched = svc.GetTask(tasks_pb2.GetTaskRequest(id=task.id), ctx)
    assert ctx.code == 5  # NOT_FOUND
