from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .database import Base, SessionLocal, engine
from .routers.media import router as media_router
from .routers.tweets import router as tweets_router
from .routers.users import router as users_router
from .seed import seed_users

STATIC_DIRECTORY = Path("app/static")
MEDIA_DIRECTORY = Path("app/media")


@asynccontextmanager
async def lifespan(app: FastAPI):
    MEDIA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        seed_users(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="Corporate Microblogging Service",
    description="Backend сервиса корпоративных микроблогов",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    tweets_router,
    prefix="/api/tweets",
    tags=["Tweets"],
)

app.include_router(
    users_router,
    prefix="/api/users",
    tags=["Users"],
)

app.include_router(
    media_router,
    prefix="/api/medias",
    tags=["Media"],
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIRECTORY)),
    name="static",
)

app.mount(
    "/css",
    StaticFiles(directory=str(STATIC_DIRECTORY / "css")),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=str(STATIC_DIRECTORY / "js")),
    name="js",
)

app.mount(
    "/media",
    StaticFiles(directory=str(MEDIA_DIRECTORY)),
    name="media",
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": "HTTPException",
            "error_message": str(exc.detail),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "result": False,
            "error_type": "ValidationError",
            "error_message": "Invalid request data",
        },
    )


@app.get(
    "/",
    include_in_schema=False,
)
def serve_index() -> FileResponse:
    return FileResponse("app/static/index.html")
