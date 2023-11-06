from datetime import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    phone_number = Column(String(50), nullable=True)
    name = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    password = Column(String(250))
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_login = Column(DateTime)
    deleted = Column(Boolean)

    country = relationship("Country", back_populates="user")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    code = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="country")


class CarBrand(Base):
    __tablename__ = "car_brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    country_name = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_model = relationship("CarModel", back_populates="car_brand")


class CarModel(Base):
    __tablename__ = "car_models"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("car_brands.id"), nullable=True)
    brand_model_name = Column(String(50))
    production_years = Column(String(50), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_brand = relationship("CarBrand", back_populates="car_model")
    car_trim = relationship("CarTrim", back_populates="car_model")


class CarTrim(Base):
    __tablename__ = "car_trims"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("car_models.id"))
    trim_name = Column(String(50))
    engine = Column(String(50), nullable=True)
    curb_weight = Column(String(50), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_model = relationship("CarModel", back_populates="car_trim")


class CarStandardFeatures(Base):
    __tablename__ = "car_standard_features"

    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class CarFuelType(Base):
    __tablename__ = "car_fuel_type"

    id = Column(Integer, primary_key=True, index=True)
    fuel_type = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
