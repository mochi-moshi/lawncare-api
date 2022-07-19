from fastapi import Depends, HTTPException, status, Response, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix='/client')

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_client(client: schemas.POSTClientInput, db: Session = Depends(get_db)):

    client_exists = db.query(models.Client).filter(models.Client.email == client.email).first()
    if client_exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email address in use")

    client.password = utils.hash(client.password)
    new_client = models.Client(**client.dict())
    db.add(new_client)
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED)

@router.get('/{id}', response_model=schemas.GETClientReturn)
def get_client(id: int, db: Session = Depends(get_db)):
    # TODO: check if user has permissions
    client: models.Client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    return client

@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete_client(id: int, db: Session = Depends(get_db)):
    # TODO: check if user has permissions
    client_query = db.query(models.Client).filter(models.Client.id == id)
    if not client_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    client_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)