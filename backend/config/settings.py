import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Ensure backend .env is loaded
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables with fail-fast validation."""

    def __init__(self) -> None:
        raw_issuer = os.getenv("CLERK_ISSUER")
        if not raw_issuer or not raw_issuer.strip():
            raise RuntimeError(
                "CLERK_ISSUER is not set. Please configure it in your environment or .env file."
            )

        issuer = raw_issuer.strip().rstrip("/")
        if not issuer.startswith("https://"):
            raise ValueError(
                f"CLERK_ISSUER must start with 'https://', got: '{issuer}'"
            )
        self.clerk_issuer: str = issuer

        # Parse CORS_ORIGINS as a comma-separated list
        raw_cors = os.getenv("CORS_ORIGINS")
        if raw_cors is None:
            self.cors_origins: List[str] = [
                "http://localhost:3000",
                "http://localhost:5173",
            ]
        else:
            origins = [o.strip() for o in raw_cors.split(",") if o.strip()]
            # Disallow wildcard origins per security requirements
            origins = [o for o in origins if o != "*"]
            if not origins:
                self.cors_origins = [
                    "http://localhost:3000",
                ]
            else:
                self.cors_origins = origins

        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/neuroteach_db",
        )


def get_settings() -> Settings:
    return Settings()


# Lazy-loaded or initialized settings instance
try:
    settings = get_settings()
except RuntimeError:
    # If CLERK_ISSUER is not yet in environment (e.g. during certain unit test setups),
    # settings will be instantiated when accessed or can be initialized when env is ready.
    settings = None  # type: ignore
