"""Backend entry point"""
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from .api.router import api_router
from .configuration import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# static files with generated client app
app.mount("/client", StaticFiles(directory="client"), name="client")

app.include_router(api_router)


@app.get("/health")
def health():
    """
    Health check
    :return:
    """
    return "OK"
