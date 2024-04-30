# import sys
# sys.path.append("..")
from datetime import datetime, timedelta
import calendar
import random
from typing import Annotated, Any, List
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

import models
import schemas
from database import SessionLocal
import logging
import os
import uuid
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from email.mime.image import MIMEImage
import requests
from schemas import UserCreate, UserUpdate

router = APIRouter(
    tags=["Auth"],
    prefix='/auth'
)

load_dotenv()  # Load environment variables from .env

SECRET_KEY = 'a0ca9d98526e3a3d00cd899a53994e9a574fdecef9abe8bc233b1c262753cd2a'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token ')
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def authenticated_user(username: str, password: str, db):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", )
    if not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", )
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta, email: str, role: str, name: str):
    encode = {'sub': username, 'id': user_id, 'email': email, 'role': role, 'name': name}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_hashed_password(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def get_user_by_email(email: str, password: str, db: Session):
    query = db.query(models.User).filter(models.User.email == email)
    user = query.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", )
    if not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password", )
    user.last_login = datetime.now()
    db.commit()
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        name: str = payload.get('name')
        user = db.query(models.User).filter(models.User.username == username).first()
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        # return {'username': username, 'id': user_id, 'user_role': user_role}
        return user

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


async def get_current_active_user(
        current_user: Annotated[schemas.UserOut, Depends(get_current_user)]
):
    return current_user


user_dependency = Annotated[dict, Depends(get_current_user)]


class Token(BaseModel):
    access_token: str
    token_type: str
    # role: str


class UserToken(BaseModel):
    access_token: str
    token_type: str
    role: str
    userId: int
    name: str


UPLOAD_FOLDER = "CarSellImages"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def save_uploaded_file(file: UploadFile):
    file_extension = file.filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, random_filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return random_filename


def read_email_template():
    template_path = os.path.join(os.getcwd(), "templates", "email", "email.html")
    with open(template_path, "r") as file:
        return file.read()


def send_sms(phone_number, message):
    url = "https://api.mista.io/sms"
    api_key = os.getenv('API_KEY')  # API key
    sender_id = os.getenv('SENDER_ID')  # Sender ID

    payload = {
        'action': 'send-sms',
        'to': phone_number,
        'from': sender_id,
        'sms': message,
        'unicode': '0'
    }
    headers = {
        'x-api-key': api_key
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Error sending SMS: {e}")
        return None


def generate_random_mixed():
    random_number = random.randint(10, 9999)
    return random_number


@router.get('/all')
async def all_users(db: db_dependency):
    # all_users = db.query(models.User).all()
    all_users = db.query(models.User).filter(models.User.role != "admin").order_by(models.User.id.desc()).all()
    user_count = db.query(models.User).filter(models.User.role != "admin").count()
    active_users = db.query(models.User).filter(models.User.is_active == True).filter(models.User.role != "admin").count()
    recently_registered = db.query(models.User).filter(models.User.role != "admin").filter(models.User.created_at >= datetime.now() - timedelta(days=7)).count()
    results_user_count  = {"user_count": user_count, "active_users": active_users, "recently_registered": recently_registered}
    users = []
    for user in all_users:
        last_login = None
        if user.last_login:
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S')
        results = {
            "id": user.id,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "last_login": last_login,
            "gender":user.gender,
            "role": user.role,
            "country_id": user.country_id,
            "created_at": user.created_at,
            "country_name": db.query(models.Country).filter(models.Country.id == user.country_id).first().name
        }
        users.append(results)
    return {"users": users, "counts": results_user_count}

@router.get("/all_admin_users")
async def all_admin_users(db: db_dependency):
    all_users = db.query(models.User).filter(models.User.role == "admin").all()
    user_count = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    recently_registered = db.query(models.User).filter(models.User.created_at >= datetime.now() - timedelta(days=7)).count()
    results_user_count  = {"user_count": user_count, "active_users": active_users, "recently_registered": recently_registered}
    users = []
    for user in all_users:
        last_login = None
        if user.last_login:
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S')
        results = {
            "id": user.id,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "role": user.role,
            "gender": user.gender,
            "country_id": user.country_id,
            "country_name": db.query(models.Country).filter(models.Country.id == user.country_id).first().name
        }
        users.append(results)
    return {"users": users, "counts": results_user_count}

# router.get("/all_users")
# async def all_users(db: db_dependency):
#     all_users = db.query(models.User).filter(models.User.role != "admin").all()
#     users = []
#     for user in all_users:
#         last_login = None
#         if user.last_login:
#             last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S')
#         results = {
#             "id": user.id,
#             "firstName": user.firstName,
#             "lastName": user.lastName,
#             "email": user.email,
#             "phone_number": user.phone_number,
#             "last_login": last_login,
#             "is_active": user.is_active,
#             "created_at": user.created_at,
#             "role": user.role,
#         }
#         users.append(results)
#     return users

@router.post('/send_verification_code/{phone_number}')
async def verify_phone_number(phone_number: str, db: db_dependency):
    new_phone = "250" + phone_number
    user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    if user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Phone number already exist")
    else:
        verification_code = generate_random_mixed()
        verification_message = f"Your verification code is {verification_code}"
        # Send SMS with verification code
        sms_result = send_sms(new_phone, verification_message)
        if sms_result:
            # Save the verification code in the database
            new_verification = models.OTPVerification(
                phone_number=new_phone,
                otp_code=verification_code,
                verified=False,
                created_at=datetime.now()
            )
            db.add(new_verification)
            db.commit()
            # Assuming SMS was sent successfully
            # Here, you can save the verification_code in the database or elsewhere for future comparison
            return {"detail": "Verification code sent successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to send verification code")


@router.post('/otp_verification')
async def verify_phone_number(opt_verify: schemas.OTPVerificationUpdate, db: db_dependency):
    verify_number = db.query(models.OTPVerification).filter(
        models.OTPVerification.phone_number == opt_verify.phone_number).first()
    verify_opt = db.query(models.OTPVerification).filter(models.OTPVerification.phone_number == opt_verify.phone_number,
                                                         models.OTPVerification.otp_code == opt_verify.otp_code).first()
    if verify_number is None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Phone number not found")
    elif verify_opt is None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid OTP code")

    if verify_opt:
        verify_opt.verified = True
        verify_opt.verified_at = datetime.now()
        db.commit()
        return {"detail": "Phone number verified successfully"}


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: Session = Depends(get_db), user_request: schemas.UserCreate = Depends(),
                      profile_picture: UploadFile = File(...)):
    try:
        picture_path = save_uploaded_file(profile_picture)
        hashed_password = get_hashed_password(user_request.password)
        new_user = models.User(
            username=user_request.username,
            email=user_request.email,
            name=user_request.name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            password=hashed_password,
            role=user_request.role,
            country_id=user_request.country_id,
            phone_number=user_request.phone_number,
            is_active=True
        )
        db.add(new_user)

        response_data = schemas.UserOut(
            message="User successfully created",
            id=new_user.id,
            user_id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            phone_number=new_user.phone_number,
            username=new_user.username,
            role=new_user.role,
            created_at=new_user.created_at,
            is_active=new_user.is_active,
        )

        smtp_server = os.getenv("MAILGUN_SMTP_SERVER")
        smtp_port = int(os.getenv("MAILGUN_SMTP_PORT"))
        smtp_username = os.getenv("MAILGUN_SMTP_USERNAME")
        smtp_password = os.getenv("MAILGUN_SMTP_PASSWORD")

        # Read the email template
        email_template_content = read_email_template()

        # Create a Jinja2 environment and load the template
        env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), "templates", "email")))
        template = env.from_string(email_template_content)

        message = "We are absolutely thrilled to welcome you to our vibrant community! Your registration has been confirmed, and we're excited to have you on board. \n At Mentor.rw, we believe in fostering a supportive and engaging environment where members like you can connect, learn, and collaborate. Your presence adds immense value to our community, and we can't wait to see the positive impact we'll create together."
        # Render the template with the provided data
        email_content = template.render(message=message, name=user_request.name)

        # Create the email content
        email = EmailMessage()
        email["From"] = f"Mentor.rw <{smtp_username}>"
        email["To"] = user_request.email
        email["Subject"] = "Welcome to Mentor Community - Registration is Completed 🎉"
        email.set_content("This is the plain text content.")
        email.add_alternative(email_content, subtype="html")
        # Attach the image
        image_path = "templates/email/mentorlogo.png"
        with open(image_path, "rb") as img_file:
            image = MIMEImage(img_file.read())
            image.add_header("Content-ID", "mentorlogo.png")
            email.attach(image)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(email)

        return response_data

    except Exception as e:
        db.rollback()
        error_msg = f"Error adding a new user: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg)


