"""Preview script for certificate image generation."""

import os
import sys
import tempfile
from datetime import datetime, timezone

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.certificates import generate_certificate_image


def main() -> None:
    sample_name = "Ada Lovelace"
    sample_module = "Intro to Machine Learning"
    sample_date = datetime.now(timezone.utc).strftime("%B %d, %Y")

    image_bytes = generate_certificate_image(
        user_name=sample_name,
        module_title=sample_module,
        date_val=sample_date,
    )

    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "preview_certificate.png")
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(output_path)


if __name__ == "__main__":
    main()
