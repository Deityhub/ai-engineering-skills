#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for staff-engineer skill tests.
"""

import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_go_project(temp_dir):
    """Create a sample Go project structure."""
    (temp_dir / "go.mod").write_text("module example.com/test\n\ngo 1.21\n")
    (temp_dir / "main.go").write_text("package main\n\nfunc main() {}\n")
    (temp_dir / "handler.go").write_text("""
package main

import (
    "database/sql"
    "fmt"
    "net/http"
)

func GetUser(db *sql.DB, id string) (*User, error) {
    query := "SELECT * FROM users WHERE id = '" + id + "'"
    row := db.QueryRow(query)
    return nil, row.Err()
}

type User struct {
    ID   string
    Name string
}
""")
    (temp_dir / "handler_test.go").write_text("""
package main

import "testing"

func TestGetUser(t *testing.T) {
    // test
}
""")
    return temp_dir


@pytest.fixture
def sample_python_project(temp_dir):
    """Create a sample Python project structure."""
    (temp_dir / "pyproject.toml").write_text("""
[project]
name = "test"
version = "0.1.0"
dependencies = ["requests"]
""")
    (temp_dir / "main.py").write_text("""
import sqlite3

def get_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    return cursor.fetchone()
""")
    (temp_dir / "test_main.py").write_text("""
import pytest

def test_get_user():
    pass
""")
    return temp_dir


@pytest.fixture
def sample_ts_project(temp_dir):
    """Create a sample TypeScript project structure."""
    (temp_dir / "package.json").write_text("""
{
  "name": "test",
  "version": "1.0.0",
  "dependencies": {},
  "devDependencies": {"typescript": "^5.0.0"}
}
""")
    (temp_dir / "tsconfig.json").write_text("""
{
  "compilerOptions": {"strict": true, "target": "ES2020"},
  "include": ["src"]
}
""")
    (temp_dir / "src" / "user.ts").mkdir(parents=True)
    (temp_dir / "src" / "user.ts").write_text("""
import { Pool } from 'pg';

async function getUser(db: Pool, id: string) {
  const result = await db.query(`SELECT * FROM users WHERE id = '${id}'`);
  return result.rows[0];
}
""")
    return temp_dir