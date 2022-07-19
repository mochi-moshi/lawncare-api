from fastapi import FastAPI
from .routers import client

app = FastAPI()
app.include_router(client.router)

@app.get('/')
def root():
    return {}

@app.get('/test')
def test():
    return {"message": "Hello, World!"}