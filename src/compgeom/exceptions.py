"""Centralized exception classes for CompGeom."""

from __future__ import annotations

class CompGeomError(Exception):
    """Base class for all CompGeom-related exceptions."""
    pass

class KernelError(CompGeomError):
    """Base class for exceptions in the kernel module."""
    pass

class MeshError(CompGeomError):
    """Base class for exceptions in the mesh module."""
    pass

class AlgorithmError(CompGeomError):
    """Base class for exceptions in the algo module."""
    pass
