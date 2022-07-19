from fastapi import FastAPI
from fastapi.params import Body

app = FastAPI()


@app.get('/')
async def root():
    return {}

@app.get('/test')
async def test():
    return {"message": "Hello, World!"}

@app.post('/echo')
async def echo(payload: dict = Body(...)):
    return payload