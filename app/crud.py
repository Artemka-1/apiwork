from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from . import models, schemas
from typing import List, Optional
from datetime import date, datetime, timedelta

def create_contact(db: Session, contact: schemas.ContactCreate) -> models.Contact:
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contact(db: Session, contact_id: int) -> Optional[models.Contact]:
    return db.get(models.Contact, contact_id)

def list_contacts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Contact]:
    return db.query(models.Contact).offset(skip).limit(limit).all()

def update_contact(db: Session, contact_id: int, patch: schemas.ContactUpdate) -> Optional[models.Contact]:
    db_contact = db.get(models.Contact, contact_id)
    if not db_contact:
        return None
    for key, value in patch.dict(exclude_unset=True).items():
        setattr(db_contact, key, value)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int) -> bool:
    db_contact = db.get(models.Contact, contact_id)
    if not db_contact:
        return False
    db.delete(db_contact)
    db.commit()
    return True

def search_contacts(db: Session, q: str, skip: int = 0, limit: int = 100):
    pattern = f"%{q}%"
    return db.query(models.Contact).filter(
        or_(
            models.Contact.first_name.ilike(pattern),
            models.Contact.last_name.ilike(pattern),
            models.Contact.email.ilike(pattern),
        )
    ).offset(skip).limit(limit).all()

def birthdays_next_days(db: Session, days: int = 7):
    today = date.today()
    results = []
    # load all contacts and filter in python (safer for month-day logic across year boundary)
    all_contacts = db.query(models.Contact).all()
    for c in all_contacts:
        bd = c.birth_date
        # compute next birthday date in current year or next year
        try:
            this_year_bday = date(today.year, bd.month, bd.day)
        except ValueError:
            # For Feb 29 on non-leap year -> treat as Feb 28
            this_year_bday = date(today.year, 2, 28)
        if this_year_bday < today:
            try:
                next_bday = date(today.year + 1, bd.month, bd.day)
            except ValueError:
                next_bday = date(today.year + 1, 2, 28)
        else:
            next_bday = this_year_bday
        delta = (next_bday - today).days
        if 0 <= delta <= days:
            results.append((c, delta))
    # sort by upcoming delta
    results.sort(key=lambda x: x[1])
    return [r[0] for r in results]
