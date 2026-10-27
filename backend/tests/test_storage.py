"""Tests for image storage service (stub fallback and Cloudinary upload)."""

import logging
import sys
from unittest.mock import MagicMock, patch
import pytest

# Ensure cloudinary exists in sys.modules so that patch works seamlessly
# regardless of whether cloudinary is installed in the test environment.
if "cloudinary" not in sys.modules:
    _mock_cloudinary = MagicMock()
    _mock_uploader = MagicMock()
    _mock_cloudinary.uploader = _mock_uploader
    sys.modules["cloudinary"] = _mock_cloudinary
    sys.modules["cloudinary.uploader"] = _mock_uploader

from services.storage import StorageUploadError, upload_image


def test_stub_returned_when_all_env_vars_missing(monkeypatch, caplog):
    """When Cloudinary env vars are missing, return stub URL and log a warning."""
    monkeypatch.delenv("CLOUDINARY_CLOUD_NAME", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_KEY", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)

    with caplog.at_level(logging.WARNING):
        url = upload_image(b"image_bytes", "mod1_cert")

    assert url == "https://example.com/certificates/mod1_cert.png"
    assert any("Cloudinary credentials missing" in record.message for record in caplog.records)


def test_stub_returned_when_name_has_png_extension(monkeypatch):
    """Stub URL does not duplicate .png when name already ends with .png."""
    monkeypatch.delenv("CLOUDINARY_CLOUD_NAME", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_KEY", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)

    url = upload_image(b"image_bytes", "mod1_cert.png")
    assert url == "https://example.com/certificates/mod1_cert.png"


@pytest.mark.parametrize(
    "cloud_name, api_key, api_secret",
    [
        ("", "key123", "secret123"),
        ("cloud123", "", "secret123"),
        ("cloud123", "key123", ""),
        ("   ", "key123", "secret123"),
        ("cloud123", "   ", "secret123"),
        ("cloud123", "key123", "   "),
    ],
)
def test_stub_returned_when_any_env_var_missing_or_empty(
    monkeypatch, caplog, cloud_name, api_key, api_secret
):
    """When any of the three credentials is missing or whitespace-only, fall back to stub."""
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", cloud_name)
    monkeypatch.setenv("CLOUDINARY_API_KEY", api_key)
    monkeypatch.setenv("CLOUDINARY_API_SECRET", api_secret)

    with caplog.at_level(logging.WARNING):
        url = upload_image(b"image_bytes", "cert_partial")

    assert url == "https://example.com/certificates/cert_partial.png"
    assert any("Cloudinary credentials missing" in record.message for record in caplog.records)


def test_cloudinary_upload_real_path_mocked(monkeypatch):
    """When all env vars are set, configure and upload via Cloudinary, returning secure_url."""
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "my_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "my_api_key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "my_api_secret")

    expected_url = "https://res.cloudinary.com/my_cloud/image/upload/v12345/certificates/mod_1.png"

    with patch("cloudinary.config") as mock_config, patch(
        "cloudinary.uploader.upload",
        return_value={"secure_url": expected_url},
    ) as mock_upload:
        url = upload_image(b"sample_data", "mod_1")

    assert url == expected_url
    mock_config.assert_called_once_with(
        cloud_name="my_cloud",
        api_key="my_api_key",
        api_secret="my_api_secret",
        secure=True,
    )
    mock_upload.assert_called_once_with(
        b"sample_data",
        folder="certificates",
        public_id="mod_1",
        overwrite=True,
        resource_type="image",
    )


def test_cloudinary_upload_strips_png_suffix_for_public_id(monkeypatch):
    """Public ID derived from name strips trailing .png if present."""
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "my_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "my_api_key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "my_api_secret")

    with patch("cloudinary.config"), patch(
        "cloudinary.uploader.upload",
        return_value={"secure_url": "https://res.cloudinary.com/my_cloud/image.png"},
    ) as mock_upload:
        upload_image(b"sample_data", "my_cert.png")

    mock_upload.assert_called_once_with(
        b"sample_data",
        folder="certificates",
        public_id="my_cert",
        overwrite=True,
        resource_type="image",
    )


def test_cloudinary_upload_failure_raises_clear_exception(monkeypatch):
    """When Cloudinary upload raises an exception, wrap and raise StorageUploadError."""
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "my_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "my_api_key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "my_api_secret")

    with patch("cloudinary.config"), patch(
        "cloudinary.uploader.upload",
        side_effect=RuntimeError("Cloudinary service unavailable"),
    ):
        with pytest.raises(StorageUploadError, match="Failed to upload image 'fail_cert'"):
            upload_image(b"sample_data", "fail_cert")


def test_cloudinary_missing_secure_url_raises_clear_exception(monkeypatch):
    """When response dictionary does not contain secure_url, raise StorageUploadError."""
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "my_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "my_api_key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "my_api_secret")

    with patch("cloudinary.config"), patch(
        "cloudinary.uploader.upload",
        return_value={"url": "http://insecure.url"},
    ):
        with pytest.raises(StorageUploadError, match="missing 'secure_url'"):
            upload_image(b"sample_data", "no_secure_url")


def test_never_log_api_secrets(monkeypatch, caplog):
    """Ensure API keys and secrets are never printed to the logs."""
    fake_key = "sensitive_api_key_xyz"
    fake_secret = "sensitive_api_secret_abc"
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "my_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", fake_key)
    monkeypatch.setenv("CLOUDINARY_API_SECRET", fake_secret)

    with patch("cloudinary.config"), patch(
        "cloudinary.uploader.upload",
        side_effect=Exception("Connection timed out"),
    ):
        with pytest.raises(StorageUploadError):
            upload_image(b"data", "test_cert")

    assert fake_key not in caplog.text
    assert fake_secret not in caplog.text
