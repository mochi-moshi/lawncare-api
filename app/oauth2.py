from datetime import timedelta, datetime
from jose import JWTError, jwt
from . import schemas, models, database
from .config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.token_secret
ALGORITHM = settings.token_algorithm
EXPIRE_SECONDS = settings.token_expire_seconds

def create_access_token(data: dict) -> str:
    data_copy = data.copy()
    
    expire = datetime.utcnow() + timedelta(seconds=EXPIRE_SECONDS)
    data_copy.update({"exp": expire})
    
    return jwt.encode(data_copy, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str = Depends(oauth2_scheme)) -> schemas.TokenData:
    try:
        data: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = data.get("client_id")
        if id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
        return schemas.TokenData(id=id)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})

def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    token = verify_access_token(token)
    client = db.query(models.Client).filter(models.Client.id == token.id).first()
    if not client:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    return client
    