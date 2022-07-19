from fastapi import Depends, HTTPException, status, Response, APIRouter
from sqlalchemy.orm import Session

from app import oauth2
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix='/client',
    tags=['Client']
    )

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_client(client: schemas.POSTClientInput, db: Session = Depends(get_db)):
    '''
    Adds a new client to the database if the email address is not already registered
    '''
    client_exists = db.query(models.Client).filter(models.Client.email == client.email).first()
    if client_exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email address in use")

    client.password = utils.hash(client.password)
    new_client = models.Client(**client.dict())
    db.add(new_client)
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED)

@router.get('/', response_model=schemas.GETClientReturn)
def get_client(db: Session = Depends(get_db), current_client: models.Client = Depends(oauth2.get_current_client)):
    '''
    Gets the  'public' information
    '''
    return current_client

@router.get('/{id}', response_model=schemas.GETClientReturn)
def get_client(id: int, db: Session = Depends(get_db), current_client: models.Client = Depends(oauth2.get_current_client)):
    '''
    Gets the  'public' information
    '''
    if id != current_client.id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f'Cannot access client id: {id}')
    client: models.Client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    return client

@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete_client(id: int, db: Session = Depends(get_db), current_client: models.Client = Depends(oauth2.get_current_client)):
    '''
    Removes the client from the database
    '''
    # TODO: differentiate between admin removal and personal removal
    if id != current_client.id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f'Cannot remove client id: {id}')
    client_query = db.query(models.Client).filter(models.Client.id == id)
    if not client_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    client_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)