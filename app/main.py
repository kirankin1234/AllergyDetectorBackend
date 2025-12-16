from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.allergen_controller import router as allergen_router
from app.controllers.scan_controller import router as scan_router

app = FastAPI(title="Allergy Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(allergen_router, prefix="/api")
app.include_router(scan_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Allergy Detector API"}
