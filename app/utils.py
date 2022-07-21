from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(*args):
    return pwd_context.hash('-'.join([str(arg) for arg in args]))

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def is_set(parameter):
    return not (parameter is None)