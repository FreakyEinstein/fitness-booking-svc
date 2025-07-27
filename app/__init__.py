from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
import traceback
import json
import logging
from dotenv import load_dotenv
from .routes import router
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()


logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = FastAPI()


class RawBodyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.body = await request.body()

        async def receive():
            return {"type": "http.request", "body": request.state.body}
        request._receive = receive
        response = await call_next(request)
        return response


app.add_middleware(RawBodyMiddleware)

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
    # Use the raw body captured by middleware
    body = getattr(request.state, "body", None)
    try:
        if body is not None:
            try:
                body_json = json.loads(body)
                body_str = json.dumps(body_json, indent=2, ensure_ascii=False)
            except Exception:
                try:
                    decoded = body.decode("utf-8", errors="replace")
                    normalized = " ".join(decoded.split())
                    if len(normalized) > 500:
                        normalized = normalized[:500] + "... [truncated]"
                    body_str = normalized
                except Exception:
                    body_str = str(body)
        else:
            body_str = "<no body captured>"
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
