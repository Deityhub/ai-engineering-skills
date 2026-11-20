#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terraform Validator — Runs fmt, validate, plan with optional OPA policy checking.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional


class TerraformValidator:
    def __init__(self, terraform_path: str = "terraform"):
        self.terraform_path = terraform_path

    def _run(self, args: List[str], cwd: Path, env: Dict = None) -> subprocess.CompletedProcess:
        """Run terraform command."""
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        return subprocess.run(
            [self.terraform_path] + args,
            cwd=cwd,
            env=full_env,
            capture_output=True,
            text=True,
            timeout=300,
        )

    def fmt_check(self, path: Path) -> Dict[str, Any]:
        """Run terraform fmt -check."""
        result = self._run(["fmt", "-check", "-diff"], path)
        return {
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def init(self, path: Path, backend_config: Dict = None) -> Dict[str, Any]:
        """Run terraform init."""
        args = ["init"]
        if backend_config:
            for k, v in backend_config.items():
                args.extend(["-backend-config", f"{k}={v}"])
        result = self._run(args, path)
        return {
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def validate(self, path: Path) -> Dict[str, Any]:
        """Run terraform validate."""
        result = self._run(["validate", "-json"], path)
        try:
            output = json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            output = {"valid": result.returncode == 0, "raw": result.stdout}
        return {
            "passed": result.returncode == 0,
            "output": output,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def plan(self, path: Path, var_files: List[Path] = None, vars: Dict = None, out: Path = None) -> Dict[str, Any]:
        """Run terraform plan."""
        args = ["plan", "-input=false", "-refresh=true"]
        if var_files:
            for vf in var_files:
                args.extend(["-var-file", str(vf)])
        if vars:
            for k, v in vars.items():
                args.extend(["-var", f"{k}={v}"])
        if out:
            args.extend(["-out", str(out)])
        else:
            args.append("-detailed-exitcode")
        
        result = self._run(args, path)
        # Exit codes: 0 = no changes, 1 = error, 2 = changes present
        has_changes = result.returncode == 2
        error = result.returncode == 1
        
        return {
            "passed": not error,
            "has_changes": has_changes,
            "error": error,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def show_plan_json(self, plan_file: Path) -> Dict[str, Any]:
        """Run terraform show -json on plan file."""
        result = self._run(["show", "-json", str(plan_file)], plan_file.parent)
        try:
            output = json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            output = {"error": "Failed to parse plan JSON", "raw": result.stdout[:5000]}
        return {
            "passed": result.returncode == 0,
            "plan": output,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }


class PolicyChecker:
    def __init__(self, opa_path: str = "opa"):
        self.opa_path = opa_path

    def check(self, plan_json: Dict, policy_dir: Path) -> Dict[str, Any]:
        """Run OPA eval on plan JSON against policies."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(plan_json, f)
            plan_file = f.name
        
        try:
            result = subprocess.run(
                [self.opa_path, "eval", "-i", plan_file, "-d", str(policy_dir), "data.terraform.deny"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            violations = []
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout)
                    if output and "result" in output:
                        for r in output["result"]:
                            if "expressions" in r:
                                for expr in r["expressions"]:
                                    if "value" in expr and expr["value"]:
                                        violations.extend(expr["value"])
                except json.JSONDecodeError:
                    pass
            
            return {
                "passed": len(violations) == 0,
                "violations": violations,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        finally:
            os.unlink(plan_file)


def main():
    parser = argparse.ArgumentParser(description="Validate Terraform configuration")
    parser.add_argument("--path", required=True, help="Path to Terraform directory")
    parser.add_argument("--policy", help="Path to OPA policy directory")
    parser.add_argument("--var-file", action="append", type=Path, help="Variable file(s)")
    parser.add_argument("--var", action="append", help="Variables (key=value)")
    parser.add_argument("--plan-out", type=Path, help="Save plan to file")
    parser.add_argument("--fail-on", choices=["fmt", "validate", "plan", "policy", "any"], default="any", help="Fail on specific check")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    validator = TerraformValidator()
    vars_dict = {}
    if args.var:
        for v in args.var:
            if "=" in v:
                k, val = v.split("=", 1)
                vars_dict[k] = val

    results = {}
    overall_passed = True

    # 1. fmt check
    print("🔍 Checking formatting...")
    fmt_result = validator.fmt_check(path)
    results["fmt"] = fmt_result
    if not fmt_result["passed"]:
        overall_passed = False
        print("  ❌ Format check failed")
        if fmt_result["stdout"]:
            print(fmt_result["stdout"])
    else:
        print("  ✅ Format OK")

    # 2. init
    print("🔧 Initializing...")
    init_result = validator.init(path)
    results["init"] = init_result
    if not init_result["passed"]:
        overall_passed = False
        print("  ❌ Init failed")
        print(init_result["stderr"])
    else:
        print("  ✅ Init OK")

    # 3. validate
    print("✅ Validating...")
    validate_result = validator.validate(path)
    results["validate"] = validate_result
    if not validate_result["passed"]:
        overall_passed = False
        print("  ❌ Validation failed")
        if validate_result["output"]:
            print(json.dumps(validate_result["output"], indent=2))
    else:
        print("  ✅ Validation OK")

    # 4. plan
    print("📋 Planning...")
    plan_result = validator.plan(path, args.var_file, vars_dict, args.plan_out)
    results["plan"] = plan_result
    if plan_result["error"]:
        overall_passed = False
        print("  ❌ Plan failed")
        print(plan_result["stderr"])
    elif plan_result["has_changes"]:
        print("  ⚠️  Plan has changes")
    else:
        print("  ✅ No changes")

    # 5. policy check
    policy_result = None
    if args.policy and plan_result["passed"] and not plan_result["error"]:
        print("🛡️  Checking policies...")
        policy_checker = PolicyChecker()
        show_result = validator.show_plan_json(args.plan_out) if args.plan_out else {"passed": False, "error": "No plan file"}
        if show_result["passed"]:
            policy_result = policy_checker.check(show_result["plan"], Path(args.policy))
            results["policy"] = policy_result
            if not policy_result["passed"]:
                overall_passed = False
                print(f"  ❌ Policy violations: {len(policy_result['violations'])}")
                for v in policy_result["violations"]:
                    print(f"    - {v}")
            else:
                print("  ✅ Policy check passed")
        else:
            print("  ⚠️  Could not read plan for policy check")

    # Output
    if args.format == "json":
        output = {
            "overall_passed": overall_passed,
            "results": results,
        }
        if policy_result:
            output["results"]["policy"] = policy_result
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'✅ PASSED' if overall_passed else '❌ FAILED'}")

    # Exit code
    if args.fail_on == "any" and not overall_passed:
        sys.exit(1)
    elif args.fail_on != "any":
        check_result = results.get(args.fail_on)
        if check_result and not check_result["passed"]:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()