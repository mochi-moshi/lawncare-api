import pydantic
from app.oauth2 import create_access_token, verify_access_token
from fastapi import status
from app import models, utils, schemas
import pytest
from .database import client, session, TestSessionLocal, TestClient
from typing import List
from faker import Faker

en_US_faker = Faker()['en_US']

def generate_sample_good_client_data():
    data = []
    for _ in range(5):
        person = en_US_faker.simple_profile()
        data.append({
            "name": person['name'],
            "email": person['mail'],
            "address": person['address'],
            "password": en_US_faker.password(),
            "phone_number": en_US_faker.phone_number()
        })
    return data

sample_good_client_input: List[schemas.POSTClientInput] = [
    schemas.POSTClientInput(**d)
    for d in generate_sample_good_client_data()
    ]

def add_sample_client(session, client_data):
    new_client = models.Client(**client_data.dict())
    new_client.password = utils.hash(new_client.password)
    session.add(new_client)
    session.commit()
    return new_client

@pytest.mark.parametrize('element', ('name', 'email', 'address', 'password', 'phone_number'))
def test_non_null_post_data(client: TestClient, session: TestSessionLocal, element: str): 
    person = en_US_faker.simple_profile()
    data = {
        "name": person['name'],
        "email": person['mail'],
        "address": person['address'],
        "password": en_US_faker.password(),
        "phone_number": en_US_faker.phone_number()
    }
    data[element] = ''
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        schemas.POSTClientInput(**data)
        
@pytest.mark.parametrize('element', ('name', 'email', 'address', 'password', 'phone_number'))
def test_post_data_constraints(client: TestClient, session: TestSessionLocal, element: str):
    person = en_US_faker.simple_profile()
    data = {
        "name": person['name'],
        "email": person['mail'],
        "address": person['address'],
        "password": en_US_faker.password(),
        "phone_number": en_US_faker.phone_number()
    }
    if element == 'name':
        data[element] = en_US_faker.pystr(max_chars=2)
    elif element == 'address' or element == 'password':
        data[element] = en_US_faker.pystr(max_chars=7)
    else:
        data[element] = en_US_faker.pystr()
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        schemas.POSTClientInput(**data)

@pytest.mark.parametrize("client_data", sample_good_client_input)
def test_create_client(client: TestClient, session: TestSessionLocal, client_data: schemas.POSTClientInput):
    response = client.post(
        '/client',
        json = client_data.dict()
    )
    assert response.status_code == status.HTTP_201_CREATED
    client_query_data = session.query(models.Client).first()
    assert client_query_data
    assert client_data.name == client_query_data.name
    assert client_data.email == client_query_data.email
    assert utils.verify(client_data.password, client_query_data.password)
    assert client_data.phone_number == client_query_data.phone_number
    assert client_data.address == client_query_data.address

@pytest.mark.parametrize("client_data", sample_good_client_input)
def test_create_duplicate_client(client: TestClient, session: TestSessionLocal, client_data: schemas.POSTClientInput):
    add_sample_client(session, client_data)
    response = client.post(
        '/client',
        json = client_data.dict()
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    json = response.json()
    assert json
    assert json.get('detail') == 'Email address in use'
    
@pytest.mark.parametrize("client_data", sample_good_client_input)
def test_login_client(client: TestClient, session: TestSessionLocal, client_data: schemas.POSTClientInput):
    add_sample_client(session, client_data)
    response = client.post(
        '/auth/login',
        data =
        {
            "username": client_data.email,
            "password": client_data.password
        }
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    json = response.json()
    assert json
    assert verify_access_token(json.get('access_token'))
    assert json.get('token_type') == 'bearer'

def test_login_no_client(client: TestClient, session: TestSessionLocal):
    response = client.post(
        '/auth/login',
        data =
        {
            "username": "example@gmail.com",
            "password": "12345"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    json = response.json()
    assert json
    assert json.get('detail') == 'Invalid Credentials'
    
@pytest.mark.parametrize("client_data", sample_good_client_input)
def test_get_client_implicit(client: TestClient, session: TestSessionLocal, client_data: schemas.POSTClientInput):
    new_client = add_sample_client(session, client_data)
    token = create_access_token({"client_id":new_client.id})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    response = client.get('/client')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json
    assert schemas.ClientPublic(**json) == schemas.ClientPublic(**client_data.dict())
    
@pytest.mark.parametrize("client_data", sample_good_client_input)
def test_get_client_fail(client: TestClient, session: TestSessionLocal, client_data: schemas.POSTClientInput):
    new_client = add_sample_client(session, client_data)
    response = client.get(f'/client')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json = response.json()
    assert json
    assert json.get("detail") == f'Not authenticated'
    
@pytest.mark.parametrize("client_data", sample_good_client_input)
def test_delete_client_implicit(client: TestClient, session: TestSessionLocal, client_data: schemas.POSTClientInput):
    new_client = add_sample_client(session, client_data)
    token = create_access_token({"client_id":new_client.id})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    response = client.delete('/client')
    assert response.status_code == status.HTTP_200_OK
    queried_client = session.query(models.Client).filter(models.Client.id == 1).first()
    assert not queried_client
    
@pytest.mark.parametrize("client_data", sample_good_client_input)
def test_delete_client_fail(client: TestClient, session: TestSessionLocal, client_data: schemas.POSTClientInput):
    new_client = add_sample_client(session, client_data)
    response = client.delete(f'/client')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json = response.json()
    assert json
    assert json.get("detail") == f'Not authenticated'