from fastapi import Header, HTTPException
from config import settings

async def verify_api_key(x_api_key: str = Header(..., alias="x-api-key")):
    """
    Dependency that validates the header. 
    Using '...' makes the header required.
    """
    if x_api_key != settings.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key