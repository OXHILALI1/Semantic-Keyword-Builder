#!/usr/bin/env python3
"""
Auto-Add Workflow Script for N8N Repository
Automatically analyzes, renames, and adds new workflow files to the repository.
"""

import json
import os
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from new_workflow_analyzer import NewWorkflowAnalyzer

class AutoWorkflowAdder:
    """Automatically adds new workflows to the repository with proper naming."""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = workflows_dir
        self.analyzer = NewWorkflowAnalyzer(workflows_dir)
        
        # Ensure workflows directory exists
        os.makedirs(workflows_dir, exist_ok=True)

    @classmethod
    def _validate_workflow_file(cls, file_path: str) -> Optional[Dict[str, Any]]:
        """Validate a single workflow JSON file."""
        if not os.path.exists(file_path):
            return {'success': False, 'error': f"File '{file_path}' not found."}

        if not file_path.endswith('.json'):
            return {'success': False, 'error': f"File '{file_path}' is not a JSON file."}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'nodes' not in data or 'connections' not in data:
                return {'success': False, 'error': f"File '{file_path}' is not a valid workflow file (missing 'nodes' or 'connections')."}
        except FileNotFoundError: # Should be caught by os.path.exists, but good for robustness
             return {'success': False, 'error': f"File '{file_path}' not found during read attempt."}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return {'success': False, 'error': f"Error decoding JSON from '{file_path}': {str(e)}"}
        except Exception as e:
            return {'success': False, 'error': f"Error reading file '{file_path}': {str(e)}"}

        return None # All checks passed
    
    def add_workflow(self, source_file: str, auto_confirm: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Add a new workflow to the repository with proper naming."""
        validation_result = self._validate_workflow_file(source_file)
        if validation_result:
            return validation_result
        
        # Analyze the workflow
        analysis = self.analyzer.analyze_workflow_file(source_file)
        
        if not analysis['success']:
            return analysis
        
        suggested_filename = analysis['suggested_filename']
        target_path = os.path.join(self.workflows_dir, suggested_filename)
        
        # Check if target already exists
        if os.path.exists(target_path):
            return {
                'success': False,
                'error': f"Target file '{suggested_filename}' already exists in repository."
            }
        
        # Show analysis and get confirmation
        if not auto_confirm and not dry_run:
            self._print_add_preview(source_file, analysis)
            
            confirm = input("\n✅ Proceed with adding this workflow? (yes/no): ").lower().strip()
            if confirm not in ['yes', 'y']:
                return {
                    'success': False,
                    'error': "Operation cancelled by user."
                }
        
        if dry_run:
            print(f"🔍 DRY RUN: Would copy '{source_file}' to '{target_path}'")
            return {
                'success': True,
                'action': 'dry_run',
                'source_file': source_file,
                'target_file': suggested_filename,
                'target_path': target_path,
                'analysis': analysis
            }
        
        # Copy file with new name
        try:
            shutil.copy2(source_file, target_path)
            
            # Update analyzer's next number for subsequent operations
            self.analyzer.existing_numbers.add(analysis['next_number'])
            self.analyzer.next_number = self.analyzer._get_next_available_number()
            
            print(f"✅ Successfully added workflow:")
            print(f"   📄 Source: {os.path.basename(source_file)}")
            print(f"   📝 Added as: {suggested_filename}")
            print(f"   📂 Location: {target_path}")
            
            return {
                'success': True,
                'action': 'added',
                'source_file': source_file,
                'target_file': suggested_filename,
                'target_path': target_path,
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to copy file: {str(e)}"
            }
    
    def add_multiple_workflows(self, source_files: list, auto_confirm: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Add multiple workflows to the repository."""
        results = {
            'success': True,
            'total_files': len(source_files),
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        print(f"🚀 Processing {len(source_files)} workflow files...")
        
        for i, source_file in enumerate(source_files, 1):
            print(f"\n📄 Processing file {i}/{len(source_files)}: {os.path.basename(source_file)}")
            
            result = self.add_workflow(source_file, auto_confirm, dry_run)
            results['results'].append(result)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
                print(f"❌ Error: {result['error']}")
        
        # Summary
        print(f"\n📊 BATCH PROCESSING SUMMARY:")
        print(f"   ✅ Successful: {results['successful']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📈 Total: {results['total_files']}")
        
        if results['failed'] > 0:
            results['success'] = False
        
        return results
    
    def _print_add_preview(self, source_file: str, analysis: Dict[str, Any]):
        """Print preview of what will be added."""
        print("=" * 80)
        print("📋 NEW WORKFLOW ADDITION PREVIEW")
        print("=" * 80)
        
        print(f"📄 Source File: {os.path.basename(source_file)}")
        print(f"📍 Full Path: {source_file}")
        print(f"📛 Workflow Name: {analysis['workflow_name']}")
        
        print(f"\n🔍 ANALYSIS:")
        print(f"   🔢 Will be numbered: {analysis['next_number']:04d}")
        print(f"   🏷️  Services: {', '.join(analysis['services']) if analysis['services'] else 'None detected'}")
        print(f"   🎯 Purpose: {analysis['purpose']}")
        print(f"   ⚡ Trigger: {analysis['trigger_type']}")
        print(f"   🔧 Nodes: {analysis['node_count']} ({analysis['analysis']['complexity']})")
        
        print(f"\n✨ NEW FILENAME:")
        print(f"   📝 {analysis['suggested_filename']}")
        
        print(f"\n📂 WILL BE SAVED TO:")
        print(f"   📍 {os.path.join(self.workflows_dir, analysis['suggested_filename'])}")
        
        print("=" * 80)
    
    def list_pending_workflows(self, directory: str = ".") -> list:
        """List potential workflow files in a directory that aren't in the repository yet."""
        pending = []
        
        if not os.path.exists(directory):
            return pending
        
        # Find all JSON files in the directory
        for file_path_obj in Path(directory).glob("*.json"):
            file_path = str(file_path_obj)
            filename = file_path_obj.name
            
            # Skip files that look like they're already properly named
            if not filename.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                validation_result = self._validate_workflow_file(file_path)
                if validation_result is None: # File is valid
                    pending.append(file_path)
                # else: # Optionally log validation_result['error'] if needed
                #     print(f"Skipping invalid file {filename}: {validation_result['error']}")
        
        return pending

def _validate_multiple_workflow_files_for_cli(file_paths: List[str], adder_class: type) -> bool:
    """Validate multiple workflow files and print errors if any."""
    all_valid = True
    error_messages = []
    for fp in file_paths:
        validation_result = adder_class._validate_workflow_file(fp)
        if validation_result:
            all_valid = False
            error_messages.append(validation_result['error'])

    if not all_valid:
        print("❌ Error: The following file issues were found:")
        for error in error_messages:
            print(f"   - {error}")
    return all_valid

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Automatically add new N8N workflows to repository')
    parser.add_argument('files', nargs='*', help='Workflow JSON files to add')
    parser.add_argument('--workflows-dir', default='workflows', help='Directory containing workflows')
    parser.add_argument('--auto-confirm', '-y', action='store_true', help='Auto-confirm all operations')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--scan', '-s', metavar='DIR', help='Scan directory for workflow files to add')
    parser.add_argument('--list-pending', '-l', metavar='DIR', 
                       help='List potential workflow files that could be added')
    
    args = parser.parse_args()
    
    adder = AutoWorkflowAdder(args.workflows_dir)
    
    # List pending workflows
    if args.list_pending:
        pending = adder.list_pending_workflows(args.list_pending)
        if pending:
            print(f"🔍 Found {len(pending)} potential workflow files to add:")
            for i, file_path in enumerate(pending, 1):
                print(f"   {i}. {os.path.basename(file_path)}")
            print(f"\nTo add these files, use:")
            quoted_files = [f'"{f}"' for f in pending]
            print(f"   python auto_add_workflow.py {' '.join(quoted_files)}")
        else:
            print("🔍 No potential workflow files found.")
        return 0
    
    # Scan directory for workflows
    if args.scan:
        pending = adder.list_pending_workflows(args.scan)
        if pending:
            print(f"🔍 Found {len(pending)} workflow files in '{args.scan}' to add.")
            
            if not args.auto_confirm:
                confirm = input("Add all found workflows? (yes/no): ").lower().strip()
                if confirm not in ['yes', 'y']:
                    print("❌ Operation cancelled.")
                    return 1
            
            result = adder.add_multiple_workflows(pending, args.auto_confirm, args.dry_run)
            return 0 if result['success'] else 1
        else:
            print(f"🔍 No workflow files found in '{args.scan}'.")
            return 0
    
    # Process specified files
    if not args.files:
        parser.print_help()
        return 1
    
    if not _validate_multiple_workflow_files_for_cli(args.files, AutoWorkflowAdder):
        return 1
    
    # Process files
    if len(args.files) == 1:
        result = adder.add_workflow(args.files[0], args.auto_confirm, args.dry_run)
        if not result['success']:
            print(f"❌ Error: {result['error']}")
            return 1
    else:
        result = adder.add_multiple_workflows(args.files, args.auto_confirm, args.dry_run)
        if not result['success']:
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())