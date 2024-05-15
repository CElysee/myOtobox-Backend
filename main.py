from fastapi import FastAPI, HTTPException

# from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from fastapi.staticfiles import StaticFiles

from routes import (
    auth,
    country,
    CarBrand,
    CarModel,
    CarTrim,
    CarStandardFeautures,
    CarFuelType,
    CarForSale,
    CarBodyType,
    BookATestDrive,
    ImportOnOrder,
    TaxCalculator,
    DashboardStats,
)
from routes.auth import get_current_user, user_dependency

import models
from database import engine, db_dependency
import os
from cachetools import TTLCache

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Configure CORS
origins = [
    "http://localhost:5173",  # Your frontend origin
    # Add other allowed origins as needed
]
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(country.router)
app.include_router(CarBrand.router)
app.include_router(CarModel.router)
app.include_router(CarTrim.router)
app.include_router(CarStandardFeautures.router)
app.include_router(CarFuelType.router)
app.include_router(CarForSale.router)
app.include_router(CarBodyType.router)
app.include_router(BookATestDrive.router)
app.include_router(ImportOnOrder.router)
app.include_router(TaxCalculator.router)
app.include_router(DashboardStats.router)


app.mount("/CarSellImages", StaticFiles(directory="CarSellImages"), name="images")
app.mount("/BrandLogo", StaticFiles(directory="BrandLogo"), name="images")
app.mount("/BrandModel", StaticFiles(directory="BrandModel"), name="images")
app.mount("/BodyTypeImage", StaticFiles(directory="BodyTypeImage"), name="images")
# Your cache instance, replace with your specific cache implementation
cache = TTLCache(
    maxsize=100, ttl=600
)  # TTLCache as an example, use your actual cache implementation


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    user = db.query(models.User).all()
    return user


@app.get("/UserProfiles/{filename}")
async def get_image(filename: str):
    """Get an image by filename."""
    if not os.path.exists(f"CarSellImages/{filename}"):
        raise HTTPException(status_code=404, detail="Image not found")

    with open(f"CarSellImages/{filename}", "rb") as f:
        image_data = f.read()

    return image_data


@app.get("/BrandLogo/{filename}")
async def get_image(filename: str):
    """Get an image by filename."""
    if not os.path.exists(f"./BrandLogo/{filename}"):
        raise HTTPException(status_code=404, detail="Image not found")

    with open(f"BrandLogo/{filename}", "rb") as f:
        image_data = f.read()

    return image_data


@app.get("/BrandModel/{filename}")
async def get_image(filename: str):
    """Get an image by filename."""
    if not os.path.exists(f"BrandModel/{filename}"):
        raise HTTPException(status_code=404, detail="Image not found")

    with open(f"BrandModel/{filename}", "rb") as f:
        image_data = f.read()

    return image_data


@app.get("/BodyTypeImage/{filename}")
async def get_image(filename: str):
    """Get an image by filename."""
    if not os.path.exists(f"BodyTypeImage/{filename}"):
        raise HTTPException(status_code=404, detail="Image not found")

    with open(f"BodyTypeImage/{filename}", "rb") as f:
        image_data = f.read()

    return image_data


@app.post("/clear_cache")
def clear_cache():
    cache.clear()
    return {"message": "Cache cleared successfully"}
