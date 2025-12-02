"""FastAPI dependency injection utilities."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from loguru import logger

from src.config import Settings, get_settings
from src.ml.segmenter import Segmenter

# Type alias for settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


@lru_cache(maxsize=1)
def _load_segmenter() -> Segmenter:
    """Load segmenter model once and cache it."""
    logger.info("Loading segmenter model...")
    return Segmenter.load()


def get_segmenter() -> Segmenter:
    """Get the loaded segmenter model.

    Returns:
        Loaded and fitted Segmenter instance.

    Raises:
        HTTPException: If model file not found (503 Service Unavailable).
    """
    try:
        return _load_segmenter()
    except FileNotFoundError as e:
        logger.error(f"Segmenter model not found: {e}")
        raise HTTPException(
            status_code=503,
            detail="Segmentation model not available. Please train the model first.",
        ) from e


# Type alias for segmenter dependency
SegmenterDep = Annotated[Segmenter, Depends(get_segmenter)]

