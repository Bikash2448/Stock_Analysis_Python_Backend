from fastapi import FastAPI
from app.api.v1.nifty import router as nifty_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Indian Stock Market API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173","http://127.0.0.1:4001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nifty_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Stock API is running"}