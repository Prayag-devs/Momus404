"""
momus404 — backend/laya_judge.py (Backward Compatibility Facade)
Re-exports from app.services.judge_service.
"""

from app.services.judge_service import (
    LayaEdgeJudge,
    get_judge,
    CUDA_AVAILABLE,
    TORCH_AVAILABLE,
    DEVICE_NAME,
)

# Compatibility aliases
_CUDA_AVAILABLE = CUDA_AVAILABLE
_TORCH_AVAILABLE = TORCH_AVAILABLE
_DEVICE_NAME = DEVICE_NAME

judge = get_judge()

__all__ = [
    "LayaEdgeJudge",
    "judge",
    "CUDA_AVAILABLE",
    "TORCH_AVAILABLE",
    "DEVICE_NAME",
    "_CUDA_AVAILABLE",
    "_TORCH_AVAILABLE",
    "_DEVICE_NAME",
]
