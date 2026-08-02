import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME", "adria_clean")
    
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    CLOUDINARY_CLOUD_NAME=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    CLOUDINARY_API_KEY.environ.get("CLOUDINARY_API_KEY"),
    CLOUDINARY_API_SECRET=os.environ.get("CLOUDINARY_API_SECRET"),
    SECURE=True,
