from fastapi import Depends, HTTPException, status, Response, APIRouter, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import oauth2
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/appointment", tags=["Appointment"])


@router.get("", status_code=status.HTTP_200_OK)
def get_appointments(
    request: Request,
    client_id: int = None,
    appointment_id: int = None,
    before: int = None,
    after: str = None,
    paid: bool = False,
    db: Session = Depends(get_db),
    auth_token: schemas.TokenData = Depends(oauth2.verify_access_token),
):
    if auth_token.testing != "True":
        oauth2.validate_access_token(request.host, request.port, auth_token)
    if auth_token.client_id != "0":
        if utils.is_set(client_id):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Cannot get appointments from client of different id",
            )
        client_id = int(auth_token.client_id)

    if not utils.is_set(client_id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Need to specify client to get appointments from",
        )

    if utils.is_set(appointment_id):
        if utils.is_set(before) or utils.is_set(after) or utils.is_set(paid):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot set constraints when fetching by id",
            )
        appointment = (
            db.query(models.Appointment)
            .filter(models.Appointment.id == appointment_id)
            .first()
        )
        if not appointment or appointment.client_id != client_id:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Cannot find appointment with id: {appointment_id}",
            )
        return appointment
    else:
        appointments = db.query(models.Appointment).filter(
            models.Appointment.client_id == client_id
        )
        if utils.is_set(before):
            appointments = appointments.filter(
                models.Appointment.date < datetime.fromtimestamp(before)
            )
        if utils.is_set(after):
            appointments = appointments.filter(
                models.Appointment.date > datetime.fromtimestamp(after)
            )
        if utils.is_set(paid):
            appointments = appointments.filter(
                models.Appointment.paid == ("t" if paid else "f")
            )

    return appointments.all()


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.GETAppointmentReturn
)
def make_appointment(
    request: Request,
    appointment_data: schemas.POSTAppointmentInput,
    db: Session = Depends(get_db),
    auth_token: schemas.TokenData = Depends(oauth2.verify_access_token),
):
    if auth_token.testing != "True":
        oauth2.validate_access_token(request.host, request.port, auth_token)
    # Admin access
    if auth_token.client_id != "0":
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    # TODO: add email notification
    _data = appointment_data.dict()

    client = (
        db.query(models.Client)
        .filter(models.Client.id == appointment_data.client_id)
        .first()
    )
    if not client:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Client with id: {appointment_data.client_id} does not exists",
        )
    if (
        appointment_data.date
        < datetime.now().timestamp() + timedelta(days=1).total_seconds()
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot create past appointment")
    if not appointment_data.description:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Must provide description")
    if not appointment_data.price:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Must provide price")
    if appointment_data.paid is None:
        _data["paid"] = False

    _data["date"] = datetime.fromtimestamp(_data["date"]).date()

    appointment = (
        db.query(models.Appointment)
        .filter(models.Appointment.client_id == appointment_data.client_id)
        .filter(models.Appointment.date == _data["date"])
        .first()
    )
    if appointment:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Appointment already exists for client"
        )

    appointment = models.Appointment(**_data)
    db.add(appointment)
    db.commit()
    return _data


@router.delete("", status_code=status.HTTP_200_OK)
def cancel_appointment(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    auth_token: schemas.TokenData = Depends(oauth2.verify_access_token),
):
    if auth_token.testing != "True":
        oauth2.validate_access_token(request.host, request.port, auth_token)
    client = (
        db.query(models.Client).filter(models.Client.id == auth_token.client_id).first()
    )
    if not client:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Client with id: {auth_token.client_id} does not exists",
        )
    appointment = (
        db.query(models.Appointment)
        .filter(models.Appointment.client_id == auth_token.id)
        .filter(models.Appointment.id == id)
    )
    if appointment.first():
        # TODO: add email notification
        appointment.delete(synchronize_session=False)
        db.commit()
    else:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointment with id: {id} does not exist for client",
        )

    return Response(status_code=status.HTTP_200_OK)
