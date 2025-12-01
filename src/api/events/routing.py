import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from .models import (
    EventModel, 
    EventBucketSchema, 
    EventCreateSchema,
    get_utc_now
)
from .sessions import get_session
from sqlmodel import case, func
from datetime import datetime, timedelta, timezone
from timescaledb.hyperfunctions import time_bucket
# from db.config import DATABASE_URL
from src.api.events.db.config import DATABASE_URL

 
router = APIRouter()

DEFAULT_LOOKUP_PAGES = [
    "/", "/about", "/pricing", "/content", "/blog", "/products", "/login", "/signup", "/dashboard", "/settings"
]


# Get Method


# @router.get("/")
# def read_events():
#     return{
#         "item": ['1','2','3']
#     }

@router.get("/", response_model=List[EventBucketSchema])
def read_events(
    duration: str = Query(default='1 day'),
    pages: List = Query(default=None),
    session: Session=Depends(get_session)):

    os_case = case(
        (EventModel.user_agent.ilike('%Windows%'), 'Windows'),
        (EventModel.user_agent.ilike('%Mac%'), 'Mac'),
        (EventModel.user_agent.ilike('%Linux%'), 'Linux'),
        (EventModel.user_agent.ilike('%Android%'), 'Android'),
        (EventModel.user_agent.ilike('%iOS%'), 'iOS'),
        else_='Other'
    ).label('operating_system')

    bucket = time_bucket(duration, EventModel.time)
    lookup_pages = pages if isinstance(pages, list) and len(pages) > 0 else DEFAULT_LOOKUP_PAGES


    query = (
            select(
                bucket.label('bucket'),
                os_case,
                EventModel.page.label('page'),
                func.count().label('count'),
                func.avg(EventModel.duration).label('average_duration'),
            )
            .where(
                EventModel.page.in_(lookup_pages)
            )
            .group_by(
                bucket,
                EventModel.page,
                os_case,
            )
            .order_by(
                bucket,
                EventModel.page,
                os_case,
            )
    )
    results = session.exec(query).fetchall()

    return results

@router.get("/{event_id}", response_model=EventModel) 
def get_data(event_id: int, session: Session = Depends(get_session)):
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()

    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return result 


# @router.get("/{event_id_str}") 
# def get_data(event_id_str: str):
#     return{"id": event_id_str}







# Post Method

# @router.post("/")
# def create_event() -> EventModel:
#     return{"id": 123}


@router.post("/", response_model=EventModel)
def create_event(
    payload:EventCreateSchema, 
    session: Session = Depends(get_session)):

    data = payload.model_dump()
    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj


# Put Method  

# @router.put("/{event_id}", response_model=EventModel) 
# def update_data(
#     event_id: int, 
#     payload:EventUpdateSchema, 
#     session: Session = Depends(get_session)):

#     query = select(EventModel).where(EventModel.id == event_id)
#     obj = session.exec(query).first()

#     if not obj:
#         raise HTTPException(status_code=404, detail="Item not found")
    

#     data = payload.model_dump()
#     for k,v in data.items():
#         setattr(obj, k, v)

#     obj.updated_at = get_utc_now()
#     session.add(obj)
#     session.commit()
#     session.refresh(obj)

#     return obj 


# # Delete Method
 
# @router.delete("/{event_id}") 
# def delete_data(event_id: int) -> EventModel:
#     return{"id": event_id}


