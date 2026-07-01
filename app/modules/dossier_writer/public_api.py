"""Dossier writer module public API — cross-module access points.

Other modules should import from this file instead of directly accessing
internal service/repository/models.
"""

from app.modules.dossier_writer.repository import DossierRepository
from app.modules.dossier_writer.service import DossierService

__all__ = [
    "DossierService",
    "DossierRepository",
]
