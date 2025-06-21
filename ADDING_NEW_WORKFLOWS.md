# 📋 Adding New Workflows to Your Repository

This guide explains how to properly add new workflows while maintaining the professional naming convention established in your repository.

## 🎯 Quick Start

### Method 1: Automated Analysis & Addition
```bash
# Analyze a workflow file and get naming suggestion
python new_workflow_analyzer.py my-workflow.json

# Automatically add a workflow with proper naming
python auto_add_workflow.py my-workflow.json

# Add multiple workflows at once
python auto_add_workflow.py workflow1.json workflow2.json workflow3.json
```

### Method 2: Manual Process
1. Export workflow from n8n as JSON
2. Analyze with the analyzer tool
3. Rename according to suggestion
4. Place in `workflows/` directory
5. Commit to repository

## 🔧 Detailed Instructions

### Step 1: Export from n8n
1. Open your workflow in n8n
2. Click the "..." menu (three dots)
3. Select "Export"
4. Choose "Download as JSON"
5. Save file (usually named something like "workflow.json")

### Step 2: Analyze the Workflow
Use the analyzer tool to understand your workflow:

```bash
python new_workflow_analyzer.py path/to/your/workflow.json
```

This will show you:
- **Services detected** (Gmail, Slack, etc.)
- **Purpose identified** (Create, Update, Sync, etc.)
- **Trigger type** (Manual, Webhook, Scheduled)
- **Suggested filename** following the standard format
- **Next available number** (currently starting from 2054)

### Step 3: Add to Repository

#### Option A: Automatic Addition
```bash
# Add with confirmation prompt
python auto_add_workflow.py path/to/your/workflow.json

# Add without confirmation (auto-approve)
python auto_add_workflow.py -y path/to/your/workflow.json

# Dry run (see what would happen without making changes)
python auto_add_workflow.py -d path/to/your/workflow.json
```

#### Option B: Manual Addition
1. Copy the suggested filename from the analyzer
2. Rename your file to match the suggestion
3. Move it to the `workflows/` directory
4. Commit your changes

## 📁 Naming Convention

Your repository uses this standardized format:
```
XXXX_Service1_Service2_Purpose_Trigger.json
```

### Examples:
- `2054_Gmail_Slack_Send_Webhook.json`
- `2055_Airtable_Notion_Sync_Scheduled.json`
- `2056_Manual_OpenAI_Process_Triggered.json`
- `2057_GoogleSheets_Create.json`

### Components:
- **XXXX**: Sequential number (2054, 2055, 2056...)
- **Service1/Service2**: Up to 2 main services (Gmail, Slack, etc.)
- **Purpose**: What it does (Create, Update, Sync, Send, etc.)
- **Trigger**: How it's activated (Webhook, Scheduled, etc.)

## 🛠️ Advanced Usage

### Batch Processing
```bash
# Scan a directory for workflow files and add them all
python auto_add_workflow.py --scan /path/to/directory

# List potential workflow files in current directory
python auto_add_workflow.py --list-pending

# List potential workflow files in specific directory
python auto_add_workflow.py --list-pending /path/to/directory
```

### Integration with Documentation
After adding workflows, your documentation system will automatically include them:

```bash
# Rebuild documentation (if using API server)
python api_server.py  # Visit http://localhost:8000

# Or generate static documentation
python generate_documentation.py  # Creates workflow-documentation.html
```

## 📊 Current Repository Status

- **Total Workflows**: 2,053 (numbered 0001-2053)
- **Next Available**: 2054
- **Naming Standard**: 100% compliance
- **Documentation**: Fully automated

## 🚨 Important Notes

### DO:
✅ Use the analyzer tool for consistent naming  
✅ Follow the sequential numbering (2054, 2055, etc.)  
✅ Include up to 2 main services in the filename  
✅ Use standard purpose keywords (Create, Update, Sync, etc.)  
✅ Test workflows before committing  

### DON'T:
❌ Skip numbers in the sequence  
❌ Use special characters or emojis in filenames  
❌ Exceed 2 services in the filename  
❌ Use generic names like "workflow.json"  
❌ Forget to commit your changes  

## 🔍 Troubleshooting

### Analyzer Not Working?
```bash
# Check if file is valid JSON
python -m json.tool your-workflow.json

# Ensure it's actually an n8n workflow (should have 'nodes' and 'connections')
grep -q '"nodes"' your-workflow.json && echo "Valid workflow" || echo "Not a workflow"
```

### File Already Exists?
If the suggested filename already exists:
1. Check if it's actually a duplicate workflow
2. If different, the analyzer will suggest an alternative name
3. Manually adjust the filename if needed (keeping the format)

### Wrong Services Detected?
The analyzer tries its best, but you can:
1. Manually rename the file after analysis
2. Follow the naming convention format
3. Ensure the number sequence remains correct

## 🎯 Best Practices

1. **Test First**: Always test workflows in n8n before adding to repository
2. **Descriptive Names**: Use meaningful workflow names in n8n (helps with analysis)
3. **Regular Commits**: Commit new workflows regularly with descriptive messages
4. **Documentation**: Keep workflow descriptions updated in n8n
5. **Backup**: The system creates backups, but git is your safety net

## 🆘 Getting Help

If you encounter issues:
1. Check this guide first
2. Run the analyzer tool with `-h` for help
3. Use dry-run mode to preview changes
4. Check the existing workflows for naming examples

---

## 🎉 Examples

### Simple Workflow Addition
```bash
# 1. Download "My Slack Bot.json" from n8n
# 2. Analyze it
python new_workflow_analyzer.py "My Slack Bot.json"

# Output suggests: 2054_Slack_Manual_Automation.json

# 3. Add it automatically
python auto_add_workflow.py "My Slack Bot.json"

# ✅ Done! Now committed as workflows/2054_Slack_Manual_Automation.json
```

### Batch Addition
```bash
# Add all JSON files in Downloads folder
python auto_add_workflow.py --scan ~/Downloads --auto-confirm

# Result: All valid n8n workflows added with proper naming
```

This system maintains your repository's professional standards while making it easy to add new workflows! 🚀