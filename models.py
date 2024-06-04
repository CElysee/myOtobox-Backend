from datetime import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    phone_number = Column(String(50), nullable=True)
    firstName = Column(String(50))
    lastName = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    password = Column(String(250))
    gender = Column(String(50))
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_login = Column(DateTime)
    deleted = Column(Boolean)

    country = relationship("Country", back_populates="user")
    car_for_sale = relationship("CarForSale", back_populates="user")
    cars_for_rent = relationship("CarsForRent", back_populates="user")
    book_a_test_drive = relationship("BookATestDrive", back_populates="user")
    import_on_order = relationship("ImportOnOrder", back_populates="user")
    tax_calculator = relationship("TaxCalculator", back_populates="user")


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
    brand_logo = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_model = relationship("CarModel", back_populates="car_brand")
    car_trim = relationship("CarTrim", back_populates="car_brand")
    car_for_sale = relationship("CarForSale", back_populates="car_brand")
    cars_for_rent = relationship("CarsForRent", back_populates="car_brand")
    import_on_order = relationship("ImportOnOrder", back_populates="car_brand")
    tax_calculator = relationship("TaxCalculator", back_populates="car_brand")


class CarModel(Base):
    __tablename__ = "car_models"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("car_brands.id"), nullable=True)
    brand_model_name = Column(String(50))
    production_years = Column(String(50), nullable=True)
    brand_model_image = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_brand = relationship("CarBrand", back_populates="car_model")
    car_trim = relationship("CarTrim", back_populates="car_model")
    car_for_sale = relationship("CarForSale", back_populates="car_model")
    cars_for_rent = relationship("CarsForRent", back_populates="car_model")
    import_on_order = relationship("ImportOnOrder", back_populates="car_model")
    tax_calculator = relationship("TaxCalculator", back_populates="car_model")


class CarTrim(Base):
    __tablename__ = "car_trims"

    id = Column(Integer, primary_key=True, index=True)
    car_brand_id = Column(Integer, ForeignKey("car_brands.id"))
    car_model_id = Column(Integer, ForeignKey("car_models.id"))
    trim_name = Column(String(50))
    engine = Column(String(50), nullable=True)
    curb_weight = Column(String(50), nullable=True)
    trim_hp = Column(String(50), nullable=True)
    trim_production_years = Column(String(50), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_brand = relationship("CarBrand", back_populates="car_trim")
    car_model = relationship("CarModel", back_populates="car_trim")
    car_for_sale = relationship("CarForSale", back_populates="car_trim")
    cars_for_rent = relationship("CarsForRent", back_populates="car_trim")
    import_on_order = relationship("ImportOnOrder", back_populates="car_trim")
    tax_calculator = relationship("TaxCalculator", back_populates="car_trim")


class CarStandardFeatures(Base):
    __tablename__ = "car_standard_features"

    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_sell_standard_features = relationship(
        "CarSellStandardFeatures", back_populates="car_standard_features"
    )
    car_rent_standard_features = relationship("CarRentStandardFeatures", back_populates="car_standard_features")


class CarFuelType(Base):
    __tablename__ = "car_fuel_type"

    id = Column(Integer, primary_key=True, index=True)
    fuel_type = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class CarForSale(Base):
    __tablename__ = "car_for_sale"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_number = Column(Text)
    car_name_info = Column(String(50))
    car_year = Column(String(50))
    car_brand_id = Column(Integer, ForeignKey("car_brands.id"))
    car_model_id = Column(Integer, ForeignKey("car_models.id"))
    car_trim_id = Column(Integer, ForeignKey("car_trims.id"))
    car_price = Column(String(50))
    car_mileage = Column(String(50))
    car_vin_number = Column(String(50))
    car_transmission = Column(String(50))
    car_drive_train = Column(String(50))
    car_fuel_type = Column(String(50))
    car_fuel_consumption = Column(String(50))
    car_engine_capacity = Column(String(50))
    car_interior_color = Column(String(50))
    car_exterior_color = Column(String(50))
    car_body_type = Column(String(50))
    car_location = Column(String(50))
    car_registration_number = Column(String(50))
    car_insurance = Column(String(50))
    car_control_technique = Column(String(50))
    seller_phone_number = Column(String(50))
    seller_email = Column(String(50))
    car_status = Column(String(50))
    car_condition = Column(String(50))
    car_seller_name = Column(String(50))
    featured = Column(Boolean)
    seller_note = Column(Text)
    cover_image = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="car_for_sale")
    car_brand = relationship("CarBrand", back_populates="car_for_sale")
    car_model = relationship("CarModel", back_populates="car_for_sale")
    car_trim = relationship("CarTrim", back_populates="car_for_sale")
    car_sell_standard_features = relationship(
        "CarSellStandardFeatures", back_populates="car_for_sale"
    )
    car_sell_images = relationship("CarSellImages", back_populates="car_for_sale")
    book_a_test_drive = relationship("BookATestDrive", back_populates="car_for_sale")
    
    
