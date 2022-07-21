import pydantic
from app.oauth2 import create_access_token, verify_access_token
from fastapi import status
from app import models, utils, schemas, config
import pytest
from .database import client, session, TestSessionLocal, TestClient
from faker import Faker

en_US_faker = Faker()['en_US']

@pytest.fixture
def sample_client_data():
    person = en_US_faker.simple_profile()
    return {
        "name": person['name'],
        "email": person['mail'],
        "address": person['address'],
        "password": en_US_faker.password(),
        "phone_number": en_US_faker.phone_number()
    }

@pytest.fixture
def sample_client_POST(sample_client_data):
    return schemas.POSTClientInput(**sample_client_data)

def add_client(client_data, session):
    new_client = models.Client(**client_data)
    new_client.password = utils.hash(new_client.password)
    session.add(new_client)
    session.commit()
    return new_client

@pytest.fixture
def sample_client(sample_client_data, session):
    return add_client(sample_client_data, session)

@pytest.mark.parametrize('element', ('name', 'email', 'address', 'password', 'phone_number'))
def test_non_null_post_data(client: TestClient, session: TestSessionLocal, element: str, sample_client_data: dict): 
    sample_client_data[element] = ''
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        schemas.POSTClientInput(**sample_client_data)
        
@pytest.mark.parametrize('element', ('name', 'email', 'address', 'password', 'phone_number'))
def test_post_data_constraints(client: TestClient, session: TestSessionLocal, element: str, sample_client_data: dict):
    if element == 'name':
        sample_client_data[element] = en_US_faker.pystr(max_chars=2)
    elif element == 'address' or element == 'password':
        sample_client_data[element] = en_US_faker.pystr(max_chars=7)
    else:
        sample_client_data[element] = en_US_faker.pystr()
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        schemas.POSTClientInput(**sample_client_data)

def test_create_client(client: TestClient, session: TestSessionLocal, sample_client_POST: schemas.POSTClientInput):
    response = client.post(
        '/client',
        json = sample_client_POST.dict()
    )
    assert response.status_code == status.HTTP_201_CREATED
    client_query_data = session.query(models.Client).first()
    assert client_query_data
    assert sample_client_POST.name == client_query_data.name
    assert sample_client_POST.email == client_query_data.email
    assert utils.verify(sample_client_POST.password, client_query_data.password)
    assert sample_client_POST.phone_number == client_query_data.phone_number
    assert sample_client_POST.address == client_query_data.address

def test_create_duplicate_client(client: TestClient, session: TestSessionLocal, sample_client_data: dict):
    add_client(sample_client_data, session)
    response = client.post(
        '/client',
        json = sample_client_data
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    json = response.json()
    assert json
    assert json.get('detail') == 'Email address in use'
    
def test_login_client(client: TestClient, session: TestSessionLocal, sample_client_data: dict):
    add_client(sample_client_data, session)
    response = client.post(
        '/auth/login',
        data =
        {
            "username": sample_client_data['email'],
            "password": sample_client_data['password']
        }
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    json = response.json()
    assert json
    assert verify_access_token(json.get('access_token'))
    assert json.get('token_type') == 'bearer'

def test_login_no_client(client: TestClient, session: TestSessionLocal, sample_client_data: dict):
    response = client.post(
        '/auth/login',
        data =
        {
            "username": sample_client_data['email'],
            "password": sample_client_data['password']
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    json = response.json()
    assert json
    assert json.get('detail') == 'Invalid Credentials'
    
def test_get_client_implicit(client: TestClient, session: TestSessionLocal, sample_client_data: dict):
    new_client = add_client(sample_client_data, session)
    token = create_access_token({"client_id":new_client.id})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    response = client.get('/client')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json
    assert schemas.ClientPublic(**json) == schemas.ClientPublic(**sample_client_data)
    
def test_get_client_fail(client: TestClient, session: TestSessionLocal, sample_client_data: dict):
    add_client(sample_client_data, session)
    response = client.get(f'/client')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json = response.json()
    assert json
    assert json.get("detail") == f'Not authenticated'
    
def test_delete_client_implicit(client: TestClient, session: TestSessionLocal, sample_client: models.Client):
    token = create_access_token({"client_id":sample_client.id})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    response = client.delete('/client')
    assert response.status_code == status.HTTP_200_OK
    queried_client = session.query(models.Client).filter(models.Client.id == 1).first()
    assert not queried_client
    
def test_delete_client_fail(client: TestClient, session: TestSessionLocal, sample_client: models.Client):
    response = client.delete(f'/client')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json = response.json()
    assert json
    assert json.get("detail") == f'Not authenticated'

# ADMIN TESTS

def test_login_admin(client: TestClient, session: TestSessionLocal):
    response = client.post(
        '/auth/login',
        data =
        {
            "username": config.settings.testing_admin_username,
            "password": config.settings.testing_admin_password
        }
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    json = response.json()
    assert json
    assert json.get('token_type') == 'bearer'
    token = verify_access_token(json.get('access_token'))
    assert token.id == '0'
    
def test_get_client_explicit_admin(client: TestClient, session: TestSessionLocal, sample_client_data: dict):
    new_client = add_client(sample_client_data, session)
    token = create_access_token({"client_id":0})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    response = client.get(
        '/client',
        params = {
            "id":new_client.id
        })
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json
    assert schemas.ClientPublic(**json) == schemas.ClientPublic(**sample_client_data)
    
def test_delete_client_explicit_admin(client: TestClient, session: TestSessionLocal, sample_client: models.Client):
    token = create_access_token({"client_id":0})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    response = client.delete(
        '/client',
        params = {
            "id":sample_client.id
        })
    assert response.status_code == status.HTTP_200_OK
    queried_client = session.query(models.Client).filter(models.Client.id == 1).first()
    assert not queried_client