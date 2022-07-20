from fastapi import Depends, HTTPException, status, Response, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..config import settings
from ..database import get_db

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post('/login', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Token)
def login_client(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    if credentials.username == settings.admin_username and utils.verify(credentials.password, settings.admin_password):
        access_token = oauth2.create_access_token({
            "client_id": 0
        })
    else:
        client: models.Client = db.query(models.Client).filter(models.Client.email == credentials.username).first()
        
        if not client:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid Credentials")

        if not utils.verify(credentials.password, client.password):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid Credentials")

        access_token = oauth2.create_access_token({
            "client_id": client.id
        })
    return {"access_token": access_token, "token_type": "bearer"}