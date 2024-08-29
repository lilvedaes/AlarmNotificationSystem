from pydantic import BaseModel, constr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional
from typing_extensions import Self

# Restrict phone number format
PhoneNumber.phone_format = 'E164'

# User Schemas
class UserBase(BaseModel):
    username: constr(max_length=50)
    phone_number: PhoneNumber

# UserCreate will include all UserBase fields
class UserCreate(UserBase):
    pass

# UserUpdate will include only phone_number
class UserUpdate(BaseModel):
    phone_number: PhoneNumber = None

# The User schema will include all UserBase fields + id
class User(UserBase):
    id: int

    class Config:
        from_attributes = True