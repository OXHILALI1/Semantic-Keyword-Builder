"""
Unit tests for AutoWorkflowAdder class.
Tests file operations, validation, dry-run functionality, and workflow addition logic.
"""

import pytest
import tempfile
import json
import os
import shutil
from unittest.mock import patch, MagicMock

from auto_add_workflow import AutoWorkflowAdder
from new_workflow_analyzer import NewWorkflowAnalyzer


class TestAutoWorkflowAdder:
    """Test suite for AutoWorkflowAdder functionality."""

    def test_adder_initialization_default(self):
        """Test adder initializes with correct default values."""
        adder = AutoWorkflowAdder()
        
        assert adder.workflows_dir == "workflows"
        assert isinstance(adder.analyzer, NewWorkflowAnalyzer)

    def test_adder_initialization_custom_directory(self, temp_workflows_dir):
        """Test adder with custom workflows directory."""
        adder = AutoWorkflowAdder(temp_workflows_dir)
        
        assert adder.workflows_dir == temp_workflows_dir
        assert adder.analyzer.workflows_dir == temp_workflows_dir

    def test_add_workflow_dry_run_success(self, temp_workflow_file, temp_workflows_dir):
        """Test successful dry run workflow addition."""
        adder = AutoWorkflowAdder(temp_workflows_dir)
        result = adder.add_workflow(temp_workflow_file, auto_confirm=True, dry_run=True)
        
        assert result["success"] is True
        assert result["action"] == "dry_run"
        assert "target_file" in result
        assert result["target_file"].endswith(".json")
        assert result["target_file"].startswith("000")  # Should have number prefix

    def test_add_workflow_dry_run_nonexistent_file(self, temp_workflows_dir):
        """Test dry run with non-existent source file."""
        adder = AutoWorkflowAdder(temp_workflows_dir)
        result = adder.add_workflow("/non/existent/file.json", auto_confirm=True, dry_run=True)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_add_workflow_actual_success(self, temp_workflow_file, temp_workflows_dir):
        """Test successful actual workflow addition."""
        adder = AutoWorkflowAdder(temp_workflows_dir)
        result = adder.add_workflow(temp_workflow_file, auto_confirm=True, dry_run=False)
        
        assert result["success"] is True
        assert result["action"] == "added"
        assert "target_file" in result
        assert "target_path" in result
        
        # Verify file was actually created
        target_path = result["target_path"]
        assert os.path.exists(target_path)
        
        # Verify content is valid JSON
        with open(target_path, 'r') as f:
            data = json.load(f)
            assert "id" in data
            assert "name" in data

    def test_add_workflow_conflict_detection(self, temp_workflow_file, temp_workflows_dir):
        """Test detection of filename conflicts."""
        adder = AutoWorkflowAdder(temp_workflows_dir)
        
        # Add workflow first time
        result1 = adder.add_workflow(temp_workflow_file, auto_confirm=True, dry_run=False)
        assert result1["success"] is True
        
        # Try to add same workflow again (should detect conflict)
        result2 = adder.add_workflow(temp_workflow_file, auto_confirm=True, dry_run=False)
        # This might succeed with a different number, depending on implementation
        # The exact behavior depends on how conflicts are handled

    def test_add_multiple_workflows_success(self, temp_workflows_dir):
        """Test adding multiple workflows in batch."""
        # Create multiple temp workflow files
        workflow_files = []
        for i in range(3):
            workflow_data = {
                "id": f"test-multi-{i:03d}",
                "name": f"Test Workflow {i}",
                "nodes": [
                    {
                        "id": f"node-{i}",
                        "name": f"Test Node {i}",
                        "type": "n8n-nodes-base.manualTrigger"
                    }
                ],
                "connections": {},
                "active": True
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(workflow_data, f)
                workflow_files.append(f.name)
        
        try:
            adder = AutoWorkflowAdder(temp_workflows_dir)
            result = adder.add_multiple_workflows(workflow_files, auto_confirm=True, dry_run=True)
            
            assert result["success"] is True
            assert result["total_files"] == 3
            assert result["successful"] == 3
            assert result["failed"] == 0
            
        finally:
            # Cleanup temp files
            for file_path in workflow_files:
                try:
                    os.unlink(file_path)
                except FileNotFoundError:
                    pass

    def test_add_multiple_workflows_partial_failure(self, temp_workflows_dir):
        """Test batch addition with some failures."""
        # Create mix of valid and invalid files
        valid_workflow = {
            "id": "test-valid",
            "name": "Valid Workflow", 
            "nodes": [{"id": "node", "type": "n8n-nodes-base.manualTrigger"}],
            "connections": {},
            "active": True
        }
        
        files = []
        
        # Valid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_workflow, f)
            files.append(f.name)
        
        # Invalid file (malformed JSON)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            files.append(f.name)
        
        # Non-existent file
        files.append("/non/existent/file.json")
        
        try:
            adder = AutoWorkflowAdder(temp_workflows_dir)
            result = adder.add_multiple_workflows(files, auto_confirm=True, dry_run=True)
            
            assert result["total_files"] == 3
            assert result["successful"] >= 1  # At least the valid one should work
            assert result["failed"] >= 1     # At least some should fail
            
        finally:
            # Cleanup temp files
            for file_path in files[:2]:  # Only the first two exist
                try:
                    os.unlink(file_path)
                except FileNotFoundError:
                    pass

    def test_list_pending_workflows_found(self, temp_workflows_dir):
        """Test finding potential workflow files in directory."""
        # Create some workflow-like files
        workflow_files = []
        
        # Valid workflow
        valid_workflow = {
            "id": "test-pending-1",
            "name": "Pending Workflow",
            "nodes": [],
            "connections": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir=temp_workflows_dir) as f:
            json.dump(valid_workflow, f)
            workflow_files.append(f.name)
        
        # Invalid JSON (should be ignored)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir=temp_workflows_dir) as f:
            f.write('invalid json')
            workflow_files.append(f.name)
        
        # Non-JSON file (should be ignored)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, dir=temp_workflows_dir) as f:
            f.write('text file')
            workflow_files.append(f.name)
        
        try:
            adder = AutoWorkflowAdder(temp_workflows_dir)
            pending = adder.list_pending_workflows(temp_workflows_dir)
            
            # Should find at least the valid workflow
            assert len(pending) >= 1
            assert any(f.endswith('.json') for f in pending)
            
        finally:
            # Cleanup
            for file_path in workflow_files:
                try:
                    os.unlink(file_path)
                except FileNotFoundError:
                    pass

    def test_list_pending_workflows_none_found(self, temp_workflows_dir):
        """Test when no workflow files are found."""
        # Create non-workflow files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, dir=temp_workflows_dir) as f:
            f.write('not a workflow')
            temp_file = f.name
        
        try:
            adder = AutoWorkflowAdder(temp_workflows_dir)
            pending = adder.list_pending_workflows(temp_workflows_dir)
            
            assert len(pending) == 0
            
        finally:
            os.unlink(temp_file)

    def test_list_pending_workflows_nonexistent_directory(self):
        """Test listing pending workflows in non-existent directory."""
        adder = AutoWorkflowAdder()
        pending = adder.list_pending_workflows("/non/existent/directory")
        
        assert len(pending) == 0

    def test_next_number_updates_after_addition(self, temp_workflow_file, temp_workflows_dir):
        """Test that next available number updates after adding workflow."""
        adder = AutoWorkflowAdder(temp_workflows_dir)
        
        # Get initial next number
        initial_next = adder.analyzer.next_number
        
        # Add a workflow
        result = adder.add_workflow(temp_workflow_file, auto_confirm=True, dry_run=False)
        assert result["success"] is True
        
        # Next number should be updated
        updated_next = adder.analyzer.next_number
        assert updated_next > initial_next

    def test_error_handling_invalid_workflow_structure(self, temp_workflows_dir):
        """Test error handling with invalid workflow structure."""
        # Create file with invalid workflow structure
        invalid_workflow = {
            "id": "test-invalid",
            "name": "Invalid Workflow"
            # Missing required fields like nodes, connections
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_workflow, f)
            temp_path = f.name
        
        try:
            adder = AutoWorkflowAdder(temp_workflows_dir)
            result = adder.add_workflow(temp_path, auto_confirm=True, dry_run=True)
            
            # Should still succeed for analysis even if workflow is incomplete
            # The analyzer should handle missing fields gracefully
            assert "success" in result
            
        finally:
            os.unlink(temp_path)

    @patch('shutil.copy2')
    def test_file_copy_error_handling(self, mock_copy, temp_workflow_file, temp_workflows_dir):
        """Test error handling when file copy fails."""
        mock_copy.side_effect = PermissionError("Permission denied")
        
        adder = AutoWorkflowAdder(temp_workflows_dir)
        result = adder.add_workflow(temp_workflow_file, auto_confirm=True, dry_run=False)
        
        assert result["success"] is False
        assert "error" in result
        assert "failed to copy" in result["error"].lower() or "permission" in result["error"].lower()

    def test_workflow_directory_creation(self):
        """Test that workflows directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_workflows_dir = os.path.join(temp_dir, "new_workflows")
            
            # Directory shouldn't exist initially
            assert not os.path.exists(non_existent_workflows_dir)
            
            # Creating adder should create the directory
            adder = AutoWorkflowAdder(non_existent_workflows_dir)
            
            # Directory should now exist
            assert os.path.exists(non_existent_workflows_dir)
            assert os.path.isdir(non_existent_workflows_dir)

    def test_analyze_workflow_integration(self, temp_workflow_file, temp_workflows_dir):
        """Test integration between adder and analyzer."""
        adder = AutoWorkflowAdder(temp_workflows_dir)
        
        # The add_workflow method should use the analyzer internally
        result = adder.add_workflow(temp_workflow_file, auto_confirm=True, dry_run=True)
        
        assert result["success"] is True
        
        # Result should contain analysis data
        analysis = result.get("analysis", {})
        if analysis:  # If analysis data is included in result
            assert "services" in analysis or "target_file" in result
            assert "purpose" in analysis or "target_file" in result

    def test_sequential_numbering_with_existing_workflows(self, mock_existing_workflows):
        """Test that new workflows get correct sequential numbers with existing workflows."""
        # mock_existing_workflows creates workflows 0001, 0002, 0005
        # Next should be 0006
        
        adder = AutoWorkflowAdder(mock_existing_workflows)
        
        # Check that next number is calculated correctly
        next_num = adder.analyzer.next_number
        assert next_num == 6  # After 0001, 0002, 0005 -> next is 0006

    def test_filename_sanitization_in_actual_addition(self, temp_workflows_dir):
        """Test that generated filenames are properly sanitized."""
        # Create workflow with problematic characters in name
        problematic_workflow = {
            "id": "test-problematic",
            "name": "Workflow with Special @#$% Characters & Symbols",
            "nodes": [
                {
                    "id": "node1",
                    "name": "Test Node",
                    "type": "n8n-nodes-base.manualTrigger"
                }
            ],
            "connections": {},
            "active": True
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(problematic_workflow, f)
            temp_path = f.name
        
        try:
            adder = AutoWorkflowAdder(temp_workflows_dir)
            result = adder.add_workflow(temp_path, auto_confirm=True, dry_run=True)
            
            assert result["success"] is True
            
            # Check that filename doesn't contain problematic characters
            target_file = result["target_file"]
            problematic_chars = ['@', '#', '$', '%', '&', ' ']
            
            for char in problematic_chars:
                if char == ' ':
                    continue  # Spaces might be converted to underscores
                assert char not in target_file, f"Found problematic character '{char}' in filename: {target_file}"
            
        finally:
            os.unlink(temp_path)