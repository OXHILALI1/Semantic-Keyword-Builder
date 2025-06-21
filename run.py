#!/usr/bin/env python3
"""
🚀 Simple Launcher for n8n-workflows Search Engine
Start the system with advanced search capabilities.
"""

import sys
import os
from pathlib import Path

def print_banner():
    print("🚀 n8n-workflows Advanced Search Engine")
    print("=" * 50)

def check_requirements():
    """Check if requirements are installed."""
    try:
        import sqlite3
        import uvicorn
        import fastapi
        print("✅ Dependencies verified")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install -r requirements.txt")
        return False

def setup_database():
    """Setup database if needed."""
    from workflow_db import WorkflowDatabase
    
    db_path = "database/workflows.db"
    os.makedirs("database", exist_ok=True)
    
    print(f"🔄 Setting up database: {db_path}")
    db = WorkflowDatabase(db_path)
    
    # Check if database has data
    stats = db.get_stats()
    if stats['total'] == 0:
        print("📚 Indexing workflows...")
        index_stats = db.index_all_workflows(force_reindex=True)
        print(f"✅ Indexed {index_stats['processed']} workflows")
    else:
        print(f"✅ Database ready: {stats['total']} workflows")
    
    return db_path

def start_server(port=8000):
    """Start the API server."""
    print(f"🌐 Starting server at http://localhost:{port}")
    print(f"📊 API: http://localhost:{port}/api/workflows")
    print(f"🗂️ Categories: http://localhost:{port}/api/categories")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Configure database path
    os.environ['WORKFLOW_DB_PATH'] = "database/workflows.db"
    
    # Start uvicorn without reload to avoid StatReload issues
    import uvicorn
    uvicorn.run("api_server:app", host="127.0.0.1", port=port, reload=False)

def main():
    print_banner()
    
    # Check dependencies
    if not check_requirements():
        sys.exit(1)
    
    # Setup database
    try:
        setup_database()
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        sys.exit(1)
    
    # Start server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 