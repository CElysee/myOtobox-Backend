from datetime import datetime, time
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    username: Optional[str]
    password: str
    role: str
    phone_number: Optional[str]

    # last_login: Optional[datetime] = None
    # deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class UserCreate(User):
    pass


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str
    username: str
    role: str
    created_at: datetime
    is_active: bool
    # country_id: int
    # user_profile_id: int


class UserCheck(BaseModel):
    email: EmailStr


class UserId(BaseModel):
    id: int


class CountryBase(BaseModel):
    name: str
    code: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class CountryUpdate(CountryBase):
    pass


class CountryOut(CountryBase):
    id: int

    class Config:
        from_attributes = True


class CarBrandBase(BaseModel):
    name: str
    country_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class CarBrandUpdate(BaseModel):
    name: Optional[str]
    country_name: Optional[str]
    updated_at: Optional[datetime] = None


class CarModelBase(BaseModel):
    brand_id: str
    brand_model_name: str
    production_years: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class CarModelUpdate(BaseModel):
    brand_id: Optional[str]
    brand_model_name: Optional[str]
    production_years: Optional[str]
    updated_at: Optional[datetime] = None


class CarTrimBase(BaseModel):
    model_id: str
    trim_name: str
    engine: Optional[str]
    curb_weight: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None


class CarTrimUpdate(BaseModel):
    model_id: Optional[str]
    trim_name: Optional[str]
    engine: Optional[str]
    curb_weight: Optional[str]
    updated_at: Optional[datetime] = None


class CarStandardFeaturesBase(BaseModel):
    feature_name: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None


class CarStandardFeaturesUpdate(BaseModel):
    feature_name: Optional[str]
    updated_at: Optional[datetime] = None


class CarFuelTypeBase(BaseModel):
    fuel_type: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None


class CarFuelTypeUpdate(BaseModel):
    fuel_type: Optional[str]
    updated_at: Optional[datetime] = None
