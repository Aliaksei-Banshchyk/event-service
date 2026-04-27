import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/api", tags=["EventService"])


@router.post("/events", response_model=schemas.EventResponse, status_code=201)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    event = models.Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/events", response_model=List[schemas.EventResponse])
def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()


@router.get("/event/byDate", response_model=List[schemas.EventResponse])
def get_events_by_date(from_date: Optional[datetime] = Query(None), to_date: Optional[datetime] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Event)
    if from_date:
        query = query.filter(models.Event.event_date >= from_date)
    if to_date:
        query = query.filter(models.Event.event_date <= to_date)
    return query.order_by(models.Event.event_date).all()


@router.get("/event/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/events/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, payload: schemas.EventUpdate, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event
