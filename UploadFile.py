import os
import uuid
from fastapi import UploadFile


class FileHandler:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

        # Create the upload folder if it doesn't exist
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

    def save_uploaded_file(self, file: UploadFile):
        file_extension = file.filename.split(".")[-1]
        random_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.upload_folder, random_filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        return random_filename