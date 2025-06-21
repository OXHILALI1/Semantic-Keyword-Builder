#!/usr/bin/env python3
"""
New Workflow Analyzer for N8N Repository
Analyzes new workflow files and suggests proper standardized filenames.
"""

import json
import os
import glob
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path

class NewWorkflowAnalyzer:
    """Analyzes new workflow files and suggests proper naming convention."""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = workflows_dir
        self.existing_numbers = self._get_existing_numbers()
        self.next_number = self._get_next_available_number()
        
    def _get_existing_numbers(self) -> Set[int]:
        """Get all existing workflow numbers from current files."""
        numbers = set()
        if not os.path.exists(self.workflows_dir):
            return numbers
            
        json_files = glob.glob(os.path.join(self.workflows_dir, "*.json"))
        
        for file_path in json_files:
            filename = os.path.basename(file_path)
            # Extract number from filename pattern: 0001_...
            match = re.match(r'(\d{4})_', filename)
            if match:
                numbers.add(int(match.group(1)))
        
        return numbers
    
    def _get_next_available_number(self) -> int:
        """Get the next available sequential number."""
        if not self.existing_numbers:
            return 1
        return max(self.existing_numbers) + 1
    
    def analyze_workflow_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a workflow file and suggest proper naming."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return {
                'error': f"Failed to read workflow file: {str(e)}",
                'success': False
            }
        
        original_filename = os.path.basename(file_path)
        
        # Extract workflow metadata
        workflow_name = data.get('name', original_filename.replace('.json', ''))
        nodes = data.get('nodes', [])
        
        # Analyze nodes for services and trigger type
        services, trigger_type = self._analyze_nodes(nodes)
        
        # Determine purpose from name and nodes
        purpose = self._determine_purpose(workflow_name, nodes)
        
        # Generate suggested filename
        suggested_filename = self._generate_filename(services, purpose, trigger_type)
        
        return {
            'success': True,
            'original_filename': original_filename,
            'suggested_filename': suggested_filename,
            'workflow_name': workflow_name,
            'services': list(services),
            'purpose': purpose,
            'trigger_type': trigger_type,
            'node_count': len(nodes),
            'next_number': self.next_number,
            'analysis': {
                'complexity': self._determine_complexity(len(nodes)),
                'has_credentials': self._has_credentials(nodes),
                'integrations_count': len(services)
            }
        }
    
    def _analyze_nodes(self, nodes: List[Dict]) -> Tuple[Set[str], str]:
        """Analyze nodes to determine services and trigger type."""
        services = set()
        trigger_type = 'Manual'
        
        for node in nodes:
            node_type = node.get('type', '')
            
            # Determine trigger type
            if any(x in node_type.lower() for x in ['webhook', 'http']):
                trigger_type = 'Webhook'
            elif any(x in node_type.lower() for x in ['cron', 'schedule', 'interval']):
                trigger_type = 'Scheduled'
            elif 'trigger' in node_type.lower() and trigger_type == 'Manual':
                trigger_type = 'Triggered'
            
            # Extract service names
            if node_type.startswith('n8n-nodes-base.'):
                service = node_type.replace('n8n-nodes-base.', '')
                service = service.replace('Trigger', '').replace('trigger', '')
                
                # Clean up service names with comprehensive mapping
                service_mapping = {
                    'webhook': 'Webhook',
                    'httpRequest': 'HTTP',
                    'cron': 'Cron',
                    'gmail': 'Gmail',
                    'slack': 'Slack',
                    'googleSheets': 'GoogleSheets',
                    'airtable': 'Airtable',
                    'notion': 'Notion',
                    'telegram': 'Telegram',
                    'discord': 'Discord',
                    'twitter': 'Twitter',
                    'github': 'GitHub',
                    'hubspot': 'HubSpot',
                    'salesforce': 'Salesforce',
                    'stripe': 'Stripe',
                    'shopify': 'Shopify',
                    'trello': 'Trello',
                    'asana': 'Asana',
                    'clickup': 'ClickUp',
                    'calendly': 'Calendly',
                    'zoom': 'Zoom',
                    'mattermost': 'Mattermost',
                    'microsoftTeams': 'Teams',
                    'googleCalendar': 'GoogleCalendar',
                    'googleDrive': 'GoogleDrive',
                    'dropbox': 'Dropbox',
                    'onedrive': 'OneDrive',
                    'aws': 'AWS',
                    'azure': 'Azure',
                    'googleCloud': 'GCP',
                    'postgresql': 'PostgreSQL',
                    'mysql': 'MySQL',
                    'mongodb': 'MongoDB',
                    'redis': 'Redis',
                    'elasticsearch': 'Elasticsearch',
                    'typeform': 'Typeform',
                    'mailchimp': 'Mailchimp',
                    'sendgrid': 'SendGrid',
                    'twilio': 'Twilio',
                    'openai': 'OpenAI',
                    'anthropic': 'Anthropic',
                    'replicate': 'Replicate'
                }
                
                clean_service = service_mapping.get(service.lower(), service.title())
                
                # Skip utility nodes
                utility_nodes = {
                    'Set', 'Function', 'If', 'Switch', 'Merge', 'StickyNote', 
                    'NoOp', 'Code', 'Execute', 'Split', 'Wait', 'Stop'
                }
                
                if clean_service not in utility_nodes:
                    services.add(clean_service)
        
        return services, trigger_type
    
    def _determine_purpose(self, name: str, nodes: List[Dict]) -> str:
        """Determine workflow purpose from name and node analysis."""
        name_lower = name.lower()
        
        # Purpose keywords mapping
        purpose_keywords = {
            'create': ['create', 'add', 'new', 'generate', 'build', 'make'],
            'update': ['update', 'modify', 'change', 'edit', 'patch', 'refresh'],
            'sync': ['sync', 'synchronize', 'mirror', 'replicate', 'match'],
            'send': ['send', 'email', 'message', 'notify', 'alert', 'push'],
            'import': ['import', 'load', 'fetch', 'get', 'retrieve', 'pull'],
            'export': ['export', 'save', 'backup', 'archive', 'download'],
            'monitor': ['monitor', 'check', 'watch', 'track', 'status', 'health'],
            'process': ['process', 'transform', 'convert', 'parse', 'analyze'],
            'automate': ['automate', 'workflow', 'bot', 'automation', 'routine'],
            'manage': ['manage', 'organize', 'admin', 'control', 'handle']
        }
        
        for purpose, keywords in purpose_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return purpose.title()
        
        # Analyze nodes for purpose hints
        node_types = [node.get('type', '').lower() for node in nodes]
        
        if any('create' in nt or 'add' in nt for nt in node_types):
            return 'Create'
        elif any('update' in nt or 'edit' in nt for nt in node_types):
            return 'Update'
        elif any('send' in nt or 'email' in nt or 'message' in nt for nt in node_types):
            return 'Send'
        
        return 'Automation'
    
    def _determine_complexity(self, node_count: int) -> str:
        """Determine workflow complexity based on node count."""
        if node_count <= 5:
            return 'Simple'
        elif node_count <= 15:
            return 'Standard'
        else:
            return 'Complex'
    
    def _has_credentials(self, nodes: List[Dict]) -> bool:
        """Check if workflow uses any credentials."""
        for node in nodes:
            if node.get('credentials'):
                return True
        return False
    
    def _generate_filename(self, services: Set[str], purpose: str, trigger_type: str) -> str:
        """Generate standardized filename."""
        # Format: 0001_Service1_Service2_Purpose_Trigger.json
        
        services_list = sorted(list(services))[:2]  # Max 2 services
        
        # Build filename components
        parts = [f"{self.next_number:04d}"]
        
        # Add services
        if services_list:
            parts.extend(services_list)
        else:
            parts.append('Manual')  # Default if no services detected
        
        # Add purpose
        parts.append(purpose)
        
        # Add trigger if not Manual
        if trigger_type not in ['Manual', 'Triggered']:
            parts.append(trigger_type)
        
        # Join and clean filename
        filename = '_'.join(parts)
        filename = re.sub(r'[^\w\-_]', '', filename)  # Remove special chars
        filename = re.sub(r'_+', '_', filename)  # Collapse multiple underscores
        filename = filename.strip('_')  # Remove leading/trailing underscores
        
        return f"{filename}.json"
    
    def analyze_and_suggest(self, file_path: str, verbose: bool = True) -> Dict[str, Any]:
        """Analyze workflow and provide detailed suggestions."""
        result = self.analyze_workflow_file(file_path)
        
        if not result['success']:
            return result
        
        if verbose:
            self._print_analysis(result)
        
        return result
    
    def _print_analysis(self, result: Dict[str, Any]):
        """Print detailed analysis results."""
        print("=" * 80)
        print("🔍 NEW WORKFLOW ANALYSIS")
        print("=" * 80)
        
        print(f"📄 Original File: {result['original_filename']}")
        print(f"📛 Workflow Name: {result['workflow_name']}")
        print(f"🔢 Next Number: {result['next_number']:04d}")
        
        print(f"\n📋 ANALYSIS RESULTS:")
        print(f"   🏷️  Services: {', '.join(result['services']) if result['services'] else 'None detected'}")
        print(f"   🎯 Purpose: {result['purpose']}")
        print(f"   ⚡ Trigger: {result['trigger_type']}")
        print(f"   🔧 Nodes: {result['node_count']}")
        print(f"   📊 Complexity: {result['analysis']['complexity']}")
        print(f"   🔐 Uses Credentials: {'Yes' if result['analysis']['has_credentials'] else 'No'}")
        
        print(f"\n✨ SUGGESTED FILENAME:")
        print(f"   📝 {result['suggested_filename']}")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Review the suggested filename")
        print(f"   2. Rename your file to: {result['suggested_filename']}")
        print(f"   3. Place it in the workflows/ directory")
        print(f"   4. Commit with descriptive message")
        
        print("=" * 80)


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze new N8N workflow files and suggest proper naming')
    parser.add_argument('file', help='Path to the workflow JSON file to analyze')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode - minimal output')
    parser.add_argument('--workflows-dir', default='workflows', help='Directory containing existing workflows')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ Error: File '{args.file}' not found.")
        return 1
    
    analyzer = NewWorkflowAnalyzer(args.workflows_dir)
    result = analyzer.analyze_and_suggest(args.file, verbose=not args.quiet)
    
    if not result['success']:
        print(f"❌ Error: {result['error']}")
        return 1
    
    if args.quiet:
        print(result['suggested_filename'])
    
    return 0


if __name__ == "__main__":
    exit(main())