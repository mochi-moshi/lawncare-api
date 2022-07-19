from pydantic import BaseModel, EmailStr

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