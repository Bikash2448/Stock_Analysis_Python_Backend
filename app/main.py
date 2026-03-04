from fastapi import FastAPI
from app.api.v1.dashboard import dashboard_router
from app.api.v1.stock_router import stock_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Indian Stock Market API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173","http://127.0.0.1:4001","http://localhost:4001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router, prefix="/api")
app.include_router(stock_router,prefix="/api/chart")

@app.get("/")
def root():
    return {"message": "Stock API is running"}