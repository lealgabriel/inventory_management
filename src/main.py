from fastapi import FastAPI

from src import settings

app: FastAPI = FastAPI(title=settings.APPLICATION_NAME, version="0.1.0")

routers = []

for router in sorted(routers, key=lambda r: getattr(r, "prefix", "")):
    app.include_router(router)
    
@app.get("/")
async def health_check():
    return {"message": "OK"}