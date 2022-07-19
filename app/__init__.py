from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from .routers import client, appointment, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(client.router)
app.include_router(appointment.router)
app.include_router(auth.router)

@app.get('/')
def root():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get('/test', status_code=status.HTTP_200_OK)
def test():
    return {"message": "Hello, World!"}