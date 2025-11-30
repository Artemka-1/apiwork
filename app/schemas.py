from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import date

PhoneStr = constr(min_length=5, max_length=30, regex=r'^[\d\+\-\s\(\)]*$') 

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: PhoneStr
    birth_date: date
    extra: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[PhoneStr] = None
    birth_date: Optional[date] = None
    extra: Optional[str] = None

class ContactOut(ContactBase):
    id: int

    class Config:
        orm_mode = True
