from datetime import datetime, time
from typing import Optional, List

from pydantic import BaseModel, EmailStr, FilePath


class User(BaseModel):
    firstName: str
    lastName: str
    gender: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"
    phone_number: Optional[str]
    country_id: Optional[int]

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


class UserUpdate(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    gender: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]
    country_id: Optional[int]


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
    brand_logo: FilePath  # Path to the uploaded image on the server
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CarBrandUpdate(BaseModel):
    name: Optional[str]
    country_name: Optional[str]
    brand_logo: Optional[str]
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
    car_brand_id: str
    car_model_id: str
    trim_code_name: str
    trim_name: str
    engine: Optional[str] = None
    trim_hp: Optional[str] = None
    engine_displacement: str
    curb_weight: Optional[str] = None
    trim_production_years: Optional[str] = None
    created_at: Optional[datetime] = None


class CarTrimUpdate(BaseModel):
    car_brand_id: Optional[int] = None
    car_model_id: Optional[int] = None
    trim_name: Optional[str] = None
    engine: Optional[str] = None
    curb_weight: Optional[str] = None
    trim_hp: Optional[str] = None
    updated_at: Optional[datetime] = None


class Feature(BaseModel):
    feature_name: str


class CarStandardFeaturesBase(BaseModel):
    features: List[Feature]
    created_at: Optional[datetime] = None


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


class CarForSaleBase(BaseModel):
    user_id: int
    car_brand_id: int
    car_model_id: int
    car_trim_id: Optional[int]
    car_year: str
    car_mileage: str
    car_price: str
    car_currency: str
    car_location: str
    # car_images: List[str]
    car_standard_features: List[str]
    car_fuel_type_id: int
    car_exterior_color: str
    car_interior_color: str
    car_transmission: str
    car_engine_capacity: str
    car_drive_train: str
    car_fuel_consumption: str
    car_vin_number: str
    car_registration_number: str
    car_insurance: str
    car_control_technique: str
    car_user_type: str
    car_accident_history: str
    inspection_note: str
    seller_type: str
    seller_phone_number: str
    seller_email: str
    seller_address: str
    car_condition: str
    car_seller_name: str

    class Config:
        from_attributes = True


class CarSellImagesBase(BaseModel):
    car_for_sale_id: int
    car_image: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class OTPVerificationCreate(BaseModel):
    phone_number: str
    otp_code: str
    verified: bool
    created_at: Optional[datetime] = None


class OTPVerificationUpdate(BaseModel):
    phone_number: str
    otp_code: int


class CarBodyTypeCreate(BaseModel):
    body_type_name: str
    body_type_image: str


class CarBodyTypeUpdate(BaseModel):
    body_type_name: Optional[str] = None
    body_type_image: Optional[str] = None
    updated_at: Optional[datetime] = None


class BookATestDriveCreate(BaseModel):
    user_id: int
    car_id: str
    phone_number: str
    location_choice: str
    booking_status: Optional[str] = None
    date: str
    time: str


class BookATestDriveUpdateBookingStatus(BaseModel):
    booking_status: str


class ImportOnOrderCreate(BaseModel):
    user_id: int
    price_range: str
    fuel_type: str
    transmission_type: str
    car_brand_id: int
    car_model_id: int
    car_trim_id: int
    manufacture_year_from: str
    manufacture_year_to: str
    kilometers_from: str
    kilometers_to: str
    names: str
    phone_number: str
    email: str
    exterior_color: str
    order_note: str
    car_color: str
    order_status: Optional[str] = None


class ImportOnOrderUpdateStatus(BaseModel):
    order_status: str


class TaxCalculatorCreate(BaseModel):
    user_id: int
    car_brand_id: int
    car_model_id: int
    car_trim_id: int
    weight: int
    engine_cc: int
    year_of_manufacture: int
    price_when_new: int
    amortisation_period: str
    current_residual_value: int
    freight_cost: int
    insurance: int
    cif_kigali: int
    current_value: int
    quitus_fiscal: str
    vehicle_category: str


class BookRentalCarCreate(BaseModel):
    user_id: int
    car_id: str
    phone_number: str
    car_delivery_choice: str
    start_date: str
    start_time: Optional[str] = None
    end_date: str
    end_time: Optional[str] = None


class BookRentalCarUpdate(BaseModel):
    booking_status: str


class CarToBeSoldCreate(BaseModel):
    car_info_name: str
    manufacture_year: str
    car_brand_id: int
    car_model_id: int
    car_trim_id: int
    selling_price: str
    kilometers: str
    transmission_type: str
    fuel_type: str
    exterior_color: str
    interior_color: str
    seller_name: str
    seller_phone_number: str
    seller_note: str
    seller_email: str