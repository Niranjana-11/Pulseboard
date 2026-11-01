from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from fastapi.responses import RedirectResponse


from app.database import engine
from app.routers import alerts, services, stats

app = FastAPI(title="PulseBoard API", version="0.1.0")

app.include_router(services.router)
app.include_router(alerts.router)
app.include_router(stats.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["health"])
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", "database": "up"}