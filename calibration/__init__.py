# calibration/__init__.py
# earth-systems-physics
# CC0 — No Rights Reserved
"""
Calibration-audit submodules. A small, stdlib-only scoring framework
for running multi-dimensional audits that produce a banded verdict
(GREEN/YELLOW/RED/EXTINCT) with falsifiable claims and a JSON report.

Modules:
    schema                  — Band enum, DimensionScore, CalibrationReport
    architecture_mismatch   — detector for language-primary vs
                              substrate-primary cognitive architecture
                              mismatch
"""

from .schema import Band, DimensionScore, CalibrationReport

__all__ = ["Band", "DimensionScore", "CalibrationReport"]
