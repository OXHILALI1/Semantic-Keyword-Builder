# Testing Guide

## Overview

This repository includes a comprehensive automated testing system designed to ensure code quality, prevent regressions, and validate functionality across multiple platforms and Python versions.

## Test Architecture

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - Mock external dependencies
   - Fast execution (< 1 second per test)
   - Files: `test_workflow_analyzer.py`, `test_auto_add_workflow.py`

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Real file operations
   - API endpoint logic validation
   - Files: `test_file_operations.py`, `test_api_endpoints.py`

3. **End-to-End Tests** (`tests/e2e/`)
   - Test complete user scenarios
   - Full workflow from analysis to addition
   - Performance and data integrity validation
   - Files: `test_complete_workflow.py`

### Framework Design

- **Primary Framework**: pytest (with unittest fallback)
- **Configuration**: `pytest.ini` with custom markers
- **Fixtures**: Comprehensive test data in `tests/conftest.py`
- **Test Runner**: `run_tests.py` with multiple execution modes

## Running Tests

### Quick Commands

```bash
# Quick validation (recommended for development)
python run_tests.py --quick

# Complete test suite
python run_tests.py

# Specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --e2e

# Dependency check
python run_tests.py --check-deps
```

### Advanced Usage

```bash
# Verbose output
python run_tests.py --verbose

# Using pytest directly (if available)
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_workflow_analyzer.py -v

# Run with coverage (if pytest-cov installed)
pytest tests/ --cov=. --cov-report=html
```

## Test Fixtures

### Workflow Fixtures (`tests/conftest.py`)

- `simple_workflow`: Basic 2-node workflow for quick testing
- `complex_workflow`: Multi-service workflow with GitHub/Discord integration
- `scheduled_workflow`: Cron-triggered workflow for timing tests
- `invalid_workflow`: Malformed workflow for error testing

### Environment Fixtures

- `temp_workflows_dir`: Clean temporary directory for each test
- `temp_workflow_file`: Temporary workflow file with cleanup
- `mock_existing_workflows`: Pre-populated test environment

## Continuous Integration

### GitHub Actions Workflows

1. **`test.yml`** - Main testing pipeline
   - Runs on every push and pull request
   - Tests across Python 3.8, 3.9, 3.10, 3.11
   - Multi-platform: Ubuntu, Windows, macOS
   - Comprehensive test suite execution

2. **`pr-validation.yml`** - Pull request validation
   - Workflow file validation
   - Backward compatibility checks
   - Performance regression detection
   - Security scanning

3. **`nightly.yml`** - Nightly health checks
   - Comprehensive system health monitoring
   - Performance benchmarking
   - Memory usage validation
   - Repository integrity checks

4. **`release.yml`** - Release validation
   - Pre-release testing across all platforms
   - Documentation validation
   - Security audit
   - Multi-platform compatibility verification

### Test Quality Gates

All tests must pass before code can be merged:

- ✅ Unit tests: 100% pass rate required
- ✅ Integration tests: All file operations validated
- ✅ End-to-end tests: Complete scenarios working
- ✅ Multi-platform: Linux, Windows, macOS support
- ✅ Multi-version: Python 3.8+ compatibility

## Test Coverage

### Core Components

- **NewWorkflowAnalyzer**: 95%+ test coverage
  - Service detection algorithms
  - Filename generation logic
  - Error handling scenarios
  - Edge cases (malformed files, missing data)

- **AutoWorkflowAdder**: 95%+ test coverage
  - File operations (copy, move, backup)
  - Conflict resolution
  - Batch processing
  - Dry-run functionality

### Integration Points

- **File Operations**: Complete test coverage
  - Large file handling
  - Permission management
  - Encoding support (UTF-8, Unicode)
  - Concurrent operations

- **API Logic**: Comprehensive validation
  - Request/response cycles
  - Error handling
  - File upload validation
  - Performance characteristics

## Performance Testing

### Benchmarks

- **Analysis Speed**: < 100ms per workflow (target)
- **Addition Speed**: < 500ms per workflow (target)
- **Memory Usage**: < 100MB increase for large workflows
- **Concurrent Operations**: Support for multiple simultaneous operations

### Load Testing

- **Batch Processing**: 50+ workflows in single operation
- **Large Files**: 500+ node workflows (> 50KB JSON)
- **Repository Scale**: 2000+ existing workflows

## Debugging Tests

### Common Issues

1. **Import Errors**
   ```bash
   # Check dependencies
   python run_tests.py --check-deps
   ```

2. **File Permission Errors**
   ```bash
   # Ensure proper permissions
   chmod 755 run_tests.py
   ```

3. **Temporary Directory Issues**
   ```bash
   # Clear temporary files
   find /tmp -name "*test*" -type d -exec rm -rf {} +
   ```

### Verbose Debugging

```bash
# Maximum verbosity with pytest
pytest tests/ -v -s --tb=long

# Python unittest with verbose output
python -m unittest discover tests/ -v
```

## Test Data Management

### Test Workflow Creation

```python
# Simple test workflow template
test_workflow = {
    "id": "test-workflow",
    "name": "Test Workflow",
    "nodes": [
        {
            "id": "trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "name": "Manual Trigger"
        }
    ],
    "connections": {},
    "active": True
}
```

### Cleanup

All tests automatically clean up:
- Temporary files and directories
- Mock objects and patches
- Test database entries
- Modified environment variables

## Best Practices

### Writing Tests

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up resources
3. **Assertions**: Use descriptive assertion messages
4. **Naming**: Use clear, descriptive test names
5. **Documentation**: Add docstrings for complex tests

### Test Organization

1. **One test per function/method**: Keep tests focused
2. **Group related tests**: Use test classes for organization
3. **Use fixtures**: Reuse common test data
4. **Mock external dependencies**: Keep tests fast and reliable

### Performance Guidelines

1. **Fast unit tests**: < 1 second each
2. **Reasonable integration tests**: < 5 seconds each
3. **Efficient end-to-end tests**: < 30 seconds each
4. **Minimal resource usage**: Clean up after each test

## Troubleshooting

### Common Solutions

1. **Tests hanging**: Check for unclosed file handles
2. **Random failures**: Look for race conditions in concurrent tests
3. **Import errors**: Verify PYTHONPATH and module structure
4. **Permission denied**: Check file/directory permissions

### Getting Help

1. Run with maximum verbosity: `python run_tests.py --verbose`
2. Check test logs in CI/CD pipeline
3. Review test coverage reports
4. Consult the test documentation in individual test files

---

*This testing system ensures the reliability and quality of the n8n workflow repository management tools across all supported platforms and Python versions.*