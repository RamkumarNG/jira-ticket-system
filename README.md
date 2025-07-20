# 🚀 Jira Ticket System

A modern, async, and production-ready ticket management system inspired by Jira, built with FastAPI, SQLAlchemy, and PostgreSQL.

---

## 🌟 Features

- **Async FastAPI** backend for high performance
- **PostgreSQL** with async SQLAlchemy ORM
- **User, Ticket, Project, and Comment** APIs
- **JWT/API Key Authentication** middleware
- **Robust Alembic migrations**
- **Pydantic** models for type-safe validation
- **Modular, scalable architecture**
- **OpenAPI/Swagger** docs at `/docs`
- **Dockerized** for easy deployment
- **Weather microservice** integration (OpenWeather API)
- **Learning notes** and SQLAlchemy relationship/eager loading cheat sheets

---

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **FastAPI**
- **SQLAlchemy (async)**
- **Alembic**
- **PostgreSQL**
- **Pydantic**
- **Docker**
- **Render.com** (cloud deployment)

---

## 🌐 Deployment

This project is **deployed on [Render](https://render.com/)** and accessible at:

- **API Docs:** [https://jira-ticket-system.onrender.com/docs](https://jira-ticket-system.onrender.com/docs)

> **Note:**
> The backend is hosted on Render’s free tier, which may cause the service to sleep when idle.
> If the API is not immediately responsive, please wait 1–2 minutes after your first request for it to fully

---



## 📚 API Highlights

- **User APIs**: Register, update, list, delete, fetch by email/ID
- **Ticket APIs**: Create, update, delete, list, filter by project/user/title
- **Comment APIs**: Add, update, delete, list comments on tickets
- **Weather Service**: Example microservice integration
- **Authentication**: API key required for all endpoints (see `.env`)

---

## 🧠 Developer Notes

- **Async SQLAlchemy**: Uses `AsyncSession`, `create_async_engine`, and async relationships.
- **Eager Loading**: Optimized queries with `joinedload`, `selectinload` ([learn/SQLAlchemy_eager_loading.md](learn/SQLAlchemy_eager_loading.md)).
- **Relationship Modeling**: One-to-many, many-to-many, one-to-one ([learn/SQLAlchemy_relationship_cheatsheet.md](learn/SQLAlchemy_relationship_cheatsheet.md)).
- **Extensible**: Add new services, models, or routers with minimal boilerplate.

---

## 🚀 Deployment

- **Render.com**: Ready-to-deploy with [render.yaml](render.yaml)
- **Docker**: Production-ready Dockerfile and start script

---


## 🚦 Quick Start

1. **Clone & Setup**

   ```sh
   git clone https://github.com/yourusername/jira-ticket-system.git
   cd jira-ticket-system
   cp app/.env.example app/.env  # Edit with your DB/API keys
   ```
2. **Run with Docker**

   ```sh
   docker build -t jira-ticket-system .
   docker run -p 10000:10000 --env-file app/.env jira-ticket-system
   ```
3. **API Docs**

   - Visit [http://localhost:10000/docs
     ](http://localhost:10000/docs)

---



## 📝 Learning Resources

- [learn/SQLAlchemy_eager_loading.md](learn/SQLAlchemy_eager_loading.md)
- [learn/SQLAlchemy_relationship_cheatsheet.md](learn/SQLAlchemy_relationship_cheatsheet.md)
- [learn/things_learned.txt](learn/things_learned.txt)
- [learn/things_to_learn.txt](learn/things_to_learn.txt)

---

## 🤝 Contributing

PRs and issues welcome!
