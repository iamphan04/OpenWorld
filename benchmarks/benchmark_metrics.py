"""Portable, optional process metrics for local research benchmarks."""
from __future__ import annotations

import sys

try:
    import resource
except ImportError:  # The standard-library module is unavailable on Windows.
    resource = None


def peak_rss() -> tuple[int | float | None, str | None]:
    """Return process-lifetime peak RSS and known units, or unavailable values.

    This metric includes earlier work in the same process. It is not the
    incremental memory cost of a case. Do not guess units on other platforms.
    """
    if resource is None or sys.platform not in ("linux", "darwin"):
        return None, None
    units = "KiB" if sys.platform == "linux" else "bytes"
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, units
