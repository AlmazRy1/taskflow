import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

from sqlalchemy.orm import Session
from .models import TaskModel
from .database import Base, engine
import tasks_pb2
import uuid
from datetime import datetime

Base.metadata.create_all(bind=engine)

def model_to_proto(m: TaskModel):
    return tasks_pb2.Task(
        id=m.id,
        title=m.title,
        description=m.description or "",
        status=m.status,
        priority=m.priority,
        completed=m.completed,
        created_at=m.created_at.isoformat() if m.created_at else "",
        updated_at=m.updated_at.isoformat() if m.updated_at else "",
    )

class TaskServiceImpl:
    def __init__(self, db_factory):
        self.db_factory = db_factory

    def CreateTask(self, request, context):
        db: Session = self.db_factory()
        try:
            task = TaskModel(
                id=str(uuid.uuid4()),
                title=request.title,
                description=request.description,
                status=request.status if request.status != 0 else 1,
                priority=request.priority if request.priority != 0 else 2,
                completed=False,
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return model_to_proto(task)
        finally:
            db.close()

    def GetTask(self, request, context):
        db = self.db_factory()
        try:
            task = db.query(TaskModel).filter(TaskModel.id == request.id).first()
            if not task:
                context.set_code(5)
                context.set_details("Task not found")
                return tasks_pb2.Task()
            return model_to_proto(task)
        finally:
            db.close()

    def ListTasks(self, request, context):
        db = self.db_factory()
        try:
            q = db.query(TaskModel)
            if request.status_filter != 0:
                q = q.filter(TaskModel.status == request.status_filter)
            if not request.include_completed:
                q = q.filter(TaskModel.completed == False)
            tasks = q.order_by(TaskModel.created_at.desc()).all()
            return tasks_pb2.ListTasksResponse(tasks=[model_to_proto(t) for t in tasks])
        finally:
            db.close()

    def UpdateTask(self, request, context):
        db = self.db_factory()
        try:
            task = db.query(TaskModel).filter(TaskModel.id == request.id).first()
            if not task:
                context.set_code(5)
                context.set_details("Task not found")
                return tasks_pb2.Task()
            if request.title:
                task.title = request.title
            if request.description:
                task.description = request.description
            if request.status != 0:
                task.status = request.status
            if request.priority != 0:
                task.priority = request.priority
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
            return model_to_proto(task)
        finally:
            db.close()

    def DeleteTask(self, request, context):
        db = self.db_factory()
        try:
            task = db.query(TaskModel).filter(TaskModel.id == request.id).first()
            if not task:
                return tasks_pb2.DeleteTaskResponse(success=False)
            db.delete(task)
            db.commit()
            return tasks_pb2.DeleteTaskResponse(success=True)
        finally:
            db.close()

    def ToggleComplete(self, request, context):
        db = self.db_factory()
        try:
            task = db.query(TaskModel).filter(TaskModel.id == request.id).first()
            if not task:
                context.set_code(5)
                context.set_details("Task not found")
                return tasks_pb2.Task()
            task.completed = not task.completed
            task.status = 3 if task.completed else 1
            db.commit()
            db.refresh(task)
            return model_to_proto(task)
        finally:
            db.close()