class CarsForRent(Base):
    __tablename__ = "cars_for_rent"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_number = Column(Text)
    car_name_info = Column(String(50))
    car_year = Column(String(50))
    car_brand_id = Column(Integer, ForeignKey("car_brands.id"))
    car_model_id = Column(Integer, ForeignKey("car_models.id"))
    car_trim_id = Column(Integer, ForeignKey("car_trims.id"))
    car_price_per_day = Column(String(50))
    car_price_per_week = Column(String(50))
    car_price_per_month= Column(String(50))
    car_price_per_day_up_country= Column(String(50))
    car_price_per_week_up_country= Column(String(50))
    car_price_per_month_up_country= Column(String(50))
    car_mileage = Column(String(50))
    car_vin_number = Column(String(50))
    car_transmission = Column(String(50))
    car_drive_train = Column(String(50))
    car_fuel_type = Column(String(50))
    car_fuel_consumption = Column(String(50))
    car_engine_capacity = Column(String(50))
    car_interior_color = Column(String(50))
    car_exterior_color = Column(String(50))
    car_body_type = Column(String(50))
    car_location = Column(String(50))
    car_registration_number = Column(String(50))
    car_insurance = Column(String(50))
    car_control_technique = Column(String(50))
    renter_phone_number = Column(String(50))
    renter_email = Column(String(50))
    car_status = Column(String(50))
    car_condition = Column(String(50))
    car_renter_name = Column(String(50))
    featured = Column(Boolean)
    renter_note = Column(Text)
    cover_image = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="cars_for_rent")
    car_brand = relationship("CarBrand", back_populates="cars_for_rent")
    car_model = relationship("CarModel", back_populates="cars_for_rent")
    car_trim = relationship("CarTrim", back_populates="cars_for_rent")
    car_rent_standard_features = relationship(
        "CarRentStandardFeatures", back_populates="cars_for_rent"
    )
    car_rent_images = relationship("CarRentImages", back_populates="cars_for_rent")    


class CarSellStandardFeatures(Base):
    __tablename__ = "car_sell_standard_features"

    id = Column(Integer, primary_key=True, index=True)
    car_for_sale_id = Column(Integer, ForeignKey("car_for_sale.id"))
    car_standard_features_id = Column(Integer, ForeignKey("car_standard_features.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_for_sale = relationship(
        "CarForSale", back_populates="car_sell_standard_features"
    )
    car_standard_features = relationship(
        "CarStandardFeatures", back_populates="car_sell_standard_features"
    )
    
class CarRentStandardFeatures(Base):
    __tablename__ = "car_rent_standard_features"

    id = Column(Integer, primary_key=True, index=True)
    car_for_rent_id = Column(Integer, ForeignKey("cars_for_rent.id"))
    car_standard_features_id = Column(Integer, ForeignKey("car_standard_features.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    cars_for_rent = relationship(
        "CarsForRent", back_populates="car_rent_standard_features"
    )
    car_standard_features = relationship(
        "CarStandardFeatures", back_populates="car_rent_standard_features"
    )    


class CarSellImages(Base):
    __tablename__ = "car_sell_images"

    id = Column(Integer, primary_key=True, index=True)
    car_for_sale_id = Column(Integer, ForeignKey("car_for_sale.id"))
    image_name = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_for_sale = relationship("CarForSale", back_populates="car_sell_images")

class CarRentImages(Base):
    __tablename__ = "car_rent_images"

    id = Column(Integer, primary_key=True, index=True)
    car_for_rent_id = Column(Integer, ForeignKey("cars_for_rent.id"))
    image_name = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    cars_for_rent = relationship("CarsForRent", back_populates="car_rent_images")
    
class OTPVerification(Base):
    __tablename__ = "otp_verification"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50))
    otp_code = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    verified = Column(Boolean)
    verified_at = Column(DateTime)
    deleted = Column(Boolean)


