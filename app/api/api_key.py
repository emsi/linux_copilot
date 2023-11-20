from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.security.api_key import APIKeyHeader
from app.configuration import api_keys

app = FastAPI()


security = APIKeyHeader(name="X-Api-Key")


def get_api_key(api_key: str = Depends(security)):
    """Get API key from header"""
    if api_key not in api_keys:
        raise HTTPException(status_code=400, detail="Invalid API Key")
    return api_key
