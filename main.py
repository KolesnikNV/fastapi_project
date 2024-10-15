import uvicorn
from fastapi import FastAPI

from src.settings import settings
from src.users.routers import router as user_router

app = FastAPI(
    title="FastAPI",
    description="FastAPI",
    version="0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/api",
)
app.include_router(user_router)


def main():
    """
    Main function.
    Start server with uvicorn.
    """

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=int(settings.PORT),
        log_level="info",
        reload=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Сервер останволен")
