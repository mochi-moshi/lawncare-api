from datetime import timedelta, datetime
from jose import JWTError, jwt
from . import schemas, models, database
from .settings import settings
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

def verify_access_token(token: str, exception) -> schemas.TokenData:
    try:
        data: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = data.get("client_id")
        if id is None:
            raise exception
        return schemas.TokenData(id=id)
    except JWTError:
        raise exception

def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    cred_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    token = verify_access_token(token, cred_exception)
    client = db.query(models.Client).filter(models.Client.id == token.id).first()
    if not client:
        raise cred_exception
    return client
    