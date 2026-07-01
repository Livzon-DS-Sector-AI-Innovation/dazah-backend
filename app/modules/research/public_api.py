"""Research module public API — cross-module access points.

Other modules should import from this file instead of directly accessing
internal service/repository/models.
"""

from app.modules.research import service
from app.modules.research import repository

__all__ = [
    "service",
    "repository",
]
