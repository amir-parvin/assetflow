from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, accounts, transactions, investments, gold, reports, zakat

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(investments.router)
app.include_router(gold.router)
app.include_router(reports.router)
app.include_router(zakat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
