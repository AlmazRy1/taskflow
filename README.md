# TaskFlow - gRPC + SQLAlchemy + React + moonrepo

Monorepo с moon.

## Stack
- Backend: Python, gRPC, SQLAlchemy (SQLite), pytest
- Frontend: TypeScript, React, Vite, @improbable-eng/grpc-web, Vitest
- Proto: proto/tasks.proto
- Orchestration: moonrepo

## Структура
```
apps/backend - Python gRPC server
apps/frontend - React client
proto/tasks.proto - контракт
```

## Запуск (требуется moon, python3.11, node20)

moon run backend:install
moon run backend:generate  # генерирует python gRPC код из proto
moon run backend:run  # :50051 gRPC, :8000 HTTP bridge для web

в другом терминале:
moon run frontend:install
moon run frontend:dev  # http://localhost:5173

## Тесты
moon run backend:test
moon run frontend:test
moon run :test  # все сразу
```

Проект: TaskFlow - CRUD для задач с статусами, приоритетами, фильтрами.
