"""Regression checks for optional benchmark metrics across local platforms."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))
import benchmark_metrics


class PortableBenchmarkMetricsTests(unittest.TestCase):
    def test_import_and_json_metric_when_resource_is_unavailable(self):
        spec = importlib.util.spec_from_file_location(
            "metrics_without_resource", benchmark_metrics.__file__)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"resource": None}):
            spec.loader.exec_module(module)
        self.assertEqual(module.peak_rss(), (None, None))

    def test_peak_rss_preserves_known_platform_units(self):
        fake = SimpleNamespace(
            RUSAGE_SELF=0, getrusage=lambda _: SimpleNamespace(ru_maxrss=123))
        for platform, units in (("linux", "KiB"), ("darwin", "bytes")):
            with self.subTest(platform=platform), \
                    patch.object(benchmark_metrics, "resource", fake), \
                    patch.object(benchmark_metrics.sys, "platform", platform):
                self.assertEqual(benchmark_metrics.peak_rss(), (123, units))

    def test_unknown_platform_does_not_guess_units(self):
        with patch.object(benchmark_metrics.sys, "platform", "unknown"):
            self.assertEqual(benchmark_metrics.peak_rss(), (None, None))
