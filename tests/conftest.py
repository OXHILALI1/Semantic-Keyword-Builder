"""
Pytest configuration and shared fixtures for n8n workflow testing.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from typing import Dict, Any

# Test data fixtures
@pytest.fixture
def simple_workflow() -> Dict[str, Any]:
    """Simple workflow with basic Slack integration."""
    return {
        "id": "test-simple-001",
        "name": "Simple Slack Notification",
        "nodes": [
            {
                "id": "manual-trigger",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "position": [100, 100],
                "parameters": {},
                "typeVersion": 1
            },
            {
                "id": "slack-node",
                "name": "Send Slack Message",
                "type": "n8n-nodes-base.slack",
                "position": [300, 100],
                "parameters": {
                    "channel": "#general",
                    "text": "Test message"
                },
                "typeVersion": 1
            }
        ],
        "connections": {
            "Manual Trigger": {
                "main": [
                    [
                        {
                            "node": "Send Slack Message",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {},
        "createdAt": "2025-06-21T06:00:00.000Z",
        "updatedAt": "2025-06-21T06:00:00.000Z",
        "tags": []
    }

@pytest.fixture
def complex_workflow() -> Dict[str, Any]:
    """Complex workflow with multiple services and triggers."""
    return {
        "id": "test-complex-001", 
        "name": "GitHub Issues to Discord and Email Notification System",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "GitHub Webhook",
                "type": "n8n-nodes-base.webhook",
                "position": [100, 100],
                "parameters": {
                    "path": "github-issues",
                    "httpMethod": "POST"
                },
                "typeVersion": 1,
                "webhookId": "test-webhook-id"
            },
            {
                "id": "github-node",
                "name": "Get Issue Details",
                "type": "n8n-nodes-base.github",
                "position": [300, 100],
                "parameters": {
                    "operation": "getIssue",
                    "owner": "test-owner",
                    "repository": "test-repo"
                },
                "typeVersion": 1
            },
            {
                "id": "discord-node",
                "name": "Send Discord Alert",
                "type": "n8n-nodes-base.discord",
                "position": [500, 50],
                "parameters": {
                    "operation": "sendMessage",
                    "channelId": "123456789",
                    "content": "New GitHub issue: {{$json.title}}"
                },
                "typeVersion": 1
            },
            {
                "id": "gmail-node",
                "name": "Send Email Summary",
                "type": "n8n-nodes-base.gmail",
                "position": [500, 150],
                "parameters": {
                    "operation": "send",
                    "sendTo": "team@example.com",
                    "subject": "GitHub Issue Alert",
                    "emailType": "html"
                },
                "typeVersion": 1
            },
            {
                "id": "function-node",
                "name": "Process Issue Data",
                "type": "n8n-nodes-base.function",
                "position": [700, 100],
                "parameters": {
                    "functionCode": "return [{processed: true, timestamp: Date.now()}];"
                },
                "typeVersion": 1
            }
        ],
        "connections": {
            "GitHub Webhook": {
                "main": [
                    [
                        {
                            "node": "Get Issue Details",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Issue Details": {
                "main": [
                    [
                        {
                            "node": "Send Discord Alert",
                            "type": "main",
                            "index": 0
                        },
                        {
                            "node": "Send Email Summary",
                            "type": "main", 
                            "index": 0
                        }
                    ]
                ]
            },
            "Send Discord Alert": {
                "main": [
                    [
                        {
                            "node": "Process Issue Data",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {},
        "createdAt": "2025-06-21T06:00:00.000Z",
        "updatedAt": "2025-06-21T06:00:00.000Z",
        "tags": ["github", "notifications", "automation"]
    }

@pytest.fixture
def scheduled_workflow() -> Dict[str, Any]:
    """Workflow with scheduled trigger."""
    return {
        "id": "test-scheduled-001",
        "name": "Daily Newsletter Email Automation",
        "nodes": [
            {
                "id": "cron-trigger",
                "name": "Daily Schedule",
                "type": "n8n-nodes-base.cron",
                "position": [100, 100],
                "parameters": {
                    "rule": {
                        "interval": [
                            {
                                "field": "cronExpression",
                                "expression": "0 9 * * *"
                            }
                        ]
                    }
                },
                "typeVersion": 1
            },
            {
                "id": "airtable-node",
                "name": "Get Newsletter Content",
                "type": "n8n-nodes-base.airtable",
                "position": [300, 100],
                "parameters": {
                    "operation": "list",
                    "application": "newsletter-content",
                    "table": "articles"
                },
                "typeVersion": 1
            },
            {
                "id": "gmail-node",
                "name": "Send Newsletter",
                "type": "n8n-nodes-base.gmail",
                "position": [500, 100],
                "parameters": {
                    "operation": "send",
                    "sendTo": "subscribers@example.com",
                    "subject": "Daily Newsletter",
                    "emailType": "html"
                },
                "typeVersion": 1
            }
        ],
        "connections": {
            "Daily Schedule": {
                "main": [
                    [
                        {
                            "node": "Get Newsletter Content",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Newsletter Content": {
                "main": [
                    [
                        {
                            "node": "Send Newsletter",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {},
        "createdAt": "2025-06-21T06:00:00.000Z",
        "updatedAt": "2025-06-21T06:00:00.000Z",
        "tags": ["newsletter", "automation", "scheduled"]
    }

@pytest.fixture
def invalid_workflow() -> Dict[str, Any]:
    """Invalid workflow for testing error handling."""
    return {
        "id": "test-invalid-001",
        "name": "Invalid Workflow Structure",
        # Missing required fields like nodes, connections
        "active": True
    }

@pytest.fixture
def malformed_json() -> str:
    """Malformed JSON for testing JSON parsing errors."""
    return '{"id": "test", "name": "broken", "nodes": [{'

@pytest.fixture
def temp_workflow_file(simple_workflow):
    """Create a temporary workflow file and clean up after test."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(simple_workflow, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass

@pytest.fixture
def temp_workflows_dir():
    """Create a temporary workflows directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix='test_workflows_')
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_existing_workflows(temp_workflows_dir):
    """Create a set of existing workflows for testing sequence numbering."""
    existing_workflows = [
        ("0001_Slack_Manual_Automate.json", {"id": "existing-1", "name": "Test 1", "nodes": [], "connections": {}}),
        ("0002_Gmail_Webhook_Send.json", {"id": "existing-2", "name": "Test 2", "nodes": [], "connections": {}}),
        ("0005_Discord_Scheduled_Notify.json", {"id": "existing-5", "name": "Test 5", "nodes": [], "connections": {}})
    ]
    
    for filename, workflow_data in existing_workflows:
        filepath = os.path.join(temp_workflows_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(workflow_data, f)
    
    return temp_workflows_dir

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "analyzer: mark test as analyzer-specific"
    )
    config.addinivalue_line(
        "markers", "adder: mark test as adder-specific" 
    )
    config.addinivalue_line(
        "markers", "api: mark test as API-specific"
    )

def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark tests based on file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Mark tests based on filename
        if "analyzer" in str(item.fspath):
            item.add_marker(pytest.mark.analyzer)
        elif "adder" in str(item.fspath):
            item.add_marker(pytest.mark.adder)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)