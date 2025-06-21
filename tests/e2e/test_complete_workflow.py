"""
End-to-end tests for complete workflow scenarios.
Tests full user workflows from start to finish.
"""

import pytest
import json
import tempfile
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from new_workflow_analyzer import NewWorkflowAnalyzer
from auto_add_workflow import AutoWorkflowAdder


class TestCompleteWorkflowScenarios:
    """Test complete end-to-end workflow scenarios."""

    def test_complete_workflow_addition_scenario(self, complex_workflow):
        """Test complete scenario: analyze → add → verify."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Step 1: Create workflow file (simulating export from n8n)
            source_file = os.path.join(temp_dir, "exported_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(complex_workflow, f)
            
            # Step 2: Analyze workflow (user runs analyzer)
            analyzer = NewWorkflowAnalyzer(workflows_dir)
            analysis_result = analyzer.analyze_workflow_file(source_file)
            
            assert analysis_result["success"] is True
            assert "GitHub" in analysis_result["services"]
            assert "Discord" in analysis_result["services"]
            assert analysis_result["trigger_type"] == "Webhook"
            
            suggested_filename = analysis_result["suggested_filename"]
            assert suggested_filename.endswith(".json")
            assert "GitHub" in suggested_filename or "Discord" in suggested_filename
            
            # Step 3: Add workflow to repository (user confirms addition)
            adder = AutoWorkflowAdder(workflows_dir)
            add_result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            assert add_result["success"] is True
            assert add_result["action"] == "added"
            
            # Step 4: Verify workflow is in repository
            target_path = add_result["target_path"]
            assert os.path.exists(target_path)
            
            # Step 5: Verify content integrity
            with open(target_path, 'r') as f:
                saved_workflow = json.load(f)
            
            assert saved_workflow["id"] == complex_workflow["id"]
            assert saved_workflow["name"] == complex_workflow["name"]
            assert len(saved_workflow["nodes"]) == len(complex_workflow["nodes"])
            
            # Step 6: Verify workflow can be analyzed again (repository consistency)
            new_analysis = analyzer.analyze_workflow_file(target_path)
            assert new_analysis["success"] is True

    def test_batch_workflow_addition_scenario(self):
        """Test adding multiple workflows in batch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            downloads_dir = os.path.join(temp_dir, "downloads")
            os.makedirs(downloads_dir)
            
            # Create multiple workflow files (simulating downloads)
            workflow_files = []
            for i in range(5):
                workflow = {
                    "id": f"batch-test-{i:03d}",
                    "name": f"Batch Test Workflow {i}",
                    "nodes": [
                        {
                            "id": f"trigger-{i}",
                            "name": f"Trigger {i}",
                            "type": "n8n-nodes-base.manualTrigger"
                        },
                        {
                            "id": f"action-{i}",
                            "name": f"Action {i}",
                            "type": f"n8n-nodes-base.{'slack' if i % 2 == 0 else 'gmail'}"
                        }
                    ],
                    "connections": {},
                    "active": True
                }
                
                file_path = os.path.join(downloads_dir, f"workflow_{i}.json")
                with open(file_path, 'w') as f:
                    json.dump(workflow, f)
                workflow_files.append(file_path)
            
            # Add all workflows in batch
            adder = AutoWorkflowAdder(workflows_dir)
            batch_result = adder.add_multiple_workflows(workflow_files, auto_confirm=True, dry_run=False)
            
            assert batch_result["success"] is True
            assert batch_result["total_files"] == 5
            assert batch_result["successful"] == 5
            assert batch_result["failed"] == 0
            
            # Verify all workflows were added
            added_files = os.listdir(workflows_dir)
            assert len(added_files) == 5
            
            # Verify sequential numbering
            for added_file in added_files:
                assert added_file.startswith("000")
                assert added_file.endswith(".json")

    def test_error_recovery_scenario(self):
        """Test error recovery in various failure scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Scenario 1: Invalid JSON file
            invalid_file = os.path.join(temp_dir, "invalid.json")
            with open(invalid_file, 'w') as f:
                f.write('{"invalid": json syntax}')
            
            analyzer = NewWorkflowAnalyzer(workflows_dir)
            result = analyzer.analyze_workflow_file(invalid_file)
            
            # Should handle error gracefully
            assert result is None or result.get("success") is False
            
            # Scenario 2: Missing required fields
            incomplete_workflow = {
                "id": "incomplete",
                "name": "Incomplete Workflow"
                # Missing nodes, connections
            }
            
            incomplete_file = os.path.join(temp_dir, "incomplete.json")
            with open(incomplete_file, 'w') as f:
                json.dump(incomplete_workflow, f)
            
            result = analyzer.analyze_workflow_file(incomplete_file)
            # Should still try to analyze even if incomplete
            
            # Scenario 3: Non-existent file
            result = analyzer.analyze_workflow_file("/non/existent/file.json")
            assert result is None

    def test_repository_growth_scenario(self, simple_workflow):
        """Test repository growth with sequential numbering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create initial repository state
            initial_workflows = [
                ("0001_Initial_Workflow.json", {"id": "initial-1"}),
                ("0003_Another_Workflow.json", {"id": "initial-3"}),
                ("0005_Third_Workflow.json", {"id": "initial-5"})
            ]
            
            os.makedirs(workflows_dir)
            for filename, data in initial_workflows:
                filepath = os.path.join(workflows_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump({**data, "name": "Test", "nodes": [], "connections": {}}, f)
            
            # Add new workflow
            source_file = os.path.join(temp_dir, "new_workflow.json")
            with open(source_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            assert result["success"] is True
            
            # Should get next available number (0006)
            target_filename = result["target_file"]
            assert target_filename.startswith("0006")

    def test_naming_convention_consistency(self):
        """Test that naming conventions are consistently applied."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Test various workflow types
            test_workflows = [
                {
                    "id": "test-slack",
                    "name": "Slack Notification System",
                    "nodes": [
                        {"type": "n8n-nodes-base.webhook"},
                        {"type": "n8n-nodes-base.slack"}
                    ]
                },
                {
                    "id": "test-gmail", 
                    "name": "Email Processing Automation",
                    "nodes": [
                        {"type": "n8n-nodes-base.cron"},
                        {"type": "n8n-nodes-base.gmail"}
                    ]
                },
                {
                    "id": "test-complex",
                    "name": "Multi-Service Integration",
                    "nodes": [
                        {"type": "n8n-nodes-base.manualTrigger"},
                        {"type": "n8n-nodes-base.github"},
                        {"type": "n8n-nodes-base.discord"},
                        {"type": "n8n-nodes-base.airtable"}
                    ]
                }
            ]
            
            adder = AutoWorkflowAdder(workflows_dir)
            results = []
            
            for workflow in test_workflows:
                # Add required fields
                workflow.update({"connections": {}, "active": True})
                
                source_file = os.path.join(temp_dir, f"{workflow['id']}.json")
                with open(source_file, 'w') as f:
                    json.dump(workflow, f)
                
                result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
                results.append(result)
            
            # Verify all succeeded
            for result in results:
                assert result["success"] is True
            
            # Verify naming consistency
            target_files = [result["target_file"] for result in results]
            
            for target_file in target_files:
                # Should follow XXXX_Service_Purpose pattern
                parts = target_file.replace(".json", "").split("_")
                assert len(parts) >= 3  # At least number, service, purpose
                assert parts[0].isdigit()  # First part is number
                assert len(parts[0]) == 4  # Four-digit number

    def test_web_interface_simulation(self, simple_workflow):
        """Test simulating web interface workflow addition."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Simulate file upload (like web interface would do)
            uploaded_file = os.path.join(temp_dir, "uploaded_workflow.json")
            with open(uploaded_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Step 1: Analyze (like /api/analyze-workflow endpoint)
            analyzer = NewWorkflowAnalyzer(workflows_dir)
            analysis = analyzer.analyze_workflow_file(uploaded_file)
            
            assert analysis["success"] is True
            
            # Step 2: Show preview to user (simulated)
            preview_data = {
                "original_filename": "uploaded_workflow.json",
                "suggested_filename": analysis["suggested_filename"],
                "workflow_name": analysis["workflow_name"],
                "services": analysis["services"],
                "purpose": analysis["purpose"],
                "trigger_type": analysis["trigger_type"],
                "node_count": analysis["node_count"]
            }
            
            # Verify preview data is complete
            assert preview_data["suggested_filename"] != ""
            assert preview_data["workflow_name"] != ""
            assert isinstance(preview_data["services"], list)
            
            # Step 3: User confirms, add workflow (like /api/add-workflow endpoint)
            adder = AutoWorkflowAdder(workflows_dir)
            add_result = adder.add_workflow(uploaded_file, auto_confirm=True, dry_run=False)
            
            assert add_result["success"] is True
            assert add_result["target_file"] == analysis["suggested_filename"]
            
            # Step 4: Cleanup uploaded file (like web interface would do)
            os.unlink(uploaded_file)
            
            # Verify workflow is in repository
            target_path = add_result["target_path"]
            assert os.path.exists(target_path)

    def test_cli_tool_integration(self, simple_workflow):
        """Test command-line tool integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows") 
            
            # Create test workflow file
            test_file = os.path.join(temp_dir, "cli_test.json")
            with open(test_file, 'w') as f:
                json.dump(simple_workflow, f)
            
            # Test analyzer CLI (would be: python new_workflow_analyzer.py file.json)
            analyzer = NewWorkflowAnalyzer(workflows_dir)
            result = analyzer.analyze_and_suggest(test_file, verbose=False)
            
            assert result["success"] is True
            suggested_name = result["suggested_filename"]
            
            # Test adder CLI (would be: python auto_add_workflow.py file.json)
            adder = AutoWorkflowAdder(workflows_dir)
            add_result = adder.add_workflow(test_file, auto_confirm=True, dry_run=False)
            
            assert add_result["success"] is True
            assert add_result["target_file"] == suggested_name

    def test_performance_with_multiple_workflows(self):
        """Test performance with multiple workflow operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create many workflow files
            num_workflows = 20
            workflow_files = []
            
            for i in range(num_workflows):
                workflow = {
                    "id": f"perf-test-{i:03d}",
                    "name": f"Performance Test Workflow {i}",
                    "nodes": [
                        {
                            "id": f"node-{i}-1",
                            "type": "n8n-nodes-base.manualTrigger"
                        },
                        {
                            "id": f"node-{i}-2", 
                            "type": f"n8n-nodes-base.{'slack' if i % 3 == 0 else 'gmail' if i % 3 == 1 else 'discord'}"
                        }
                    ],
                    "connections": {},
                    "active": True
                }
                
                file_path = os.path.join(temp_dir, f"workflow_{i:03d}.json")
                with open(file_path, 'w') as f:
                    json.dump(workflow, f)
                workflow_files.append(file_path)
            
            # Test batch addition performance
            import time
            start_time = time.time()
            
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_multiple_workflows(workflow_files, auto_confirm=True, dry_run=False)
            
            end_time = time.time()
            duration = end_time - start_time
            
            assert result["success"] is True
            assert result["successful"] == num_workflows
            
            # Should complete reasonably quickly (adjust threshold as needed)
            assert duration < 30  # Should take less than 30 seconds
            
            # Verify all files were created
            added_files = os.listdir(workflows_dir)
            assert len(added_files) == num_workflows

    def test_data_integrity_verification(self, complex_workflow):
        """Test data integrity throughout the complete process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workflows_dir = os.path.join(temp_dir, "workflows")
            
            # Create source file
            source_file = os.path.join(temp_dir, "integrity_test.json")
            with open(source_file, 'w') as f:
                json.dump(complex_workflow, f, sort_keys=True, indent=2)
            
            # Calculate original checksum
            import hashlib
            with open(source_file, 'rb') as f:
                original_hash = hashlib.md5(f.read()).hexdigest()
            
            # Add workflow
            adder = AutoWorkflowAdder(workflows_dir)
            result = adder.add_workflow(source_file, auto_confirm=True, dry_run=False)
            
            assert result["success"] is True
            
            # Verify data integrity
            target_path = result["target_path"]
            
            # Read both files and compare content
            with open(source_file, 'r') as f:
                original_data = json.load(f)
            
            with open(target_path, 'r') as f:
                copied_data = json.load(f)
            
            # Content should be identical
            assert original_data == copied_data
            
            # Verify all key fields
            assert copied_data["id"] == complex_workflow["id"]
            assert copied_data["name"] == complex_workflow["name"]
            assert len(copied_data["nodes"]) == len(complex_workflow["nodes"])
            assert copied_data["connections"] == complex_workflow["connections"]
            
            # Verify node integrity
            for i, node in enumerate(copied_data["nodes"]):
                original_node = complex_workflow["nodes"][i]
                assert node["id"] == original_node["id"]
                assert node["type"] == original_node["type"]