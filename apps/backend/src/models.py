from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
import uuid
from .database import Base

class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, default="")
    status = Column(Integer, default=1)  # TODO=1
    priority = Column(Integer, default=2) # MEDIUM=2
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
