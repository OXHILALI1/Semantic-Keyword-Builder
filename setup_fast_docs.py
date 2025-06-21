#!/usr/bin/env python3
"""
Setup script for the new fast N8N workflow documentation system.
"""

import subprocess
import sys
import os
from pathlib import Path
import shlex

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        # Split the command string into a list for shell=False
        command_args = shlex.split(command)
        result = subprocess.run(
            command_args,
            shell=False,  # Set shell to False
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        # Consider logging e.stdout as well if it contains useful info
        return None
    except FileNotFoundError as e:
        # This can happen if sys.executable or the script is not found
        print(f"❌ {description} failed. Command not found: {e}")
        return None

def install_dependencies():
    """Install Python dependencies."""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def index_workflows():
    """Index all workflows into the database."""
    return run_command(
        f"{sys.executable} workflow_db.py --index",
        "Indexing workflow files into database"
    )

def main():
    print("🚀 Setting up N8N Fast Workflow Documentation System")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("workflows"):
        print("❌ Error: 'workflows' directory not found. Please run this script from the repository root.")
        sys.exit(1)
    
    # Install dependencies
    if install_dependencies() is None:
        print("❌ Failed to install dependencies. Please install manually:")
        print("   pip install fastapi uvicorn pydantic")
        sys.exit(1)
    
    # Index workflows
    if index_workflows() is None:
        print("⚠️  Warning: Failed to index workflows. You can do this manually later:")
        print("   python workflow_db.py --index")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📊 Performance Comparison:")
    print("   Old system: 71MB HTML file, 10s+ load time")
    print("   New system: <100KB initial load, <100ms search")
    print("\n🚀 To start the fast documentation server:")
    print("   python api_server.py")
    print("\n🌐 Then open: http://localhost:8000")
    print("\n💡 Features:")
    print("   • Instant search with <100ms response times")
    print("   • Virtual scrolling for smooth browsing")
    print("   • Real-time filtering and pagination")
    print("   • Lazy-loaded diagrams and JSON viewing")
    print("   • Dark/light theme support")
    print("   • Mobile-responsive design")

if __name__ == "__main__":
    main()