class CarBodyType(Base):
    __tablename__ = "car_body_type"

    id = Column(Integer, primary_key=True, index=True)
    body_type_name = Column(String(50))
    body_type_image = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BookATestDrive(Base):
    __tablename__ = "book_a_test_drive"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    car_id = Column(Integer, ForeignKey("car_for_sale.id"))
    date = Column(DateTime)
    time = Column(String(50))
    phone_number = Column(String(50))
    location_choice = Column(String(50))
    booking_status = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    car_for_sale = relationship("CarForSale", back_populates="book_a_test_drive")
    user = relationship("User", back_populates="book_a_test_drive")
    
    
class ImportOnOrder(Base):
    __tablename__ = "import_on_order"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    price_range = Column(String(50))
    fuel_type = Column(String(50))
    transmission_type = Column(String(50))
    car_brand_id = Column(Integer, ForeignKey("car_brands.id"), nullable=True)
    car_model_id = Column(Integer, ForeignKey("car_models.id"), nullable=True)
    car_trim_id = Column(Integer, ForeignKey("car_trims.id"), nullable=True)
    manufacture_year_from = Column(String(50))
    manufacture_year_to = Column(String(50))
    kilometers_from = Column(String(50))
    kilometers_to = Column(String(50))
    names = Column(String(50))
    phone_number = Column(String(50))
    email = Column(String(50))
    exterior_color = Column(String(50))
    car_color = Column(String(50))
    order_note =  Column(Text)
    order_status = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    user = relationship("User", back_populates="import_on_order")
    car_brand = relationship("CarBrand", back_populates="import_on_order")
    car_model = relationship("CarModel", back_populates="import_on_order")
    car_trim = relationship("CarTrim", back_populates="import_on_order") 
    
    
class TaxCalculator(Base):
    __tablename__ = "tax_calculator"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    car_brand_id = Column(Integer, ForeignKey("car_brands.id"))
    car_model_id = Column(Integer, ForeignKey("car_models.id"))
    car_trim_id = Column(Integer, ForeignKey("car_trims.id"), nullable=True)
    weight = Column(String(50))
    engine_cc = Column(String(50))
    year_of_manufacture = Column(String(50))
    price_when_new = Column(String(50))
    amortisation_period = Column(String(50))
    current_residual_value = Column(String(50))
    freight_cost = Column(String(50))
    insurance = Column(String(50))
    cif_kigali = Column(String(50))
    current_value = Column(String(50))
    quitus_fiscal = Column(String(50))
    vehicle_category = Column(Text)
    import_duty_tax = Column(String(50))
    excise_duty_tax = Column(String(50))
    vat_tax = Column(String(50))
    idl_tax = Column(String(50))
    withholding_tax = Column(String(50))
    plate_fee = Column(String(50))
    aul_tax = Column(String(50))
    total_tax = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    user = relationship("User", back_populates="tax_calculator")
    car_brand = relationship("CarBrand", back_populates="tax_calculator")
    car_model = relationship("CarModel", back_populates="tax_calculator")
    car_trim = relationship("CarTrim", back_populates="tax_calculator")    