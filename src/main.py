from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from pydantic import BaseModel
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import src.api as api
from src.config import settings

#######################
#     APPLICATION     #
#######################


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = aioredis.from_url(
        f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True,
    )
    yield
    await app.state.redis.close()


app = FastAPI(title="REST Crypto Converter", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_backend_cors_origins(settings.BACKEND_CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.conversion_router, prefix="/api", tags=["conversion"])


#######################
#     EXCEPTIONS      #
#######################


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    error_cls = exc.__class__.__name__
    if settings.DEBUG:
        return JSONResponse({"detail": f"Internal Error ({error_cls}): {exc}"}, 500)
    else:
        return JSONResponse({"detail": f"Internal Error (500)"}, 500)


#######################
#     HEALTHCHECK     #
#######################


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def healthcheck() -> HealthCheck:
    """
    Endpoint to perform a healthcheck on. This endpoint can be used by Docker
    to ensure that robust container orchestration and management is in place.
    Other services which rely on proper functioning of the API service will not
    deploy if this endpoint returns any other HTTP status code except 200 (OK).
    """
    return HealthCheck(status="OK")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
