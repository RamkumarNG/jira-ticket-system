import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.api.v1 import api_router
from app.core.database.databases import engine, async_session
from app.core.database.models import mapper_registry
from app.middleware import authentication, logging as loggingMiddleware
from app.utils.project import create_default_project
from app.utils.user import create_default_user

logging.basicConfig(
    level=logging.INFO,   # Set log level to INFO to allow all levels above it
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Customize log format
)
log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (e.g., test DB connection and check table exists)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(mapper_registry.metadata.create_all)
        
        async with async_session() as session:
            await create_default_user(session)
            await create_default_project(session)
        
        log.info("✅ Database connection test successfully")
    except Exception as e:
        log.error(f"❌ Database connection failed: {e}")
        raise

    yield  # Application runs here

    # Shutdown logic
    await engine.dispose()
    log.info("🛑 Database engine disposed")


app = FastAPI(
    title='Jira Ticket APIs',
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",  
    lifespan=lifespan
)

app.add_middleware(authentication.AuthenticationMiddleware)
app.add_middleware(loggingMiddleware.LoggingMiddleware)
cors_headers = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-api-key",
    "x-requested-with",
    "x-correlation-id",
    "x-resolution-id",
    "x-cache-key"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=cors_headers,
)


app.include_router(api_router, prefix='/api')

@app.get("/health_ping")
@app.get("/ping")
async def ping():
    return {"message": "pong"}
