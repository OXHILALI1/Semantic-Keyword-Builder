import * as React from "react"
import { Upload, FileText, Loader2 } from "../lib/icons"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { useAnalyzeWorkflow, useAddWorkflow } from "@/hooks/use-workflows"
import { cn } from "@/lib/utils"

interface AddWorkflowDialogProps {
  children: React.ReactNode
}

export function AddWorkflowDialog({ children }: AddWorkflowDialogProps) {
  const [open, setOpen] = React.useState(false)
  const [file, setFile] = React.useState<File | null>(null)
  const [customName, setCustomName] = React.useState("")
  const [dragOver, setDragOver] = React.useState(false)

  const analyzeWorkflow = useAnalyzeWorkflow()
  const addWorkflow = useAddWorkflow()

  const handleFileSelect = React.useCallback((selectedFile: File) => {
    if (selectedFile.type === 'application/json' || selectedFile.name.endsWith('.json')) {
      setFile(selectedFile)
      analyzeWorkflow.mutate(selectedFile)
    } else {
      alert('Please select a valid JSON file')
    }
  }, [analyzeWorkflow])

  const handleDrop = React.useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileSelect(droppedFile)
    }
  }, [handleFileSelect])

  const handleDragOver = React.useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = React.useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleSubmit = () => {
    if (file) {
      addWorkflow.mutate(
        { 
          file, 
          name: customName || analyzeWorkflow.data?.suggestedName 
        },
        {
          onSuccess: (response) => {
            if (response.success) {
              setOpen(false)
              setFile(null)
              setCustomName("")
              analyzeWorkflow.reset()
            }
          }
        }
      )
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen)
    if (!newOpen) {
      // Reset state when closing
      setFile(null)
      setCustomName("")
      analyzeWorkflow.reset()
      addWorkflow.reset()
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add New Workflow</DialogTitle>
          <DialogDescription>
            Upload an n8n workflow JSON file to add it to your collection.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {!file ? (
            <div
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
                dragOver 
                  ? "border-primary bg-primary/5" 
                  : "border-border hover:border-primary/50"
              )}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-sm font-medium mb-2">
                Drop your workflow file here
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                or click to browse
              </p>
              <Button
                variant="outline"
                onClick={() => {
                  const input = document.createElement('input')
                  input.type = 'file'
                  input.accept = '.json'
                  input.onchange = (e) => {
                    const file = (e.target as HTMLInputElement).files?.[0]
                    if (file) handleFileSelect(file)
                  }
                  input.click()
                }}
              >
                Browse Files
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <FileText className="h-8 w-8 text-primary" />
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>

              {analyzeWorkflow.isPending && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing workflow...
                </div>
              )}

              {analyzeWorkflow.data && (
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium">Suggested Name:</label>
                    <p className="text-sm text-muted-foreground">
                      {analyzeWorkflow.data.suggestedName}
                    </p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Analysis:</label>
                    <div className="text-sm text-muted-foreground space-y-1">
                      <p>• {analyzeWorkflow.data.analysis.nodeCount} nodes</p>
                      <p>• Trigger: {analyzeWorkflow.data.analysis.triggerType}</p>
                      <p>• Services: {analyzeWorkflow.data.analysis.services.join(', ')}</p>
                      <p>• Complexity: {analyzeWorkflow.data.analysis.complexity}</p>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="custom-name" className="text-sm font-medium">
                      Custom Name (optional):
                    </label>
                    <input
                      id="custom-name"
                      type="text"
                      value={customName}
                      onChange={(e) => setCustomName(e.target.value)}
                      placeholder="Leave empty to use suggested name"
                      className="w-full mt-1 px-3 py-2 border border-input rounded-md text-sm"
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!file || analyzeWorkflow.isPending || addWorkflow.isPending}
          >
            {addWorkflow.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Adding...
              </>
            ) : (
              'Add Workflow'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}