from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr = Field(examples=["john.doe@example.com"])
    first_name: Optional[str] = Field(default=None, examples=["John"])
    last_name: Optional[str] = Field(default=None, examples=["Doe"])
    is_active: Optional[bool] = Field(default=None, examples=[True])

    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    password: str = Field(examples=["SecurePassword&*1234"])


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None, examples=["john.doe@example.com"])
    first_name: Optional[str] = Field(default=None, examples=["John"])
    last_name: Optional[str] = Field(default=None, examples=["Doe"])
    is_active: Optional[bool] = Field(default=None, examples=[True])

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_value(cls, values):
        if isinstance(values, dict) and not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values


class UserResponse(UserBase):
    uuid: uuid.UUID = Field(examples=[uuid.uuid4()])
    first_name: Optional[str] = Field(default=None, min_length=3, pattern=r"^[\w-]+$", examples=["John"])
    last_name: Optional[str] = Field(default=None, min_length=3, pattern=r"^[\w-]+$", examples=["Doe"])
    created_at: Optional[datetime] = None

    @field_validator("uuid", mode="before")
    @classmethod
    def coerce_uuid(cls, v):
        return v if isinstance(v, uuid.UUID) else uuid.UUID(str(v))


class LoginRequest(BaseModel):
    email: str = Field(examples=["john.doe@example.com"])
    password: str = Field(examples=["SecurePassword&*1234"])


class ErrorResponse(BaseModel):
    error: str = Field(examples=["Not Found"])
    details: Optional[str] = Field(default=None, examples=["The requested resource was not found."])
