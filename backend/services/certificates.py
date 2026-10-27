"""Certificate generation and issuance service."""

from datetime import date, datetime, timezone
import io
import logging
from pathlib import Path
from typing import Union
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models.certificate import Certificate
from models.challenge import Challenge
from models.completed_challenge import CompletedChallenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User
from services.storage import upload_image

logger = logging.getLogger(__name__)


class ModuleNotFound(Exception):
    """Raised when the specified module_id does not exist."""


def _get_font_path(font_filename: str) -> Path:
    """Resolve font path relative to source file location, reaching repo root fonts/."""
    # services/certificates.py -> services -> backend -> repo_root (e.g. .github) -> fonts
    font_path = Path(__file__).resolve().parent.parent.parent / "fonts" / font_filename
    if not font_path.exists():
        raise FileNotFoundError(f"Required font file not found: {font_path}")
    return font_path


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    initial_size: int,
    max_width: int = 1000,
    min_size: int = 26,
    step: int = 13,
) -> ImageFont.FreeTypeFont:
    """Reduce font size in steps of 13 until text width is within max_width or min_size is reached."""
    current_size = initial_size
    while current_size > min_size:
        font = ImageFont.truetype(str(font_path), size=current_size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        current_size -= step
    return ImageFont.truetype(str(font_path), size=min_size)


def generate_certificate_image(
    user_name: str,
    module_title: str,
    date_val: Union[str, date, datetime],
) -> bytes:
    """Generate a 1200 x 850 certificate PNG image as bytes.

    - Uses PlayerSansMono8x13-Bold.ttf for learner name and module title.
    - Uses PlayerSansMono8x13-Classic.ttf for the date and labels.
    - Centers text and reduces font size in steps of 13 down to 26 if width exceeds ~1000 px.
    """
    bold_font_path = _get_font_path("PlayerSansMono8x13-Bold.ttf")
    classic_font_path = _get_font_path("PlayerSansMono8x13-Classic.ttf")

    # Format date string
    if isinstance(date_val, (date, datetime)):
        date_str = date_val.strftime("%B %d, %Y")
    else:
        date_str = str(date_val)

    width, height = 1200, 850
    img = Image.new("RGB", (width, height), color=(15, 23, 42))  # slate-900
    draw = ImageDraw.Draw(img)

    # Decorative double border
    draw.rectangle([30, 30, width - 30, height - 30], outline=(56, 189, 248), width=3)
    draw.rectangle([42, 42, width - 42, height - 42], outline=(30, 41, 59), width=1)

    # Fonts sizing with dynamic fitting
    font_header = ImageFont.truetype(str(bold_font_path), size=39)
    font_label = ImageFont.truetype(str(classic_font_path), size=26)
    font_name = _fit_font(draw, user_name, bold_font_path, initial_size=78)
    font_module = _fit_font(draw, module_title, bold_font_path, initial_size=52)
    font_date = _fit_font(draw, date_str, classic_font_path, initial_size=39)

    # Render centered certificate text
    draw.text((600, 130), "CERTIFICATE OF COMPLETION", font=font_header, fill=(56, 189, 248), anchor="mm")
    draw.text((600, 230), "PROUDLY PRESENTED TO", font=font_label, fill=(148, 163, 184), anchor="mm")
    draw.text((600, 335), user_name, font=font_name, fill=(248, 250, 252), anchor="mm")
    draw.text((600, 445), "FOR SUCCESSFULLY COMPLETING THE MODULE", font=font_label, fill=(148, 163, 184), anchor="mm")
    draw.text((600, 540), module_title, font=font_module, fill=(56, 189, 248), anchor="mm")
    draw.text((600, 670), date_str, font=font_date, fill=(203, 213, 225), anchor="mm")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def is_module_completed(session: Session, user_id: int, module_id: int) -> bool:
    """Return True if the module exists, has >=1 challenge, and all challenges are completed by user."""
    module = session.get(Module, module_id)
    if not module:
        return False

    challenge_ids_stmt = (
        select(Challenge.id)
        .join(SubModule, Challenge.sub_module_id == SubModule.id)
        .where(SubModule.module_id == module_id)
    )
    challenge_ids = set(session.exec(challenge_ids_stmt).all())

    # An empty module never counts as complete
    if not challenge_ids:
        return False

    completed_ids_stmt = select(CompletedChallenge.challenge_id).where(
        CompletedChallenge.user_id == user_id,
        CompletedChallenge.challenge_id.in_(challenge_ids),
    )
    completed_ids = set(session.exec(completed_ids_stmt).all())

    return challenge_ids.issubset(completed_ids)


def issue_certificate(session: Session, user: User, module_id: int) -> Certificate:
    """Issue a certificate to user for a completed module.

    1. Validate module exists; raise ModuleNotFound if not.
    2. If certificate already exists for user and module, return it.
    3. Load module title and user display name.
    4. Generate image, upload via storage service, insert Certificate row and commit.
    5. Handle concurrent duplicate insert IntegrityError.
    """
    # 1. Validate module first
    module = session.get(Module, module_id)
    if not module:
        raise ModuleNotFound(f"Module with id {module_id} does not exist.")

    # 2. Return existing certificate if already issued
    existing_cert = session.exec(
        select(Certificate).where(
            Certificate.user_id == user.id,
            Certificate.module_id == module_id,
        )
    ).first()
    if existing_cert:
        return existing_cert

    # 3. Determine display name and module title
    raw_name = getattr(user, "name", "") or ""
    user_name = raw_name.strip() if raw_name.strip() else user.email.split("@")[0]
    module_title = module.title
    issue_time = datetime.now(timezone.utc)

    # 4. Generate image, upload, insert, commit
    image_bytes = generate_certificate_image(
        user_name=user_name,
        module_title=module_title,
        date_val=issue_time,
    )
    image_name = f"certificate_user_{user.id}_module_{module_id}"
    image_url = upload_image(image_bytes, image_name)

    cert = Certificate(
        user_id=user.id,
        module_id=module_id,
        image_url=image_url,
        issued_at=issue_time,
    )
    session.add(cert)

    # 5. Commit with IntegrityError handling for concurrent duplicate inserts
    try:
        session.commit()
        session.refresh(cert)
        return cert
    except IntegrityError as exc:
        session.rollback()
        existing = session.exec(
            select(Certificate).where(
                Certificate.user_id == user.id,
                Certificate.module_id == module_id,
            )
        ).first()
        if existing:
            return existing
        raise exc
