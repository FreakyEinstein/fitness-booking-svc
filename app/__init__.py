from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
import traceback
import json
import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from .routes import router
from starlette.middleware.cors import CORSMiddleware

load_dotenv()


logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    try:
        body = await request.body()
        body_str = body.decode("utf-8", errors="replace")
    except Exception:
        body_str = "<could not decode body>"

    log_data = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": body_str,
        "error": repr(exc),
        "traceback": traceback.format_exc().splitlines()
    }

    logging.error(json.dumps(log_data, indent=2))

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )
