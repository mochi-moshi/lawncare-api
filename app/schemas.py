from pydantic import BaseModel, EmailStr, constr
from typing import Optional

PASSWORD_CONSTRAINT = constr(
        min_length=8
    )

class ClientPublic(BaseModel):
    name: constr(
        strip_whitespace=True,
        min_length=3
    )
    email: EmailStr
    phone_number: constr(
            strip_whitespace=True,
            regex=r"^(?:(?:\+[1-9]|(?:00)?[1-9])[-.]?)?(\([0-9]{3}\)|[0-9]{3}[-.]?)[0-9]{3}[-.]?[0-9]{4}(x[0-9]{1,5})?$"
        )
    address: constr(
        strip_whitespace=True,
        min_length= 8
    )

class POSTClientInput(ClientPublic):
    password: PASSWORD_CONSTRAINT

class GETClientReturn(ClientPublic):
    class Config:
        orm_mode = True

class POSTClientLogin(BaseModel):
    email: EmailStr
    password: PASSWORD_CONSTRAINT

class AppointmentPublic(BaseModel):
    description: str
    price: float
    
class POSTAppointmentInput(AppointmentPublic):
    date: int
    paid: Optional[bool] = False
    client_id: int

class GETAppointmentReturn(AppointmentPublic):
    id: int
    date: str
    paid: bool
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    client_id: str
    host: str
    testing: str = 'False'