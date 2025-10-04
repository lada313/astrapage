from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.imports import router as import_router
from app.api.v1.segments import router as segments_router
from app.api.v1.exports import router as export_router

app = FastAPI(title="CRM Shop")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"ok": True}

app.include_router(import_router, prefix="/api/v1/import", tags=["import"])
app.include_router(segments_router, prefix="/api/v1/segments", tags=["segments"])
app.include_router(export_router, prefix="/api/v1/export", tags=["export"])
