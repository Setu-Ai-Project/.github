"""Image storage service supporting Cloudinary with fallback to stub URLs."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class StorageUploadError(Exception):
    """Raised when an image upload to storage fails."""


def upload_image(data: bytes, name: str) -> str:
    """Upload an image to Cloudinary if configured, otherwise return a stub URL.

    - If CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET are ALL set (non-empty),
      uploads via the cloudinary package to folder "certificates", public_id derived from `name`,
      with overwrite allowed, returning the secure URL.
    - Otherwise returns 'https://example.com/certificates/<name>.png' and logs a warning (never logging keys).
    - Environment variables are read at call time.
    - If a real upload fails, raises StorageUploadError.
    """
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "").strip()
    api_key = os.getenv("CLOUDINARY_API_KEY", "").strip()
    api_secret = os.getenv("CLOUDINARY_API_SECRET", "").strip()

    clean_name = name.removesuffix(".png") if name.endswith(".png") else name

    if cloud_name and api_key and api_secret:
        try:
            import cloudinary
            import cloudinary.uploader
        except ImportError as exc:
            logger.error("Cloudinary package is not installed.")
            raise StorageUploadError("Cloudinary package is not installed.") from exc

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        try:
            result: dict[str, Any] = cloudinary.uploader.upload(
                data,
                folder="certificates",
                public_id=clean_name,
                overwrite=True,
                resource_type="image",
            )
            secure_url = result.get("secure_url")
            if not secure_url:
                raise StorageUploadError("Cloudinary upload response missing 'secure_url'.")
            return secure_url
        except StorageUploadError:
            raise
        except Exception as exc:
            logger.error("Cloudinary upload failed for %s: %s", clean_name, exc)
            raise StorageUploadError(f"Failed to upload image '{clean_name}' to Cloudinary: {exc}") from exc

    logger.warning(
        "Cloudinary credentials missing or incomplete; falling back to stub certificate URL."
    )
    return f"https://example.com/certificates/{clean_name}.png"
