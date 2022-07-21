from pydantic import BaseModel, EmailStr, constr
from typing import Optional
import re

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
    password: constr(
        min_length=8
    )

class GETClientReturn(ClientPublic):
    class Config:
        orm_mode = True

class POSTClientLogin(BaseModel):
    email: EmailStr
    password: str

class AppointmentPublic(BaseModel):
    description: str
    price: float
    
class POSTAppointmentInput(AppointmentPublic):
    date: int
    paid: Optional[bool]
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
    id: Optional[str] = None