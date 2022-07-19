from fastapi import Depends, HTTPException, status, Response, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import oauth2
from .. import models, schemas, utils
from ..database import get_db
import app

router = APIRouter(
    prefix='/appointment',
    tags=['Appointment']
    )

@router.get('', status_code=status.HTTP_200_OK)
def get_appointments(before: int = None, after: str = None, paid: bool = False, db: Session = Depends(get_db), current_client: models.Client = Depends(oauth2.get_current_client)):
    appointments = db.query(models.Appointment).filter(models.Appointment.client_id == current_client.id)
    if not (before is None):
        appointments = appointments.filter(models.Appointment.date < datetime.fromtimestamp(before))
    if not (after is None):
        appointments = appointments.filter(models.Appointment.date > datetime.fromtimestamp(after))
    if not (paid is None):
        appointments = appointments.filter(models.Appointment.paid == ('t' if paid else 'f'))

    return appointments.all()

@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.GETAppointmentReturn)
def make_appointment(appointment_data: schemas.POSTAppointmentInput, db: Session = Depends(get_db), current_client: models.Client = Depends(oauth2.get_current_client)):
    _data = appointment_data.dict()
    _data.update({'client_id':current_client.id})

    if appointment_data.date < datetime.now().timestamp() + timedelta(days=1).total_seconds():
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Cannot create past appointment')
    if datetime.now().timestamp() - appointment_data.date > timedelta(weeks=16).total_seconds():
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Cannot create appointment more than 4 months ahead')
    if not appointment_data.description:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Must provide description')
    if not appointment_data.price:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Must provide price')
    if appointment_data.paid is None:
        _data['paid'] = False

    _data['date'] = datetime.fromtimestamp(_data['date']).date()

    appointment = db.query(models.Appointment).filter(models.Appointment.client_id == current_client.id).filter(models.Appointment.date == _data['date']).first()
    if appointment:
        raise HTTPException(status.HTTP_409_CONFLICT, 'Appointment already exists for client')

    appointment = models.Appointment(**_data)
    db.add(appointment)
    db.commit()
    return {
        "id": appointment.id,
        "date": str(appointment.date),
        "description": appointment.description,
        "price": appointment.price,
        "paid": appointment.paid
    }

@router.delete('', status_code=status.HTTP_200_OK)
def cancel_appointment(id: int, db: Session = Depends(get_db), current_client: models.Client = Depends(oauth2.get_current_client)):
    appointment = db.query(models.Appointment).filter(models.Appointment.client_id == current_client.id).filter(models.Appointment.id == id)
    if appointment.first():
        appointment.delete(synchronize_session=False)
        db.commit()
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'Appointment with id: {id} does not exist for client')

    return Response(status_code=status.HTTP_200_OK)