@router.post("/create_admin")
async def create_user_admin(user_request: UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = get_hashed_password(user_request.password)
        new_user = models.User(
            username=user_request.email,
            email=user_request.email,
            firstName=user_request.firstName,
            lastName=user_request.lastName,
            password=hashed_password,
            role=user_request.role,
            gender=user_request.gender,
            country_id=user_request.country_id,
            phone_number=user_request.phone_number,
            is_active=True,
            created_at=datetime.now(),
        )
        db.add(new_user)
        db.commit()
        return {"message": "User successfully created"}

    except Exception as e:
        db.rollback()
        error_msg = f"Error adding a new user: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg)

@router.put("/update_user/{user_id}")
async def update_user(user_id: int, user_request: schemas.UserUpdate, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update user data if the corresponding field in user_request is not None
    if user_request.firstName:
        user.firstName = user_request.firstName
    if user_request.lastName:
        user.lastName = user_request.lastName
    if user_request.email:
        user.email = user_request.email
    if user_request.phone_number:
        user.phone_number = user_request.phone_number
    if user_request.role:
        user.role = user_request.role
    if user_request.is_active is not None:
        user.is_active = user_request.is_active
    if user_request.gender:
        user.gender = user_request.gender
    if user_request.country_id:
        user.country_id = user_request.country_id

    db.commit()
    return {"message": "User successfully updated"}
     
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticated_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

    token = create_access_token(user.username, user.id, timedelta(minutes=60), user.email, user.role, user.firstName)

    return {'message': "Successfully Authenticated", 'access_token': token, 'token_type': 'bearer'}


@router.post("/login", response_model=UserToken)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # user = authenticated_user(form_data.username, form_data.password, db)
    user = get_user_by_email(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(user.username, user.id, timedelta(minutes=60), user.email, user.role, user.firstName)

    return {'message': "Successfully Authenticated", 'access_token': token, 'token_type': 'bearer', 'role': user.role,
            'userId': user.id, 'name': user.firstName}


@router.post("/check_username", status_code=status.HTTP_200_OK)
async def check_username(user_request: schemas.UserCheck, db: db_dependency):
    user = db.query(models.User).filter(models.User.email == user_request.email).first()
    if user is None:
        return {'message': "Email not registered"}
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is not yet Approved")
    elif user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username already exist")


@router.get("/users/me", response_model=schemas.UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/users/profile/update_basic_info", status_code=status.HTTP_200_OK)
async def update_profile(
        name: str = Form(None),
        gender: str = Form(None),
        user_id: str = Form(...),
        country_id: int = Form(None),
        languages_id: list = Form(None),
        profile_picture: UploadFile = File(default=None),
        db: Session = Depends(get_db),
):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()

        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Update user and user profile fields
        if name:
            user.name = name
        if country_id:
            user.country_id = country_id
        if gender:
            user_profile.gender = gender  # Assuming you intended to update the country field

        if profile_picture is not None:
            # Save the uploaded profile picture
            picture_path = save_uploaded_file(profile_picture)
            user_profile.profile_picture = picture_path

        # Commit the changes to the database
        db.commit()

        return {"message": "Profile updated successfully"}

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an exception
        raise HTTPException(status_code=500, detail="Error updating user profile")

    finally:
        db.close()

@router.delete("/delete_user/{user_id}")
async def delete_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User successfully deleted"}

@router.get("/user/{user_id}")
async def get_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    results = {
        "id": user.id,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "phone_number": user.phone_number,
        "last_login": user.last_login,
        "created_at": user.created_at,
        "role": user.role,
        "gender": user.gender,
        "country_id": user.country_id,
        "is_active": user.is_active,
        "country_name": db.query(models.Country).filter(models.Country.id == user.country_id).first().name
    }
    return results

@router.get("/user_count")
async def user_count(db: db_dependency):
    user_count = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    recently_registered = db.query(models.User).filter(models.User.created_at >= datetime.now() - timedelta(days=7)).count()
    return {"user_count": user_count, "active_users": active_users, "recently_registered": recently_registered}