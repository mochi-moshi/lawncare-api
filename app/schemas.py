from pydantic import BaseModel

class POSTClientInput(BaseModel):
    name: str
    email: str
    phone_number: str
    password: str
    address: str

class GETClientReturn(BaseModel):
    name: str
    email: str
    phone_number: str
    address: str