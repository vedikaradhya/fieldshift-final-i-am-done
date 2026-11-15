from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.entities import Role

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    password: str = Field(min_length=12, max_length=128)
    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if not any(c.isupper() for c in value) or not any(c.islower() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Password needs upper- and lower-case letters and a number")
        return value

class LoginRequest(BaseModel): email: EmailStr; password: str
class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)
    confirmation: str
    @field_validator("confirmation")
    @classmethod
    def required_confirmation(cls, value: str) -> str:
        if value != "DELETE": raise ValueError("confirmation must equal DELETE")
        return value
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; email: EmailStr; phone: str | None; role: Role; is_verified: bool
class TokenOut(BaseModel): access_token: str; token_type: str = "bearer"; user: UserOut

class FarmInput(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = None; country: str | None = None; state: str | None = None; district: str | None = None
    boundary: dict | None = None; soil_type: str | None = None; irrigation_type: str | None = None; current_crop: str | None = None; notes: str | None = None
class FarmOut(FarmInput):
    model_config = ConfigDict(from_attributes=True)
    id: int; owner_id: int; area_hectares: float; created_at: datetime
class FieldInput(BaseModel): name: str = Field(min_length=2); boundary: dict | None = None; current_crop: str | None = None
class FieldOut(FieldInput):
    model_config = ConfigDict(from_attributes=True)
    id: int; farm_id: int; area_hectares: float
