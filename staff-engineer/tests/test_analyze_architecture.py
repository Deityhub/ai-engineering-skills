#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for analyze-architecture.py
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "analyze-architecture.py"


class TestAnalyzeArchitecture:
    """Tests for the architecture analyzer script."""

    def test_script_exists(self):
        assert SCRIPT.exists(), f"Script not found at {SCRIPT}"

    def test_script_runs_help(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_analyze_simple_python_project(self, temp_dir):
        """Test analyzing a simple Python project structure."""
        # Create a layered architecture
        (temp_dir / "domain" / "user" / "entity.py").mkdir(parents=True)
        (temp_dir / "domain" / "user" / "entity.py").write_text("""
class User:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
""")
        (temp_dir / "domain" / "user" / "repository.py").write_text("""
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> 'User':
        pass
""")
        (temp_dir / "application" / "user_service.py").write_text("""
from domain.user.repository import UserRepository
from domain.user.entity import User

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user(self, id: str) -> User:
        return self.repo.find_by_id(id)
""")
        (temp_dir / "adapters" / "db" / "postgres.py").write_text("""
from domain.user.repository import UserRepository
from domain.user.entity import User

class PostgresUserRepository(UserRepository):
    def find_by_id(self, id: str) -> User:
        # implementation
        return User(id, "test")
""")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "modules" in data
        assert "dependencies" in data
        assert "cycles" in data
        assert "layer_violations" in data
        assert "coupling_metrics" in data

        # Should detect 4 modules
        assert len(data["modules"]) >= 4

        # Should have NO cycles in this clean architecture
        assert data["cycles"] == []

        # Should have NO layer violations
        assert data["layer_violations"] == []

    def test_detects_circular_dependency(self, temp_dir):
        """Test detection of circular dependencies."""
        (temp_dir / "a.py").write_text("import b\n")
        (temp_dir / "b.py").write_text("import a\n")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Should detect at least one cycle
        assert len(data["cycles"]) > 0

    def test_detects_layer_violation(self, temp_dir):
        """Test detection of layer violations (domain -> adapters)."""
        (temp_dir / "domain" / "entity.py").mkdir(parents=True)
        (temp_dir / "domain" / "entity.py").write_text("""
import adapters.db.postgres  # VIOLATION: domain imports adapter

class User:
    pass
""")
        (temp_dir / "adapters" / "db" / "postgres.py").mkdir(parents=True)
        (temp_dir / "adapters" / "db" / "postgres.py").write_text("""
class PostgresRepo:
    pass
""")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Should detect layer violation
        assert len(data["layer_violations"]) > 0
        violation = data["layer_violations"][0]
        assert "domain" in violation.get("from_module", "")
        assert "adapter" in violation.get("to_module", "").lower()

    def test_mermaid_output(self, temp_dir):
        """Test Mermaid diagram generation."""
        (temp_dir / "domain" / "entity.py").mkdir(parents=True)
        (temp_dir / "domain" / "entity.py").write_text("class User: pass\n")
        (temp_dir / "application" / "service.py").mkdir(parents=True)
        (temp_dir / "application" / "service.py").write_text("from domain.entity import User\n")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--format", "mermaid"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0
        output = result.stdout
        assert "flowchart" in output or "graph" in output
        assert "Domain" in output
        assert "Application" in output
        assert "-->" in output  # dependency arrows

    def test_coupling_metrics(self, temp_dir):
        """Test coupling metrics calculation."""
        # Create modules with known coupling
        (temp_dir / "shared" / "utils.py").mkdir(parents=True)
        (temp_dir / "shared" / "utils.py").write_text("def helper(): pass\n")
        (temp_dir / "domain" / "a.py").mkdir(parents=True)
        (temp_dir / "domain" / "a.py").write_text("from shared.utils import helper\n")
        (temp_dir / "domain" / "b.py").mkdir(parents=True)
        (temp_dir / "domain" / "b.py").write_text("from shared.utils import helper\n")
        (temp_dir / "application" / "service.py").mkdir(parents=True)
        (temp_dir / "application" / "service.py").write_text("from domain.a import A\nfrom domain.b import B\n")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(temp_dir), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "coupling_metrics" in data
        metrics = data["coupling_metrics"]

        # shared should have high afferent coupling (Ca)
        shared_metrics = metrics.get("shared", {})
        assert shared_metrics.get("afferent", 0) >= 2  # depended on by domain.a and domain.b

        # domain should have efferent coupling to shared
        domain_metrics = metrics.get("domain", {})
        assert domain_metrics.get("efferent", 0) >= 1