"""
similarity_scorer.py
====================
Module 2: Image Similarity Scorer using CLIP.

This module loads an open-source CLIP model to turn images into vector embeddings
and computes a cosine similarity score (between 0.0 and 1.0).

Why this is separate:
In Step 1 & 2 of the AI Research Development Plan, the similarity scorer has
one specific responsibility: produce an accurate, objective similarity number.
It does NOT write qualitative feedback (that is handled by Module 3).
Keeping it isolated ensures that vision model changes, caching, and threshold
tuning can be performed independently of any text generation models.

Usage:
    from similarity_scorer import calculate_similarity, is_close_enough

    # Compare two image files
    score = calculate_similarity("reference.png", "learner_output.png")
    passed = is_close_enough(score, threshold=0.8)
    print(f"Similarity: {score:.2f}, Passed: {passed}")
"""

import os
import io
from typing import Union, Tuple, Optional
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEFAULT_CLIP_MODEL = os.getenv("CLIP_MODEL_NAME", "openai/clip-vit-base-patch32")

# 0.85 is a provisional starting threshold based on the initial Wave 1 test results and may be tuned later with more representative images
THRESHOLD = 0.85

# Global cache for loaded model and processor to avoid reloading per request
_CACHED_MODEL: Optional[CLIPModel] = None
_CACHED_PROCESSOR: Optional[CLIPProcessor] = None
_CACHED_MODEL_NAME: Optional[str] = None

# Embedding cache for reference images (keyed by file path or hash)
_EMBEDDING_CACHE: dict = {}


def load_clip_model(model_name: str = DEFAULT_CLIP_MODEL) -> Tuple[CLIPModel, CLIPProcessor]:
    """
    Loads and caches the CLIP model and processor from Hugging Face.

    Args:
        model_name: Hugging Face model identifier (default: 'openai/clip-vit-base-patch32').

    Returns:
        Tuple[CLIPModel, CLIPProcessor]: The loaded PyTorch model and processor.
    """
    global _CACHED_MODEL, _CACHED_PROCESSOR, _CACHED_MODEL_NAME

    if _CACHED_MODEL is not None and _CACHED_MODEL_NAME == model_name:
        return _CACHED_MODEL, _CACHED_PROCESSOR

    print(f"[similarity_scorer] Loading CLIP model '{model_name}'...")
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"[similarity_scorer] Using computation device: {device}")

    model = CLIPModel.from_pretrained(model_name).to(device)
    processor = CLIPProcessor.from_pretrained(model_name)
    model.eval()

    _CACHED_MODEL = model
    _CACHED_PROCESSOR = processor
    _CACHED_MODEL_NAME = model_name

    print("[similarity_scorer] CLIP model and processor loaded successfully.")
    return _CACHED_MODEL, _CACHED_PROCESSOR


def _to_pil_image(image_input: Union[str, bytes, Image.Image]) -> Image.Image:
    """
    Normalizes different image inputs (file path, bytes, PIL Image) to an RGB PIL Image.
    """
    if isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    elif isinstance(image_input, bytes):
        return Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise FileNotFoundError(f"Image file not found: {image_input}")
        return Image.open(image_input).convert("RGB")
    else:
        raise TypeError(f"Unsupported image type: {type(image_input)}. Expected path (str), bytes, or PIL Image.")


def get_image_embedding(
    image: Union[str, bytes, Image.Image],
    cache_key: Optional[str] = None,
    model: Optional[CLIPModel] = None,
    processor: Optional[CLIPProcessor] = None,
) -> torch.Tensor:
    """
    Computes a normalized embedding vector for a given image.

    If a cache_key is provided and the embedding is already cached,
    the cached embedding is returned directly to save computation time.

    Args:
        image: File path, bytes, or PIL Image.
        cache_key: Optional string identifier to cache the resulting embedding.
        model: Optional pre-loaded CLIPModel.
        processor: Optional pre-loaded CLIPProcessor.

    Returns:
        torch.Tensor: 1D normalized embedding tensor.
    """
    global _EMBEDDING_CACHE

    if cache_key and cache_key in _EMBEDDING_CACHE:
        return _EMBEDDING_CACHE[cache_key]

    if model is None or processor is None:
        model, processor = load_clip_model()

    pil_img = _to_pil_image(image)
    device = next(model.parameters()).device

    inputs = processor(images=pil_img, return_tensors="pt").to(device)

    with torch.no_grad():
        # Compute image features from CLIP vision encoder
        image_features = model.get_image_features(**inputs)
        # Handle both Tensor outputs and BaseModelOutputWithPooling (transformers 5.x)
        if hasattr(image_features, "pooler_output") and image_features.pooler_output is not None:
            features_tensor = image_features.pooler_output
        elif isinstance(image_features, (tuple, list)):
            features_tensor = image_features[0]
        elif isinstance(image_features, torch.Tensor):
            features_tensor = image_features
        else:
            features_tensor = getattr(image_features, "last_hidden_state", image_features)

        # Normalize the embedding vector to unit length for cosine similarity
        normalized_features = features_tensor / features_tensor.norm(p=2, dim=-1, keepdim=True)

    embedding = normalized_features.squeeze(0)

    if cache_key:
        _EMBEDDING_CACHE[cache_key] = embedding

    return embedding


def calculate_similarity(
    image_a: Union[str, bytes, Image.Image],
    image_b: Union[str, bytes, Image.Image],
    cache_key_a: Optional[str] = None,
    cache_key_b: Optional[str] = None,
    model: Optional[CLIPModel] = None,
    processor: Optional[CLIPProcessor] = None,
) -> float:
    """
    Calculates the cosine similarity score between two images using CLIP.

    Args:
        image_a: First image (e.g., reference image).
        image_b: Second image (e.g., learner-generated image).
        cache_key_a: Optional cache identifier for image_a.
        cache_key_b: Optional cache identifier for image_b.
        model: Optional CLIPModel instance.
        processor: Optional CLIPProcessor instance.

    Returns:
        float: Cosine similarity score bounded between 0.0 and 1.0.
    """
    if model is None or processor is None:
        model, processor = load_clip_model()

    emb_a = get_image_embedding(image_a, cache_key=cache_key_a, model=model, processor=processor)
    emb_b = get_image_embedding(image_b, cache_key=cache_key_b, model=model, processor=processor)

    # Cosine similarity between two unit-normalized vectors is simply their dot product
    cos_sim = torch.dot(emb_a, emb_b).item()

    # Clamp the value between 0.0 and 1.0 for stability and readability
    bounded_score = max(0.0, min(1.0, float(cos_sim)))
    return round(bounded_score, 4)


def score_similarity(
    image_path_a: Union[str, bytes, Image.Image],
    image_path_b: Union[str, bytes, Image.Image],
) -> float:
    """
    Computes the visual similarity score between two images using CLIP.

    This is the simple public function required by Track B1 Wave 1.
    """
    return calculate_similarity(image_path_a, image_path_b)


def is_close_enough(similarity_score: float, threshold: float = THRESHOLD) -> bool:
    """
    Determines whether a similarity score satisfies the passing threshold.

    As outlined in Step 2 of the AI Research Development Plan, the starting threshold is 0.75 and may be tuned later.

    Args:
        similarity_score: Score between 0.0 and 1.0.
        threshold: The cutoff score for a match (default: THRESHOLD).

    Returns:
        bool: True if similarity_score >= threshold, False otherwise.
    """
    return similarity_score >= threshold

