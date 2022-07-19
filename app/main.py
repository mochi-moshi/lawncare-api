from fastapi import FastAPI
from .routers import client, auth
from .database import engine
from .models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(client.router)
app.include_router(auth.router)

@app.get('/')
def root():
    return {}

@app.get('/test')
def test():
    return {"message": "Hello, World!"}