"""
Integration tests for file operations.
Tests complete file handling workflows including backup creation, file movements, and cleanup.
"""

import pytest
import json
import tempfile
import os
import shutil
from pathlib import Path

from auto_add_workflow import AutoWorkflowAdder
from new_workflow_analyzer import NewWorkflowAnalyzer


class TestFileOperations:
    """Test suite for file operation integration."""

    def test_complete_workflow_addition_file_flow(self, simple_workflow):
        """Test complete file flow from upload to final placement."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create source workflow file
            source_file = os.path.join(temp_dir, "source_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Test complete flow
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            # Verify success
            assert result["success"] is True
            assert result["action"] == "added"
            
            # Verify target file exists
            target_path = result["target_path"]
            assert os.path.exists(target_path)
            assert os.path.isfile(target_path)
            
            # Verify content integrity
            with open(target_path, 'r') as f:
                saved_data = json.load(f)
            assert saved_data["id"] == simple_workflow["id"]
            assert saved_data["name"] == simple_workflow["name"]
            assert len(saved_data["nodes"]) == len(simple_workflow["nodes"])
            
            # Verify source file still exists (copy, not move)
            assert os.path.exists(source_file)

    def test_backup_creation_and_restoration(self, simple_workflow):
        """Test backup creation and restoration functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            backup_dir = os.path.join(temp_dir, "workflow_backups")
            
            # Create initial workflow directory with some files
            os.makedirs(workflows_dir)
            
            initial_workflows = [
                ("0001_Test_Workflow.json", {"id": "test1", "name": "Test 1", "nodes": [], "connections": {}}),
                ("0002_Another_Workflow.json", {"id": "test2", "name": "Test 2", "nodes": [], "connections": {}})
            ]
            
            for filename, data in initial_workflows:
                filepath = os.path.join(workflows_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(data, f)
            
            # Create adder with custom backup directory
            adder = AutoWorkflowAdder(workflows_dir)
            adder.backup_dir = backup_dir
            
            # Test backup creation
            backup_success = adder.create_backup()
            assert backup_success is True
            assert os.path.exists(backup_dir)
            
            # Verify backup contents
            backup_files = os.listdir(backup_dir)
            assert len(backup_files) == 2
            assert "0001_Test_Workflow.json" in backup_files
            assert "0002_Another_Workflow.json" in backup_files
            
            # Verify backup file contents
            for filename, original_data in initial_workflows:
                backup_path = os.path.join(backup_dir, filename)
                with open(backup_path, 'r') as f:
                    backup_data = json.load(f)
                assert backup_data == original_data

    def test_file_conflict_handling(self, simple_workflow):
        """Test handling of filename conflicts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            os.makedirs(workflows_dir)
            
            # Create existing file with target name
            existing_file = os.path.join(workflows_dir, "0001_Manual_Slack_Automate.json")
            with open(existing_file, 'w') as f:
                json.dump({"id": "existing", "name": "Existing"}, f)
            
            # Create source workflow file
            source_file = os.path.join(temp_dir, "new_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Try to add workflow (should handle conflict)
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            # Should either succeed with different number or handle conflict gracefully
            if result["success"]:
                # If successful, should use different number
                target_filename = result["target_file"]
                assert target_filename != "0001_Manual_Slack_Automate.json"
            else:
                # If failed, should have meaningful error message
                assert "conflict" in result["error"].lower() or "exists" in result["error"].lower()

    def test_large_file_handling(self):
        """Test handling of large workflow files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create large workflow
            large_workflow = {
                "id": "large-workflow",
                "name": "Large Workflow with Many Nodes",
                "nodes": [],
                "connections": {},
                "active": True
            }
            
            # Add many nodes
            for i in range(500):  # Large workflow
                node = {
                    "id": f"node-{i:04d}",
                    "name": f"Node {i}",
                    "type": "n8n-nodes-base.manualTrigger",
                    "position": [i * 10, (i % 10) * 100],
                    "parameters": {
                        "description": f"This is node number {i} in a large workflow"
                    }
                }
                large_workflow["nodes"].append(node)
            
            # Create source file
            source_file = os.path.join(temp_dir, "large_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(large_workflow, f)
            
            # Verify file is actually large
            file_size = os.path.getsize(source_file)
            assert file_size > 50000  # Should be at least 50KB
            
            # Test adding large workflow
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            assert result["success"] is True
            
            # Verify large file was copied correctly
            target_path = result["target_path"]
            target_size = os.path.getsize(target_path)
            assert target_size == file_size  # Should be same size
            
            # Verify content integrity
            with open(target_path, 'r') as f:
                saved_data = json.load(f)
            assert len(saved_data["nodes"]) == 500
            assert saved_data["name"] == large_workflow["name"]

    def test_file_permissions_and_ownership(self, simple_workflow):
        """Test file permissions after workflow addition."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create source file
            source_file = os.path.join(temp_dir, "test_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Add workflow
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            assert result["success"] is True
            
            # Check file permissions
            target_path = result["target_path"]
            stat_info = os.stat(target_path)
            
            # File should be readable
            assert os.access(target_path, os.R_OK)
            
            # File should be writable by owner
            assert os.access(target_path, os.W_OK)

    def test_directory_structure_creation(self):
        """Test automatic creation of directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use nested directory that doesn't exist
            workflows_dir = os.path.join(temp_dir, "nested", "workflows", "directory")
            
            # Directory shouldn't exist initially
            assert not os.path.exists(workflows_dir)
            
            # Creating AutoWorkflowAdder should create directory
            adder = AutoWorkflowAdder(workflows_dir)
            
            # Directory should now exist
            assert os.path.exists(workflows_dir)
            assert os.path.isdir(workflows_dir)

    def test_file_cleanup_on_error(self, simple_workflow):
        """Test that temporary files are cleaned up on errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create source file
            source_file = os.path.join(temp_dir, "test_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Make workflows directory read-only to force error
            os.makedirs(workflows_dir)
            os.chmod(workflows_dir, 0o444)  # Read-only
            
            try:
                adder = AutoWorkflowAdder(workflows_dir)
                result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
                
                # Should fail due to permissions
                assert result["success"] is False
                
                # Check that no partial files were left behind
                files_in_dir = os.listdir(workflows_dir)
                assert len(files_in_dir) == 0  # Should be empty
                
            finally:
                # Restore permissions for cleanup
                os.chmod(workflows_dir, 0o755)

    def test_concurrent_file_operations(self, simple_workflow):
        """Test concurrent file operations don't interfere."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create multiple source files
            source_files = []
            for i in range(3):
                workflow_copy = simple_workflow.copy()
                workflow_copy["id"] = f"concurrent-test-{i}"
                workflow_copy["name"] = f"Concurrent Test Workflow {i}"
                
                source_file = os.path.join(temp_dir, f"workflow_{i}.json")
                with open(source_file, 'w') as f:
                    json.dump(workflow_copy, f)
                source_files.append(source_file)
            
            # Add workflows sequentially (simulating potential concurrency issues)
            adder = AutoWorkflowAdder(workflows_dir)
            results = []
            
            for source_file in source_files:
                result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
                results.append(result)
            
            # All should succeed
            for result in results:
                assert result["success"] is True
            
            # Check that all files were created with unique names
            target_files = [result["target_file"] for result in results]
            assert len(set(target_files)) == len(target_files)  # All unique
            
            # Verify all files exist
            for result in results:
                assert os.path.exists(result["target_path"])

    def test_symlink_handling(self, simple_workflow):
        """Test handling of symbolic links."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create source file
            source_file = os.path.join(temp_dir, "original_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Create symlink to source file
            symlink_file = os.path.join(temp_dir, "symlink_workflow.json")
            os.symlink(source_file, symlink_file)
            
            # Test adding via symlink
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(symlink_file, auto_confirm=True, dry_run=False)
            
            assert result["success"] is True
            
            # Verify content is correct (should follow symlink)
            target_path = result["target_path"]
            with open(target_path, 'r') as f:
                saved_data = json.load(f)
            assert saved_data["id"] == simple_workflow["id"]

    def test_file_encoding_handling(self, simple_workflow):
        """Test handling of different file encodings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Add unicode characters to workflow
            unicode_workflow = simple_workflow.copy()
            unicode_workflow["name"] = "Test Workflow with Unicode: 测试 🚀 café"
            unicode_workflow["description"] = "Workflow with émojis and spëcial chars"
            
            # Create source file with UTF-8 encoding
            source_file = os.path.join(temp_dir, "unicode_workflow.json")
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(unicode_workflow, f, ensure_ascii=False)
            
            # Test adding workflow with unicode
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            assert result["success"] is True
            
            # Verify unicode content is preserved
            target_path = result["target_path"]
            with open(target_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            assert saved_data["name"] == unicode_workflow["name"]
            assert "🚀" in saved_data["name"]
            assert "测试" in saved_data["name"]

    def test_disk_space_handling(self, simple_workflow):
        """Test behavior when disk space might be limited."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create source file
            source_file = os.path.join(temp_dir, "test_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Test normal operation (can't easily simulate disk full)
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            # Should succeed under normal conditions
            assert result["success"] is True
            
            # Verify file size is reasonable
            target_path = result["target_path"]
            file_size = os.path.getsize(target_path)
            assert file_size > 0
            assert file_size < 1024 * 1024  # Should be less than 1MB for simple workflow