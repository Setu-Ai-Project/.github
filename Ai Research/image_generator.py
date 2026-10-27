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
from typing import Optional, Union
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Safety & Content Moderation integration (Track B2 Wave 1)
from moderation import moderate_prompt, moderate_image_response

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
) -> Union[bytes, str]:
    """
    Generates an image from a text prompt using the Stability AI Core API,
    with Wave 1 moderation gates before generation and after response receipt.

    Args:
        prompt: The text description of the image to generate.
        output_path: Optional file path where the generated image should be saved.
        api_key: Optional Stability AI API key (defaults to STABILITY_API_KEY env var).
        aspect_ratio: Aspect ratio of the generated image (e.g., "1:1", "16:9").
        output_format: Image format ("png" or "jpeg").

    Returns:
        Union[bytes, str]:
            - Raw image file bytes if generation succeeds and passes moderation.
            - Moderation message string if blocked at pre-flight or post-response.

    Raises:
        ValueError: If the prompt is empty.
        RuntimeError: If an unhandled network or server error occurs.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    # 1. Before any generation occurs: Pre-Flight Input Moderation
    is_allowed, reason = moderate_prompt(prompt)
    if not is_allowed:
        print(f"[image_generator] Moderation Gate: Prompt blocked - {reason}")
        return reason

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

        # 2. After Stability AI response is received: Output Moderation Check
        is_safe, mod_reason = moderate_image_response(response)
        if not is_safe:
            print(f"[image_generator] Moderation Gate: Image response blocked - {mod_reason}")
            return mod_reason

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
    print("Testing image_generator.py (Module 1 with moderation.py)")
    print("=" * 60)

    # 1. Test safe benign prompt
    test_prompt = "A cozy wooden treehouse in an autumn forest at sunset"
    test_output = "test_generated_image.png"

    print(f"\n1. Testing safe prompt: '{test_prompt}'")
    result = generate_image(prompt=test_prompt, output_path=test_output)
    if isinstance(result, bytes):
        print(f"SUCCESS: Generated image size: {len(result)} bytes")
        print(f"Output file exists: {os.path.exists(test_output)}")
    else:
        print(f"FAILED: Expected image bytes, got moderation message: {result}")

    # 2. Test unsafe prompt blocked before generation
    unsafe_prompt = "A warrior with a blood covered sword after a murder"
    print(f"\n2. Testing unsafe prompt: '{unsafe_prompt}'")
    blocked_result = generate_image(prompt=unsafe_prompt)
    print(f"Returned Result: {blocked_result}")
    assert isinstance(blocked_result, str), "Expected moderation message string"
    assert "friendly, safe, and creative" in blocked_result

    print("\nModule 1 verification completed successfully.")
