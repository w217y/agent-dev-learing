import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse

from app.db.init_db import init_db
from app.api.routes_chat import router as chat_router
from app.api.routes_extract import router as extract_router
from app.api.routes_tools import router as tools_router
from app.api.routes_documents import router as documents_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Agent Dev RAG API",
              lifespan=lifespan,
              )


@app.exception_handler(RuntimeError)
async def runtime_exception_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )

@app.get("/health")
async def health_check():
    return {"status":"ok"}




app.include_router(chat_router)
app.include_router(extract_router)
app.include_router(tools_router)
app.include_router(documents_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=6002,
        reload=False
    )