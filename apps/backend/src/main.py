import os, sys, time, threading
from concurrent import futures
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

import grpc
from sqlalchemy.orm import sessionmaker
from .database import engine, Base
from .models import TaskModel
from .service import TaskServiceImpl
import tasks_pb2_grpc

# Ensure generated exists
Base.metadata.create_all(bind=engine)

def serve_grpc():
    from .database import SessionLocal
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = TaskServiceImpl(db_factory=SessionLocal)
    tasks_pb2_grpc.add_TaskServiceServicer_to_server(service, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on :50051")
    return server

# Simple HTTP bridge for React frontend (to avoid needing Envoy for gRPC-Web)
def serve_http():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    from .database import SessionLocal
    from .service import model_to_proto
    from .models import TaskModel
    import tasks_pb2

    app = FastAPI(title="TaskFlow HTTP Bridge")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/api/tasks")
    def list_tasks(status_filter: int = 0, include_completed: bool = True):
        db = SessionLocal()
        try:
            q = db.query(TaskModel)
            if status_filter != 0:
                q = q.filter(TaskModel.status == status_filter)
            if not include_completed:
                q = q.filter(TaskModel.completed == False)
            tasks = q.order_by(TaskModel.created_at.desc()).all()
            return {"tasks": [{"id": t.id, "title": t.title, "description": t.description, "status": t.status, "priority": t.priority, "completed": t.completed, "created_at": t.created_at.isoformat()} for t in tasks]}
        finally:
            db.close()

    @app.post("/api/tasks")
    def create_task(payload: dict):
        db = SessionLocal()
        try:
            import uuid
            task = TaskModel(id=str(uuid.uuid4()), title=payload.get("title",""), description=payload.get("description",""), status=payload.get("status",1), priority=payload.get("priority",2))
            db.add(task); db.commit(); db.refresh(task)
            return {"id": task.id, "title": task.title, "description": task.description, "status": task.status, "priority": task.priority, "completed": task.completed}
        finally:
            db.close()

    @app.patch("/api/tasks/{task_id}/toggle")
    def toggle(task_id: str):
        db = SessionLocal()
        try:
            task = db.query(TaskModel).filter(TaskModel.id==task_id).first()
            if not task:
                return {"error": "not found"}
            task.completed = not task.completed
            task.status = 3 if task.completed else 1
            db.commit(); db.refresh(task)
            return {"id": task.id, "completed": task.completed, "status": task.status}
        finally:
            db.close()

    @app.delete("/api/tasks/{task_id}")
    def delete(task_id: str):
        db = SessionLocal()
        try:
            task = db.query(TaskModel).filter(TaskModel.id==task_id).first()
            if not task: return {"success": False}
            db.delete(task); db.commit()
            return {"success": True}
        finally:
            db.close()

    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    grpc_server = serve_grpc()
    # run http bridge in thread
    t = threading.Thread(target=serve_http, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        grpc_server.stop(0)
