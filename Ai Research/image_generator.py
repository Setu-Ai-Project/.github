"""
image_generator.py
==================
Module 1: Image Generation from Text Prompt.

This module provides functions to call an image-generation API (Stability AI)
to turn a learner's prompt into an image.

Why this is separate:
In Step 1 of the AI Research Development Plan, image generation is kept completely
independent from similarity evaluation and feedback. This allows testing prompt
generation in isolation, swapping image providers easily, and debugging API errors
without touching the rest of the pipeline.

Usage:
    from image_generator import generate_image

    # Generate an image and save it to disk
    image_bytes = generate_image("A futuristic city floating in the clouds", "output.png")
"""

import os
import io
import requests
from typing import Optional
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env file if present
load_dotenv()


def create_mock_image(prompt: str) -> bytes:
    """
    Creates a simple placeholder image for testing when no API key is provided.
    This allows beginners to test the pipeline locally without paid API credits.

    Args:
        prompt: The text prompt to depict on the placeholder.

    Returns:
        bytes: PNG-encoded image bytes.
    """
    width, height = 512, 512
    # Create an image with a soft blue-violet background
    img = Image.new("RGB", (width, height), color=(64, 86, 161))
    draw = ImageDraw.Draw(img)

    # Draw decorative border
    draw.rectangle([10, 10, width - 10, height - 10], outline=(255, 255, 255), width=3)

    title = "[Mock Mode: Image Generator]"
    subtitle = "API Key not configured - generated placeholder"
    prompt_label = f"Prompt: {prompt[:80]}..." if len(prompt) > 80 else f"Prompt: {prompt}"

    draw.text((30, 40), title, fill=(255, 220, 100))
    draw.text((30, 80), subtitle, fill=(220, 220, 220))
    draw.text((30, 130), prompt_label, fill=(255, 255, 255))

    # Draw a simple geometric representation
    draw.ellipse([180, 220, 332, 372], fill=(100, 180, 246), outline=(255, 255, 255), width=2)
    draw.text((210, 285), "Mock Image", fill=(20, 30, 60))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_image(
    prompt: str,
    output_path: Optional[str] = None,
    api_key: Optional[str] = None,
    aspect_ratio: str = "1:1",
    output_format: str = "png",
) -> bytes:
    """
    Generates an image from a text prompt using the Stability AI Core API.

    If no API key is provided or found in the environment (STABILITY_API_KEY),
    it gracefully falls back to mock mode so beginners can run and inspect the module.

    Args:
        prompt: The text description of the image to generate.
        output_path: Optional file path where the generated image should be saved.
        api_key: Optional Stability AI API key (defaults to STABILITY_API_KEY env var).
        aspect_ratio: Aspect ratio of the generated image (e.g., "1:1", "16:9").
        output_format: Image format ("png" or "jpeg").

    Returns:
        bytes: Raw image file bytes.

    Raises:
        ValueError: If the prompt is empty.
        RuntimeError: If the API call fails unexpectedly.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    key = api_key or os.getenv("STABILITY_API_KEY")

    # Beginner-friendly fallback when no API key is set
    if not key or key == "your_stability_api_key_here":
        print("[image_generator] Notice: STABILITY_API_KEY not found or set to placeholder.")
        print("[image_generator] Generating a test placeholder image in mock mode.")
        image_bytes = create_mock_image(prompt)
        if output_path:
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"[image_generator] Placeholder image saved to: {output_path}")
        return image_bytes

    # Stability AI REST API endpoint
    endpoint = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "authorization": f"Bearer {key}",
        "accept": "image/*",
    }

    data = {
        "prompt": prompt.strip(),
        "output_format": output_format,
        "aspect_ratio": aspect_ratio,
    }

    print(f"[image_generator] Requesting image generation for: '{prompt}'...")
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            files={"none": ""},
            data=data,
            timeout=60,
        )

        if response.status_code == 200:
            image_bytes = response.content
            print("[image_generator] Image generated successfully!")
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                print(f"[image_generator] Image saved to: {output_path}")
            return image_bytes
        else:
            error_message = f"Stability API returned error {response.status_code}: {response.text}"
            print(f"[image_generator] Error: {error_message}")
            raise RuntimeError(error_message)

    except requests.RequestException as e:
        raise RuntimeError(f"Network error while connecting to image generation service: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing image_generator.py (Module 1)")
    print("=" * 60)

    test_prompt = "A cozy wooden treehouse in an autumn forest at sunset"
    test_output = "test_generated_image.png"

    print(f"Test Prompt: {test_prompt}")
    generated_bytes = generate_image(prompt=test_prompt, output_path=test_output)

    print(f"Generated image size: {len(generated_bytes)} bytes")
    print(f"Output file exists: {os.path.exists(test_output)}")
    print("Module 1 verification completed successfully.")
