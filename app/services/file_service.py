from pathlib import Path
import uuid

from fastapi import UploadFile

# Upload Folder
UPLOAD_DIR = Path("app/uploads")

# Automatically create uploads folder
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = [".pdf"]

# Maximum Upload Size (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


class FileService:

    @staticmethod
    async def validate_pdf(file: UploadFile):
        """
        Validate uploaded PDF.
        """

        if file.filename is None:
            return False, "Invalid file."

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            return False, "Only PDF files are allowed."

        return True, None

    @staticmethod
    async def save_pdf(file: UploadFile):
        """
        Save PDF securely with UUID filename.
        """

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            return False, None, "Maximum upload size is 5 MB."

        unique_filename = f"{uuid.uuid4()}.pdf"

        file_path = UPLOAD_DIR / unique_filename

        with open(file_path, "wb") as pdf_file:
            pdf_file.write(content)

        return True, unique_filename, None

    @staticmethod
    def get_file_path(filename: str):
        """
        Return absolute file path.
        """

        return UPLOAD_DIR / filename

    @staticmethod
    def delete_file(filename: str):
        """
        Delete uploaded file.
        """

        file_path = UPLOAD_DIR / filename

        if file_path.exists():
            file_path.unlink()

            return True

        return False
    