#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for scan-security.py
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "scan-security.py"


class TestScanSecurity:
    """Tests for the security scanner script."""

    def test_script_exists(self):
        assert SCRIPT.exists(), f"Script not found at {SCRIPT}"

    def test_script_runs_help(self):
        """Test script runs and shows help."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "options" in result.stdout.lower()

    def test_scan_secrets_detection(self, temp_dir):
        """Test secret detection finds common patterns."""
        # Create test files with secrets
        (temp_dir / "config.py").write_text("""
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
GITHUB_TOKEN = "ghp_1234567890abcdef1234567890abcdef12345678"
JWT_SECRET = "super-secret-jwt-key-change-in-production"
DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
""")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--checks", "secrets", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode in (0, 1)  # 0 = no findings, 1 = findings found
        if result.stdout:
            data = json.loads(result.stdout)
            assert "findings" in data
            # Should detect at least AWS keys and GitHub token
            finding_types = [f.get("type", "") for f in data["findings"]]
            assert any("aws" in t.lower() for t in finding_types)
            assert any("github" in t.lower() for t in finding_types)

    def test_scan_sast_sql_injection(self, temp_dir):
        """Test SAST detects SQL injection patterns."""
        (temp_dir / "vuln.py").write_text("""
def get_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    return cursor.fetchone()
""")
        (temp_dir / "safe.py").write_text("""
def get_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()
""")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--checks", "sast", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.stdout:
            data = json.loads(result.stdout)
            assert "findings" in data
            # Should flag the vulnerable file
            vuln_findings = [f for f in data["findings"] if "vuln.py" in f.get("file", "")]
            assert len(vuln_findings) > 0
            # Should NOT flag the safe file (or at least not for SQLi)
            safe_findings = [f for f in data["findings"] if "safe.py" in f.get("file", "") and "sql" in f.get("type", "").lower()]
            assert len(safe_findings) == 0

    def test_scan_dependencies(self, temp_dir):
        """Test dependency vulnerability scanning."""
        # Create a package.json with known vulnerable version
        (temp_dir / "package.json").write_text("""
{
  "name": "test",
  "version": "1.0.0",
  "dependencies": {
    "lodash": "4.17.15"
  }
}
""")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--checks", "deps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=120,  # npm audit can be slow
        )

        # Should run without crashing
        assert result.returncode in (0, 1, 2)
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                assert "findings" in data
            except json.JSONDecodeError:
                # Non-JSON output is OK for this test
                pass

    def test_sarif_output(self, temp_dir):
        """Test SARIF output format."""
        (temp_dir / "test.py").write_text("password = 'secret123'")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--checks", "secrets", "--format", "sarif"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.stdout:
            data = json.loads(result.stdout)
            assert "runs" in data
            assert "results" in data["runs"][0]


class TestScanSecurityIntegration:
    """Integration tests using sample projects."""

    def test_go_project_scan(self, sample_go_project):
        """Test scanning a Go project."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(sample_go_project), "--checks", "sast,secrets", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode in (0, 1)
        if result.stdout:
            data = json.loads(result.stdout)
            assert "findings" in data
            # Should detect SQL injection in handler.go
            sql_findings = [f for f in data["findings"] if "sql" in f.get("type", "").lower()]
            assert len(sql_findings) > 0

    def test_python_project_scan(self, sample_python_project):
        """Test scanning a Python project."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(sample_python_project), "--checks", "sast,secrets", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode in (0, 1)
        if result.stdout:
            data = json.loads(result.stdout)
            assert "findings" in data
            # Should detect SQL injection in main.py
            sql_findings = [f for f in data["findings"] if "sql" in f.get("type", "").lower()]
            assert len(sql_findings) > 0

    def test_ts_project_scan(self, sample_ts_project):
        """Test scanning a TypeScript project."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(sample_ts_project), "--checks", "sast,secrets", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode in (0, 1)
        if result.stdout:
            data = json.loads(result.stdout)
            assert "findings" in data
            # Should detect SQL injection in user.ts
            sql_findings = [f for f in data["findings"] if "sql" in f.get("type", "").lower()]
            assert len(sql_findings) > 0