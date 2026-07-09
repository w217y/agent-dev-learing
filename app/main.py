import uvicorn


from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from app.api.routes_chat import router as chat_router
from app.api.routes_extract import router as extract_router


app = FastAPI(title="Agent Dev Week 1 API")

app.include_router(chat_router)
app.include_router(extract_router)

@app.exception_handler(RuntimeError)
async def runtime_exception_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )

@app.get("/health")
async def health_check():
    return {"status":"ok"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=6002,
        reload=False
    )