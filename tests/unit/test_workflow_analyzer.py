"""
Unit tests for NewWorkflowAnalyzer class.
Tests service detection, purpose inference, filename generation, and other core logic.
"""

import pytest
import tempfile
import json
import os
from unittest.mock import patch, MagicMock

from new_workflow_analyzer import NewWorkflowAnalyzer


class TestNewWorkflowAnalyzer:
    """Test suite for NewWorkflowAnalyzer functionality."""

    def test_analyzer_initialization(self):
        """Test analyzer initializes with correct default values."""
        analyzer = NewWorkflowAnalyzer()
        
        assert analyzer.workflows_dir == "workflows"
        assert isinstance(analyzer.existing_numbers, set)
        assert isinstance(analyzer.next_number, int)

    def test_analyzer_with_custom_directory(self):
        """Test analyzer with custom workflows directory."""
        custom_dir = "custom_workflows"
        analyzer = NewWorkflowAnalyzer(custom_dir)
        
        assert analyzer.workflows_dir == custom_dir

    def test_service_detection_single_service(self, simple_workflow):
        """Test detection of single service (Slack)."""
        analyzer = NewWorkflowAnalyzer()
        services, trigger_type = analyzer._analyze_nodes(simple_workflow["nodes"])
        
        assert "Slack" in services
        assert trigger_type == "Triggered"  # Manual trigger defaults to Triggered

    def test_service_detection_multiple_services(self, complex_workflow):
        """Test detection of multiple services."""
        analyzer = NewWorkflowAnalyzer()
        services, trigger_type = analyzer._analyze_nodes(complex_workflow["nodes"])
        
        expected_services = {"Webhook", "GitHub", "Discord", "Gmail"}
        assert expected_services.issubset(services)
        assert trigger_type == "Webhook"

    def test_trigger_type_detection_webhook(self, complex_workflow):
        """Test webhook trigger detection."""
        analyzer = NewWorkflowAnalyzer()
        _, trigger_type = analyzer._analyze_nodes(complex_workflow["nodes"])
        
        assert trigger_type == "Webhook"

    def test_trigger_type_detection_scheduled(self, scheduled_workflow):
        """Test scheduled trigger detection."""
        analyzer = NewWorkflowAnalyzer()
        _, trigger_type = analyzer._analyze_nodes(scheduled_workflow["nodes"])
        
        assert trigger_type == "Scheduled"

    def test_trigger_type_detection_manual(self, simple_workflow):
        """Test manual trigger detection."""
        analyzer = NewWorkflowAnalyzer()
        _, trigger_type = analyzer._analyze_nodes(simple_workflow["nodes"])
        
        assert trigger_type == "Triggered"

    def test_purpose_detection_from_name(self):
        """Test purpose detection from workflow name."""
        analyzer = NewWorkflowAnalyzer()
        
        test_cases = [
            ("Create New User Account", "Create"),
            ("Update Customer Information", "Update"),
            ("Sync Data Between Systems", "Sync"),
            ("Send Daily Newsletter", "Send"),
            ("Import Customer Records", "Import"),
            ("Export Sales Report", "Export"),
            ("Monitor System Health", "Monitor"),
            ("Process Payment Data", "Process"),
            ("Automate Workflow Tasks", "Automate"),
            ("Unknown Task Type", "Automation")  # Default fallback
        ]
        
        for name, expected_purpose in test_cases:
            purpose = analyzer._determine_purpose(name, [])
            assert purpose == expected_purpose

    def test_purpose_detection_from_nodes(self):
        """Test purpose detection from node types when name is ambiguous."""
        analyzer = NewWorkflowAnalyzer()
        
        # Test with nodes that have 'create' in type
        create_nodes = [{"type": "n8n-nodes-base.createSomething"}]
        purpose = analyzer._determine_purpose("Generic Workflow", create_nodes)
        assert purpose == "Create"
        
        # Test with nodes that have 'update' in type
        update_nodes = [{"type": "n8n-nodes-base.updateRecord"}]
        purpose = analyzer._determine_purpose("Generic Workflow", update_nodes)
        assert purpose == "Update"

    def test_filename_generation_simple(self):
        """Test filename generation for simple workflow."""
        analyzer = NewWorkflowAnalyzer()
        
        workflow_data = {
            "services": ["Slack"],
            "purpose": "Send",
            "trigger_type": "Manual"
        }
        
        filename = analyzer._generate_new_filename(workflow_data, 1)
        assert filename == "0001_Slack_Send.json"

    def test_filename_generation_multiple_services(self):
        """Test filename generation with multiple services (max 2)."""
        analyzer = NewWorkflowAnalyzer()
        
        workflow_data = {
            "services": ["GitHub", "Discord", "Gmail", "Slack"],  # 4 services, should take first 2
            "purpose": "Notify",
            "trigger_type": "Webhook"
        }
        
        filename = analyzer._generate_new_filename(workflow_data, 5)
        assert filename == "0005_Discord_GitHub_Notify_Webhook.json"  # Sorted alphabetically

    def test_filename_generation_no_services(self):
        """Test filename generation when no services detected."""
        analyzer = NewWorkflowAnalyzer()
        
        workflow_data = {
            "services": [],
            "purpose": "Process",
            "trigger_type": "Manual"
        }
        
        filename = analyzer._generate_new_filename(workflow_data, 10)
        assert filename == "0010_Manual_Process.json"

    def test_filename_generation_special_characters(self):
        """Test filename generation removes special characters."""
        analyzer = NewWorkflowAnalyzer()
        
        # Mock workflow with special characters in services/purpose
        workflow_data = {
            "services": ["Test@Service", "Another#Service"],
            "purpose": "Create&Update",
            "trigger_type": "Manual"
        }
        
        filename = analyzer._generate_new_filename(workflow_data, 1)
        # Should remove special characters and clean up
        assert "@" not in filename
        assert "#" not in filename
        assert "&" not in filename
        assert filename.endswith(".json")

    def test_complexity_determination(self):
        """Test workflow complexity determination based on node count."""
        analyzer = NewWorkflowAnalyzer()
        
        assert analyzer._determine_complexity(3) == "Simple"  # ≤5 nodes
        assert analyzer._determine_complexity(10) == "Standard"  # 6-15 nodes
        assert analyzer._determine_complexity(20) == "Complex"  # 16+ nodes

    def test_credentials_detection_with_credentials(self):
        """Test detection of workflows that use credentials."""
        analyzer = NewWorkflowAnalyzer()
        
        nodes_with_creds = [
            {"credentials": {"gmail": {"id": "1", "name": "Gmail Account"}}},
            {"type": "n8n-nodes-base.slack"}
        ]
        
        assert analyzer._has_credentials(nodes_with_creds) is True

    def test_credentials_detection_without_credentials(self):
        """Test detection of workflows that don't use credentials."""
        analyzer = NewWorkflowAnalyzer()
        
        nodes_without_creds = [
            {"type": "n8n-nodes-base.manualTrigger"},
            {"type": "n8n-nodes-base.function"}
        ]
        
        assert analyzer._has_credentials(nodes_without_creds) is False

    def test_analyze_workflow_file_success(self, temp_workflow_file):
        """Test successful workflow file analysis."""
        analyzer = NewWorkflowAnalyzer()
        result = analyzer.analyze_workflow_file(temp_workflow_file)
        
        assert result["success"] is True
        assert "suggested_filename" in result
        assert "services" in result
        assert "purpose" in result
        assert "trigger_type" in result
        assert "next_number" in result

    def test_analyze_workflow_file_invalid_json(self):
        """Test analysis of invalid JSON file."""
        analyzer = NewWorkflowAnalyzer()
        
        # Create temp file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            temp_path = f.name
        
        try:
            result = analyzer.analyze_workflow_file(temp_path)
            assert result is None  # Should return None for invalid JSON
        finally:
            os.unlink(temp_path)

    def test_analyze_workflow_file_missing_file(self):
        """Test analysis of non-existent file."""
        analyzer = NewWorkflowAnalyzer()
        result = analyzer.analyze_workflow_file("/non/existent/file.json")
        
        assert result is None

    @patch('os.path.exists')
    @patch('glob.glob')
    def test_get_existing_numbers(self, mock_glob, mock_exists):
        """Test extraction of existing workflow numbers."""
        mock_exists.return_value = True
        mock_glob.return_value = [
            "workflows/0001_Test.json",
            "workflows/0005_Another.json", 
            "workflows/0010_Third.json",
            "workflows/invalid_name.json"  # Should be ignored
        ]
        
        analyzer = NewWorkflowAnalyzer()
        numbers = analyzer._get_existing_numbers()
        
        expected_numbers = {1, 5, 10}
        assert numbers == expected_numbers

    def test_get_next_available_number_empty(self):
        """Test next number calculation with no existing workflows.""" 
        analyzer = NewWorkflowAnalyzer()
        analyzer.existing_numbers = set()
        
        next_num = analyzer._get_next_available_number()
        assert next_num == 1

    def test_get_next_available_number_with_existing(self):
        """Test next number calculation with existing workflows."""
        analyzer = NewWorkflowAnalyzer()
        analyzer.existing_numbers = {1, 2, 5, 10}
        
        next_num = analyzer._get_next_available_number()
        assert next_num == 11  # Max + 1

    def test_service_name_mapping(self):
        """Test that service names are properly mapped to clean versions."""
        analyzer = NewWorkflowAnalyzer()
        
        test_nodes = [
            {"type": "n8n-nodes-base.gmail"},
            {"type": "n8n-nodes-base.googleSheets"},
            {"type": "n8n-nodes-base.microsoftTeams"},
            {"type": "n8n-nodes-base.httpRequest"}
        ]
        
        services, _ = analyzer._analyze_nodes(test_nodes)
        
        assert "Gmail" in services
        assert "GoogleSheets" in services  
        assert "Teams" in services
        assert "HTTP" in services

    def test_utility_nodes_filtering(self):
        """Test that utility nodes are filtered out from services."""
        analyzer = NewWorkflowAnalyzer()
        
        test_nodes = [
            {"type": "n8n-nodes-base.set"},
            {"type": "n8n-nodes-base.function"},
            {"type": "n8n-nodes-base.if"},
            {"type": "n8n-nodes-base.gmail"}  # Real service
        ]
        
        services, _ = analyzer._analyze_nodes(test_nodes)
        
        # Utility nodes should be filtered out
        assert "Set" not in services
        assert "Function" not in services
        assert "If" not in services
        
        # Real service should be included
        assert "Gmail" in services

    def test_end_to_end_analysis(self, complex_workflow):
        """Test complete end-to-end workflow analysis."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(complex_workflow, f)
            temp_path = f.name
        
        try:
            analyzer = NewWorkflowAnalyzer()
            result = analyzer.analyze_workflow_file(temp_path)
            
            # Verify all required fields are present
            required_fields = [
                "success", "original_filename", "suggested_filename",
                "workflow_name", "services", "purpose", "trigger_type",
                "node_count", "next_number", "analysis"
            ]
            
            for field in required_fields:
                assert field in result
                
            # Verify data types
            assert isinstance(result["success"], bool)
            assert isinstance(result["services"], list)
            assert isinstance(result["node_count"], int)
            assert isinstance(result["analysis"], dict)
            
            # Verify analysis makes sense
            assert result["success"] is True
            assert result["node_count"] == 5  # Complex workflow has 5 nodes
            assert "GitHub" in result["services"]
            assert "Discord" in result["services"]
            assert result["trigger_type"] == "Webhook"
            
        finally:
            os.unlink(temp_path)