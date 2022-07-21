from fastapi import Depends, HTTPException, status, Response, APIRouter, Request
from sqlalchemy.orm import Session

from app import oauth2
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix='/client',
    tags=['Client']
    )

@router.post('', status_code=status.HTTP_201_CREATED)
def create_client(client: schemas.POSTClientInput, db: Session = Depends(get_db)):
    '''
    Adds a new client to the database if the email address is not already registered
    '''
    # TODO: Sanitize data
    client_exists = db.query(models.Client).filter(models.Client.email == client.email).first()
    if client_exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email address in use")

    client.password = utils.hash(client.password)
    new_client = models.Client(**client.dict())
    db.add(new_client)
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED)

@router.get('', response_model=schemas.GETClientReturn)
def get_client(request: Request, id: int = None, db: Session = Depends(get_db), auth_token: schemas.TokenData = Depends(oauth2.verify_access_token)):
    '''
    Gets the  'public' information
    '''
    if auth_token.testing != 'True':
        oauth2.validate_access_token(request.host, request.port, auth_token)
    if auth_token.client_id != '0':
        if not (id is None):
            raise HTTPException(status.HTTP_403_FORBIDDEN)
        id = int(auth_token.client_id)
    if id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Need to specify client to get')
    
    client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    return client

@router.delete('', status_code=status.HTTP_200_OK)
def delete_client(request: Request, id:int = None, db: Session = Depends(get_db), auth_token: schemas.TokenData = Depends(oauth2.verify_access_token)):
    '''
    Removes the client from the database
    '''
    if auth_token.testing != 'True':
        oauth2.validate_access_token(request.host, request.port, auth_token)
    if auth_token.client_id != '0':
        if not (id is None):
            raise HTTPException(status.HTTP_403_FORBIDDEN, 'Cannot delete client of different id')
        id = int(auth_token.client_id)
    if id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Need to specify client to delete')
    client_query = db.query(models.Client).filter(models.Client.id == id)
    if not client_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Client with id: {id} does not exist')
    
    # TODO: add email notification
    client_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)