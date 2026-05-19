"""File storage service."""
import os
import uuid
from pathlib import Path
from typing import BinaryIO

from app.config import get_settings


ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png", ".zip"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class StorageService:
    """Service for file storage operations."""

    def __init__(self, upload_dir: Path | None = None):
        settings = get_settings()
        self.upload_dir = upload_dir or settings.upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, file_size: int) -> tuple[bool, str]:
        """Validate file extension and size."""
        ext = Path(filename).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Extensión no permitida: {ext}. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"

        if file_size > MAX_FILE_SIZE:
            return False, f"Archivo demasiado grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB"

        return True, ""

    def save_file(self, file: BinaryIO, original_filename: str) -> tuple[str, str]:
        """
        Save file to storage.

        Returns:
            tuple of (ruta_storage, nombre_archivo)
        """
        ext = Path(original_filename).suffix.lower()
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = self.upload_dir / unique_name

        with open(file_path, "wb") as f:
            content = file.read()
            f.write(content)

        return str(file_path), original_filename

    def delete_file(self, ruta_storage: str) -> bool:
        """Delete file from storage."""
        try:
            path = Path(ruta_storage)
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension."""
        ext = Path(filename).suffix.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".zip": "application/zip",
        }
        return mime_types.get(ext, "application/octet-stream")