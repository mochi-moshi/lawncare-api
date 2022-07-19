from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get('/')
def root():
    return {}

@app.get('/test')
def test():
    return {"message": "Hello, World!"}

@app.post('/client', status_code=status.HTTP_201_CREATED)
def create_client(client: schemas.POSTClientInput, db: Session = Depends(get_db)):
    # TODO: check if client email, address, or phone-number already registered
    new_client = models.Client(**client.dict())
    db.add(new_client)
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED)

@app.get('/client/{id}', response_model=schemas.GETClientReturn)
def get_client(id: int, db: Session = Depends(get_db)):
    # TODO: check if user has permissions
    client: models.Client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    return {
        "name": client.name,
        "email": client.email,
        "phone_number": client.phone_number,
        "address": client.address
    }

@app.delete('/client/{id}', status_code=status.HTTP_200_OK)
def delete_client(id: int, db: Session = Depends(get_db)):
    # TODO: check if user has permissions
    client_query = db.query(models.Client).filter(models.Client.id == id)
    if not client_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    client_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)