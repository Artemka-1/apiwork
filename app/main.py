from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud
from .database import engine, Base
from .deps import get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API", version="1.0")

@app.post("/contacts/", response_model=schemas.ContactOut, status_code=status.HTTP_201_CREATED)
def create_contact(contact_in: schemas.ContactCreate, db: Session = Depends(get_db)):
    # перевірка унікального email
    existing = db.query(models.Contact).filter(models.Contact.email == contact_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contact with this email already exists")
    return crud.create_contact(db, contact_in)

@app.get("/contacts/", response_model=List[schemas.ContactOut])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_contacts(db, skip=skip, limit=limit)

@app.get("/contacts/{contact_id}", response_model=schemas.ContactOut)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    c = crud.get_contact(db, contact_id)
    if not c:
        raise HTTPException(status_code=404, detail="Contact not found")
    return c

@app.put("/contacts/{contact_id}", response_model=schemas.ContactOut)
def update_contact(contact_id: int, patch: schemas.ContactUpdate, db: Session = Depends(get_db)):
    updated = crud.update_contact(db, contact_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    success = crud.delete_contact(db, contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    return

@app.get("/search/", response_model=List[schemas.ContactOut])
def search(q: str = Query(..., min_length=1), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.search_contacts(db, q=q, skip=skip, limit=limit)

@app.get("/birthdays/", response_model=List[schemas.ContactOut])
def upcoming_birthdays(days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    return crud.birthdays_next_days(db, days=days)
