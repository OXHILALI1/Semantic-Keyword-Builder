#!/usr/bin/env python3
"""
FastAPI Server for N8N Workflow Documentation
High-performance API with sub-100ms response times.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
import json
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
import uvicorn
import threading
import logging

from workflow_db import WorkflowDatabase
from new_workflow_analyzer import NewWorkflowAnalyzer
from auto_add_workflow import AutoWorkflowAdder

# Initialize FastAPI app
app = FastAPI(
    title="N8N Workflow Documentation API",
    description="Fast API for browsing and searching workflow documentation",
    version="2.0.0"
)

# Add middleware for performance
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # FastAPI server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:8000"   # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Only required methods
    allow_headers=["Content-Type", "Authorization"],  # Only required headers
)

# Initialize database
db = WorkflowDatabase()

WORKFLOWS_DIR = "workflows" # Define base directory for workflows

# Lock and flag for reindexing
reindex_lock = threading.Lock()
is_reindexing_flag = False

# File Upload Security Constants
MAX_UPLOAD_SIZE_MB = 5  # Max upload size in Megabytes
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Response models
class WorkflowSummary(BaseModel):
    id: Optional[int] = None
    filename: str
    name: str
    active: bool
    description: str = ""
    trigger_type: str = "Manual"
    complexity: str = "low"
    node_count: int = 0
    integrations: List[str] = []
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        # Allow conversion of int to bool for active field
        validate_assignment = True
        
    @validator('active', pre=True)
    def convert_active(cls, v):
        if isinstance(v, int):
            return bool(v)
        return v
    

class SearchResponse(BaseModel):
    workflows: List[WorkflowSummary]
    total: int
    page: int
    per_page: int
    pages: int
    query: str
    filters: Dict[str, Any]

class StatsResponse(BaseModel):
    total: int
    active: int
    inactive: int
    triggers: Dict[str, int]
    complexity: Dict[str, int]
    total_nodes: int
    unique_integrations: int
    last_indexed: str

class WorkflowAnalysisResponse(BaseModel):
    success: bool
    original_filename: str
    suggested_filename: str
    workflow_name: str
    services: List[str]
    purpose: str
    trigger_type: str
    node_count: int
    next_number: int
    analysis: Dict[str, Any]
    error: Optional[str] = None

class WorkflowAddResponse(BaseModel):
    success: bool
    action: str
    source_filename: str
    target_filename: Optional[str] = None
    target_path: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Serve the React application."""
    react_build_dir = Path("frontend/dist")
    index_file = react_build_dir / "index.html"
    
    # FORCE React app - no fallback to static files
    if not index_file.exists():
        return HTMLResponse("""
        <html><body>
        <h1>React Build Missing</h1>
        <p>React build not found at: """ + str(index_file.absolute()) + """</p>
        <p>Run 'npm run build' in the frontend directory</p>
        </body></html>
        """)
    
    # Force no-cache headers to prevent browser caching issues
    return FileResponse(
        str(index_file),
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "N8N Workflow API is running"}

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get workflow database statistics."""
    try:
        stats = db.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@app.get("/api/workflows", response_model=SearchResponse)
async def search_workflows(
    q: str = Query("", description="Search query"),
    trigger: str = Query("all", description="Filter by trigger type"),
    complexity: str = Query("all", description="Filter by complexity"),
    active_only: bool = Query(False, description="Show only active workflows"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Search and filter workflows with pagination."""
    try:
        offset = (page - 1) * per_page
        
        workflows, total = db.search_workflows(
            query=q,
            trigger_filter=trigger,
            complexity_filter=complexity,
            active_only=active_only,
            limit=per_page,
            offset=offset
        )
        
        # Convert to Pydantic models with error handling
        workflow_summaries = []
        for workflow in workflows:
            try:
                # Remove extra fields that aren't in the model
                clean_workflow = {
                    'id': workflow.get('id'),
                    'filename': workflow.get('filename', ''),
                    'name': workflow.get('name', ''),
                    'active': workflow.get('active', False),
                    'description': workflow.get('description', ''),
                    'trigger_type': workflow.get('trigger_type', 'Manual'),
                    'complexity': workflow.get('complexity', 'low'),
                    'node_count': workflow.get('node_count', 0),
                    'integrations': workflow.get('integrations', []),
                    'tags': workflow.get('tags', []),
                    'created_at': workflow.get('created_at'),
                    'updated_at': workflow.get('updated_at')
                }
                workflow_summaries.append(WorkflowSummary(**clean_workflow))
            except Exception as e:
                print(f"Error converting workflow {workflow.get('filename', 'unknown')}: {e}")
                # Continue with other workflows instead of failing completely
                continue
        
        pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return SearchResponse(
            workflows=workflow_summaries,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            query=q,
            filters={
                "trigger": trigger,
                "complexity": complexity,
                "active_only": active_only
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching workflows: {str(e)}")

@app.get("/api/workflows/{filename}")
async def get_workflow_detail(filename: str):
    """Get detailed workflow information including raw JSON."""
    try:
        # Validate filename and path
        resolved_workflows_dir = Path(WORKFLOWS_DIR).resolve()
        if os.path.basename(filename) != filename:
            raise HTTPException(status_code=400, detail="Invalid filename format.")

        requested_path = (resolved_workflows_dir / filename).resolve()

        if not str(requested_path).startswith(str(resolved_workflows_dir) + os.sep):
            raise HTTPException(status_code=400, detail="Invalid path specified.")

        file_path_str = str(requested_path)

        # Get workflow metadata from database (uses original filename)
        workflows, _ = db.search_workflows(f'filename:"{filename}"', limit=1)
        if not workflows:
            # This implies the DB entry exists, but the file might not, or filename is wrong.
            # If filename caused path traversal, previous checks would catch it.
            # If DB has entry but file missing (validated path), it's a server issue or data inconsistency.
            raise HTTPException(status_code=404, detail="Workflow metadata not found in database.")
        
        workflow_meta = workflows[0]
        
        # Load raw JSON from file (uses validated file_path_str)
        if not os.path.exists(file_path_str):
            logging.error(f"Workflow file not found at validated path: {file_path_str} but DB entry exists for {filename}")
            raise HTTPException(status_code=404, detail="Workflow file not found on server.")
        
        with open(file_path_str, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
        
        return {
            "metadata": workflow_meta,
            "raw_json": raw_json
        }
    except HTTPException:
        raise
    except Exception as e:
        # Logged by global handler
        raise HTTPException(status_code=500, detail=f"Error loading workflow: {str(e)}")

@app.get("/api/workflows/{filename}/download")
async def download_workflow(filename: str):
    """Download workflow JSON file."""
    resolved_workflows_dir = Path(WORKFLOWS_DIR).resolve()
    if os.path.basename(filename) != filename:
        raise HTTPException(status_code=400, detail="Invalid filename format.")

    requested_path = (resolved_workflows_dir / filename).resolve()

    if not str(requested_path).startswith(str(resolved_workflows_dir) + os.sep):
        raise HTTPException(status_code=400, detail="Invalid path specified.")

    file_path_str = str(requested_path)

    if not os.path.exists(file_path_str):
        # Consider if this should be a 404 even if db might have an entry.
        # For download, file must exist.
        raise HTTPException(status_code=404, detail="Workflow file not found for download.")
    
    return FileResponse(
        file_path_str,
        media_type="application/json",
        filename=filename # Keep original filename for download name suggestion
    )

@app.get("/api/workflows/{filename}/diagram")
async def get_workflow_diagram(filename: str):
    """Get Mermaid diagram code for workflow visualization."""
    try:
        resolved_workflows_dir = Path(WORKFLOWS_DIR).resolve()
        if os.path.basename(filename) != filename:
            raise HTTPException(status_code=400, detail="Invalid filename format.")

        requested_path = (resolved_workflows_dir / filename).resolve()

        if not str(requested_path).startswith(str(resolved_workflows_dir) + os.sep):
            raise HTTPException(status_code=400, detail="Invalid path specified.")

        file_path_str = str(requested_path)

        if not os.path.exists(file_path_str):
            raise HTTPException(status_code=404, detail="Workflow file not found for diagram generation.")
        
        with open(file_path_str, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        connections = data.get('connections', {})
        
        # Generate Mermaid diagram
        diagram = generate_mermaid_diagram(nodes, connections)
        
        return {"diagram": diagram}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating diagram: {str(e)}")

def generate_mermaid_diagram(nodes: List[Dict], connections: Dict) -> str:
    """Generate Mermaid.js flowchart code from workflow nodes and connections."""
    if not nodes:
        return "graph TD\n  EmptyWorkflow[No nodes found in workflow]"
    
    # Create mapping for node names to ensure valid mermaid IDs
    mermaid_ids = {}
    for i, node in enumerate(nodes):
        node_id = f"node{i}"
        node_name = node.get('name', f'Node {i}')
        mermaid_ids[node_name] = node_id
    
    # Start building the mermaid diagram
    mermaid_code = ["graph TD"]
    
    # Add nodes with styling
    for node in nodes:
        node_name = node.get('name', 'Unnamed')
        node_id = mermaid_ids[node_name]
        node_type = node.get('type', '').replace('n8n-nodes-base.', '')
        
        # Determine node style based on type
        style = ""
        if any(x in node_type.lower() for x in ['trigger', 'webhook', 'cron']):
            style = "fill:#b3e0ff,stroke:#0066cc"  # Blue for triggers
        elif any(x in node_type.lower() for x in ['if', 'switch']):
            style = "fill:#ffffb3,stroke:#e6e600"  # Yellow for conditional nodes
        elif any(x in node_type.lower() for x in ['function', 'code']):
            style = "fill:#d9b3ff,stroke:#6600cc"  # Purple for code nodes
        elif 'error' in node_type.lower():
            style = "fill:#ffb3b3,stroke:#cc0000"  # Red for error handlers
        else:
            style = "fill:#d9d9d9,stroke:#666666"  # Gray for other nodes
        
        # Add node with label (escaping special characters)
        clean_name = node_name.replace('"', "'")
        clean_type = node_type.replace('"', "'")
        label = f"{clean_name}<br>({clean_type})"
        mermaid_code.append(f"  {node_id}[\"{label}\"]")
        mermaid_code.append(f"  style {node_id} {style}")
    
    # Add connections between nodes
    for source_name, source_connections in connections.items():
        if source_name not in mermaid_ids:
            continue
        
        if isinstance(source_connections, dict) and 'main' in source_connections:
            main_connections = source_connections['main']
            
            for i, output_connections in enumerate(main_connections):
                if not isinstance(output_connections, list):
                    continue
                    
                for connection in output_connections:
                    if not isinstance(connection, dict) or 'node' not in connection:
                        continue
                        
                    target_name = connection['node']
                    if target_name not in mermaid_ids:
                        continue
                        
                    # Add arrow with output index if multiple outputs
                    label = f" -->|{i}| " if len(main_connections) > 1 else " --> "
                    mermaid_code.append(f"  {mermaid_ids[source_name]}{label}{mermaid_ids[target_name]}")
    
    # Format the final mermaid diagram code
    return "\n".join(mermaid_code)

@app.post("/api/reindex")
async def reindex_workflows(background_tasks: BackgroundTasks, force: bool = False):
    """Trigger workflow reindexing in the background."""
    global is_reindexing_flag
    
    if is_reindexing_flag: # Quick check without lock
        return JSONResponse(
            status_code=409,
            content={"message": "Reindexing already in progress."}
        )

    with reindex_lock:
        if is_reindexing_flag: # Double check after acquiring lock
            return JSONResponse(
                status_code=409,
                content={"message": "Reindexing already in progress."}
            )
        is_reindexing_flag = True

    def run_indexing_task():
        global is_reindexing_flag
        try:
            db.index_all_workflows(force_reindex=force)
        except Exception as e:
            print(f"Error during background reindexing: {e}") # Log error
        finally:
            with reindex_lock: # Ensure status flag update is atomic
                is_reindexing_flag = False

    background_tasks.add_task(run_indexing_task)
    return {"message": "Reindexing started in background."}

@app.get("/api/integrations")
async def get_integrations():
    """Get list of all unique integrations."""
    try:
        stats = db.get_stats()
        # For now, return basic info. Could be enhanced to return detailed integration stats
        return {"integrations": [], "count": stats['unique_integrations']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching integrations: {str(e)}")

async def _validate_uploaded_file_content(content_bytes: bytes, filename: str) -> Tuple[Optional[Dict[str, Any]], Optional[HTTPException]]:
    """Validate uploaded file content for size, encoding, and basic JSON structure."""
    # Size validation is already done before calling this, but good to have a logical place
    if len(content_bytes) > MAX_UPLOAD_SIZE_BYTES: # This check is somewhat redundant if called after pre-check
        return None, HTTPException(status_code=413, detail=f"File size exceeds limit of {MAX_UPLOAD_SIZE_MB}MB.")

    # JSON decoding and structure validation
    try:
        json_string = content_bytes.decode('utf-8')
        data = json.loads(json_string)
    except UnicodeDecodeError:
        return None, HTTPException(status_code=400, detail="Invalid file encoding. UTF-8 expected.")
    except json.JSONDecodeError:
        return None, HTTPException(status_code=400, detail="Invalid JSON format.")

    if not isinstance(data, dict) or 'nodes' not in data or 'connections' not in data:
        return None, HTTPException(status_code=400, detail="Invalid workflow structure. Missing 'nodes' or 'connections' keys.")

    return data, None # Return parsed data and no error

@app.post("/api/analyze-workflow", response_model=WorkflowAnalysisResponse)
async def analyze_workflow(file: UploadFile = File(...)):
    """Analyze uploaded workflow file and suggest proper naming."""
    if not file.filename.endswith('.json'): # Basic filename check
        raise HTTPException(status_code=400, detail="File must be a JSON file.")

    if file.content_type != "application/json":
        raise HTTPException(status_code=415, detail="Invalid content type. Only application/json is accepted.")

    await file.seek(0)
    content = await file.read()
    # Not seeking again as we use 'content' variable from now on.

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File size exceeds limit of {MAX_UPLOAD_SIZE_MB}MB.")

    parsed_data, validation_error = await _validate_uploaded_file_content(content, file.filename)
    if validation_error:
        raise validation_error
    # 'parsed_data' can be used if needed, but analyzer works with file path.
    # 'content' (bytes) is what we'll write to temp file.

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as temp_file:
            temp_file.write(content) # Write the validated byte content
            temp_file_path = temp_file.name

        if temp_file_path is None:
            logging.error("Failed to create temporary file for analysis post-validation, temp_file_path is None.")
            raise HTTPException(status_code=500, detail="Failed to create temporary file.")

        analyzer = NewWorkflowAnalyzer()
        result = analyzer.analyze_workflow_file(temp_file_path)
        
        if not result['success']:
            return WorkflowAnalysisResponse(
                success=False,
                original_filename=file.filename,
                suggested_filename="",
                workflow_name="",
                services=[],
                purpose="",
                trigger_type="",
                node_count=0,
                next_number=0,
                analysis={},
                error=result.get('error', 'Analysis failed')
            )
        
        return WorkflowAnalysisResponse(**result)

    except Exception as e:
        # The global exception handler will catch this and log str(e).
        # Specific logging for this endpoint context can be added if desired,
        # but the primary goal here is robust cleanup.
        raise HTTPException(status_code=500, detail=f"Error analyzing workflow: {str(e)}")

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logging.info(f"Successfully deleted temporary file: {temp_file_path}")
            except OSError as unlink_error:
                # Log the error during cleanup
                logging.error(f"Failed to delete temporary file {temp_file_path}: {unlink_error}", exc_info=True)

@app.post("/api/add-workflow", response_model=WorkflowAddResponse)
async def add_workflow(
    file: UploadFile = File(...),
    auto_confirm: bool = True,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Add uploaded workflow file to repository with proper naming."""
    if not file.filename.endswith('.json'): # Basic filename check
        raise HTTPException(status_code=400, detail="File must be a JSON file.")

    if file.content_type != "application/json":
        raise HTTPException(status_code=415, detail="Invalid content type. Only application/json is accepted.")

    await file.seek(0)
    content = await file.read()
    # Not seeking again as we use 'content' variable from now on.

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File size exceeds limit of {MAX_UPLOAD_SIZE_MB}MB.")

    parsed_data, validation_error = await _validate_uploaded_file_content(content, file.filename)
    if validation_error:
        raise validation_error
    # 'parsed_data' can be used if needed.
    # 'content' (bytes) is what we'll write to temp file.

    temp_file_path = None # Initialize
    try:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as temp_file:
            temp_file.write(content) # Write the validated byte content
            temp_file_path = temp_file.name

        if temp_file_path is None:
            logging.error("Failed to create temporary file for add post-validation, temp_file_path is None.")
            raise HTTPException(status_code=500, detail="Failed to create temporary file for add.")

        adder = AutoWorkflowAdder()
        result = adder.add_workflow(temp_file_path, auto_confirm=auto_confirm, dry_run=False)
        
        if result['success']:
            # Trigger database reindex in background
            def reindex_db_task(): # Renamed to avoid confusion
                global is_reindexing_flag # Ensure it's the global flag

                # Check if reindexing is already scheduled or running
                if is_reindexing_flag:
                     print("Reindex after add_workflow: Already in progress or scheduled. Skipping.")
                     return

                with reindex_lock: # Acquire lock to check and set flag
                    if is_reindexing_flag:
                        print("Reindex after add_workflow: Lock acquired, but flag was already true. Skipping.")
                        return # Another task just set it
                    is_reindexing_flag = True

                try:
                    print("Reindex after add_workflow: Starting actual indexing.")
                    db.index_all_workflows(force_reindex=False)
                except Exception as e:
                    print(f"Error reindexing after workflow addition: {e}")
                finally:
                    with reindex_lock: # Acquire lock to reset flag
                        is_reindexing_flag = False
                        print("Reindex after add_workflow: Indexing finished, flag reset.")

            background_tasks.add_task(reindex_db_task)
            
            return WorkflowAddResponse(
                success=True,
                action=result['action'],
                source_filename=file.filename,
                target_filename=result.get('target_file'),
                target_path=result.get('target_path')
            )
        else:
            return WorkflowAddResponse(
                success=False,
                action="failed",
                source_filename=file.filename,
                error=result.get('error', 'Failed to add workflow')
            )

    except Exception as e:
        # Global exception handler will log this.
        raise HTTPException(status_code=500, detail=f"Error adding workflow: {str(e)}")

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logging.info(f"Successfully deleted temporary file after add: {temp_file_path}")
            except OSError as unlink_error:
                logging.error(f"Failed to delete temporary file {temp_file_path} after add: {unlink_error}", exc_info=True)

@app.get("/api/workflow-stats")
async def get_workflow_addition_stats():
    """Get statistics for workflow addition (next number, etc.)."""
    try:
        analyzer = NewWorkflowAnalyzer()
        stats = db.get_stats()
        
        return {
            "total": stats.get('total', 0),
            "recentlyAdded": 10,  # Could be calculated from creation dates
            "lastUpdated": stats.get('last_indexed', ''),
            "next_available_number": analyzer.next_number,
            "total_existing": len(analyzer.existing_numbers),
            "last_number": max(analyzer.existing_numbers) if analyzer.existing_numbers else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching workflow stats: {str(e)}")

# Custom exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log the full exception details to the server console/logs
    logging.error(f"Unhandled exception during request to {request.url.path}: {exc}", exc_info=True)

    # Return a generic error message to the client
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred. Please try again later or contact support if the issue persists."}
    )

# Mount React build files AFTER all routes are defined
react_build_dir = Path("frontend/dist")
if react_build_dir.exists():
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    print(f"✅ React build assets mounted from {react_build_dir.absolute()}")
else:
    print(f"❌ Warning: React build directory not found at {react_build_dir.absolute()}")

# REMOVED: No static file mounting - React only!
# static_dir = Path("static")
# if static_dir.exists():
#     app.mount("/static", StaticFiles(directory="static"), name="static")
#     print(f"✅ Static files mounted from {static_dir.absolute()}")
# else:
#     print(f"❌ Warning: Static directory not found at {static_dir.absolute()}")
print("🚫 Static file mounting disabled - React app only!")

# PURGED: No more static directory creation!
# def create_static_directory():
#     """Create static directory if it doesn't exist."""
#     static_dir = Path("static")
#     static_dir.mkdir(exist_ok=True)
#     return static_dir

def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    # PURGED: No static directory creation!
    # create_static_directory()
    
    # Debug: Check database connectivity
    try:
        stats = db.get_stats()
        print(f"✅ Database connected: {stats['total']} workflows found")
        if stats['total'] == 0:
            print("🔄 Database is empty. Indexing workflows...")
            db.index_all_workflows()
            stats = db.get_stats()
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("🔄 Attempting to create and index database...")
        try:
            db.index_all_workflows()
            stats = db.get_stats()
            print(f"✅ Database created: {stats['total']} workflows indexed")
        except Exception as e2:
            print(f"❌ Failed to create database: {e2}")
            stats = {'total': 0}
    
    # PURGED: No more static file references!
    print(f"🚀 Starting N8N Workflow Documentation API")
    print(f"📊 Database contains {stats['total']} workflows")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"⚛️  React app serving from: http://{host}:{port}/")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload,
        access_log=True,  # Enable access logs for debugging
        log_level="info"
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='N8N Workflow Documentation API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, reload=args.reload)