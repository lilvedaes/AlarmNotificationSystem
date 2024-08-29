from pydantic import BaseModel, constr, model_validator
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

# UserUpdate will include either email or phone_number
class UserUpdate(BaseModel):
    username: Optional[constr(max_length=50)] = None
    phone_number: Optional[PhoneNumber] = None

    # Validate that at least one of username or phone_number is provided
    @model_validator(mode='after')
    @classmethod
    def check_contact_info(cls, self) -> Self:
        if not self.username and not self.phone_number:
            raise ValueError('At least one of username or phone_number must be provided.')
        return self

# The User schema will include all UserBase fields + id + aws_phone_number_id
class User(UserBase):
    id: int
    aws_phone_number_id: str

    class Config:
        from_attributes = True