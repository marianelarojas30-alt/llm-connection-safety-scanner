import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import run_scan


class EmptyScanTests(unittest.TestCase):
    def test_missing_and_empty_suites_preserve_previous_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            empty_directory = root / "empty-directory"
            empty_array = root / "empty-array"
            empty_directory.mkdir()
            empty_array.mkdir()
            (empty_array / "test_connection_tests.json").write_text("[]", encoding="utf-8")
            results = root / "results"
            reports = root / "reports"
            results.mkdir()
            reports.mkdir()
            outputs = [results / "connection_scan_results.json",
                       results / "connection_scan_results.csv", reports / "latest_report.md"]
            for output in outputs:
                output.write_bytes(b"previous run")

            for scenarios in (root / "missing", empty_directory, empty_array):
                with self.subTest(directory=scenarios.name):
                    stderr = io.StringIO()
                    with patch.multiple(run_scan, SCENARIOS_DIR=scenarios,
                                        RESULTS_DIR=results, REPORTS_DIR=reports), \
                            patch.object(sys, "argv", ["run_scan.py"]), redirect_stderr(stderr):
                        with self.assertRaises(SystemExit) as stopped:
                            run_scan.main()
                    self.assertEqual(stopped.exception.code, 1)
                    self.assertIn(str(scenarios), stderr.getvalue())
                    for output in outputs:
                        self.assertEqual(output.read_bytes(), b"previous run")
