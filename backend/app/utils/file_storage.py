from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.utils.errors import APIError

ALLOWED_FILE_EXTENSIONS = {
    "zip",
    "rar",
    "7z",
    "tar",
    "gz",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "csv",
    "txt",
    "json",
}


def _upload_dir() -> Path:
    return Path(current_app.config["UPLOAD_DIR"]).resolve()


def ensure_upload_dir() -> None:
    _upload_dir().mkdir(parents=True, exist_ok=True)


def _safe_ext(filename: str) -> str:
    if "." not in filename:
        raise APIError("invalid_file", "File extension is required", 422)
    return filename.rsplit(".", 1)[1].lower()


def save_upload(file_obj: FileStorage) -> tuple[str, str, str, int]:
    if not file_obj or not file_obj.filename:
        raise APIError("invalid_file", "File is required", 422)

    original_name = secure_filename(file_obj.filename)
    if not original_name:
        raise APIError("invalid_file", "Invalid file name", 422)

    ext = _safe_ext(original_name)
    if ext not in ALLOWED_FILE_EXTENSIONS:
        raise APIError("unsupported_file_type", f"Unsupported file type: .{ext}", 422)

    data = file_obj.read()
    size = len(data)
    max_bytes = int(current_app.config["MAX_FILE_BYTES"])
    if size == 0:
        raise APIError("invalid_file", "File is empty", 422)
    if size > max_bytes:
        raise APIError(
            "file_too_large",
            f"File exceeds {max_bytes} bytes",
            413,
            details={"max_bytes": max_bytes, "actual_bytes": size},
        )

    storage_name = f"{uuid.uuid4().hex}_{original_name}"
    ensure_upload_dir()
    destination = _upload_dir() / storage_name
    destination.write_bytes(data)
    return str(destination), original_name, (file_obj.mimetype or "application/octet-stream"), size


def delete_file_if_exists(path: str | None) -> None:
    if not path:
        return
    try:
        target = Path(path).resolve()
        uploads = _upload_dir()
        if os.path.commonpath([str(target), str(uploads)]) != str(uploads):
            return
        if target.exists():
            target.unlink()
    except OSError:
        return
