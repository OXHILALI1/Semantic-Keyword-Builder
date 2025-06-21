#!/usr/bin/env python3
"""
Test runner for n8n workflow repository testing.
Provides a simple interface to run different test suites.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return success status."""
    print(f"🔧 {description}")
    print(f"   Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return False
            
    except FileNotFoundError:
        print(f"   ❌ Command not found: {cmd[0]}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking test dependencies...")
    
    # Check Python
    python_cmd = [sys.executable, "--version"]
    if not run_command(python_cmd, "Checking Python version"):
        return False
    
    # Try to import required modules
    try:
        import json
        import tempfile
        import pathlib
        print("   ✅ Core Python modules available")
    except ImportError as e:
        print(f"   ❌ Missing Python module: {e}")
        return False
    
    # Check if our modules can be imported
    try:
        from new_workflow_analyzer import NewWorkflowAnalyzer
        from auto_add_workflow import AutoWorkflowAdder
        print("   ✅ Workflow modules available")
    except ImportError as e:
        print(f"   ❌ Cannot import workflow modules: {e}")
        return False
    
    return True


def run_unit_tests():
    """Run unit tests."""
    if not os.path.exists("tests/unit"):
        print("❌ Unit tests directory not found")
        return False
    
    # Try pytest first, fall back to unittest
    pytest_cmd = [sys.executable, "-m", "pytest", "tests/unit", "-v", "--tb=short"]
    if run_command(pytest_cmd, "Running unit tests with pytest"):
        return True
    
    # Fallback to unittest discovery
    unittest_cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests/unit", "-v"]
    return run_command(unittest_cmd, "Running unit tests with unittest")


def run_integration_tests():
    """Run integration tests."""
    if not os.path.exists("tests/integration"):
        print("❌ Integration tests directory not found")
        return False
    
    pytest_cmd = [sys.executable, "-m", "pytest", "tests/integration", "-v", "--tb=short"]
    if run_command(pytest_cmd, "Running integration tests with pytest"):
        return True
    
    unittest_cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests/integration", "-v"]
    return run_command(unittest_cmd, "Running integration tests with unittest")


def run_e2e_tests():
    """Run end-to-end tests."""
    if not os.path.exists("tests/e2e"):
        print("❌ E2E tests directory not found")
        return False
    
    pytest_cmd = [sys.executable, "-m", "pytest", "tests/e2e", "-v", "--tb=short"]
    if run_command(pytest_cmd, "Running E2E tests with pytest"):
        return True
    
    unittest_cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests/e2e", "-v"]
    return run_command(unittest_cmd, "Running E2E tests with unittest")


def run_all_tests():
    """Run all test suites."""
    print("🚀 Running complete test suite...\n")
    
    results = {
        "unit": run_unit_tests(),
        "integration": run_integration_tests(),
        "e2e": run_e2e_tests()
    }
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    total_passed = 0
    total_suites = len(results)
    
    for suite_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {suite_name.upper():12} {status}")
        if passed:
            total_passed += 1
    
    print(f"\n🎯 Overall: {total_passed}/{total_suites} test suites passed")
    
    if total_passed == total_suites:
        print("🎉 All tests passed! Your workflow system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


def run_quick_validation():
    """Run a quick validation of core functionality."""
    print("⚡ Running quick validation tests...\n")
    
    try:
        # Test 1: Import modules
        print("🔧 Testing module imports...")
        from new_workflow_analyzer import NewWorkflowAnalyzer
        from auto_add_workflow import AutoWorkflowAdder
        print("   ✅ Modules imported successfully")
        
        # Test 2: Create instances
        print("🔧 Testing instance creation...")
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = NewWorkflowAnalyzer(temp_dir)
            adder = AutoWorkflowAdder(temp_dir)
            print("   ✅ Instances created successfully")
            
            # Test 3: Basic functionality
            print("🔧 Testing basic functionality...")
            
            # Create a minimal test workflow
            test_workflow = {
                "id": "quick-test",
                "name": "Quick Test Workflow",
                "nodes": [
                    {
                        "id": "test-node",
                        "type": "n8n-nodes-base.manualTrigger",
                        "name": "Test Node"
                    }
                ],
                "connections": {},
                "active": True
            }
            
            # Test analysis
            import json
            import tempfile as tf
            with tf.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(test_workflow, f)
                temp_file = f.name
            
            try:
                result = analyzer.analyze_workflow_file(temp_file)
                if result and result.get("success"):
                    print("   ✅ Workflow analysis working")
                else:
                    print("   ❌ Workflow analysis failed")
                    return False
            finally:
                os.unlink(temp_file)
        
        print("\n🎉 Quick validation passed! Core functionality is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Quick validation failed: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='N8N Workflow Repository Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only') 
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests only')
    parser.add_argument('--quick', action='store_true', help='Run quick validation only')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("🧪 N8N Workflow Repository Test Runner")
    print("="*50)
    
    # Check dependencies first
    if args.check_deps:
        success = check_dependencies()
        return 0 if success else 1
    
    if not check_dependencies():
        print("\n❌ Dependency check failed. Cannot run tests.")
        return 1
    
    print()  # Empty line for readability
    
    # Run specific test suite
    if args.quick:
        success = run_quick_validation()
    elif args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.e2e:
        success = run_e2e_tests()
    else:
        # Run all tests by default
        success = run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    import tempfile
    exit(main())