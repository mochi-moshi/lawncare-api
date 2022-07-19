from pydantic import BaseModel, EmailStr
from typing import Optional

class ClientPublic(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    address: str

class POSTClientInput(ClientPublic):
    password: str

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