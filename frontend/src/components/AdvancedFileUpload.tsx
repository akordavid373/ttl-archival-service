import React, { useState, useCallback, useRef } from 'react'
import { 
  Upload, 
  File, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  Image as ImageIcon, 
  Film, 
  Music,
  Loader2,
  Eye,
  RefreshCw
} from 'lucide-react'
import { cn } from '../utils/cn'

interface UploadingFile {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error' | 'paused'
  previewUrl?: string
  error?: string
  uploadSpeed?: number
  timeRemaining?: number
}

interface FileUploadProps {
  onUploadComplete?: (files: File[]) => void
  onFileSelect?: (files: File[]) => void
  onProgress?: (fileId: string, progress: number) => void
  maxSize?: number // in bytes
  maxFiles?: number
  allowedTypes?: string[]
  disabled?: boolean
  autoUpload?: boolean
  showPreview?: boolean
  className?: string
}

export function AdvancedFileUpload({ 
  onUploadComplete,
  onFileSelect,
  onProgress,
  maxSize = 50 * 1024 * 1024, // 50MB default
  maxFiles = 10,
  allowedTypes = ['image/*', 'application/pdf', 'text/*', 'application/zip', 'application/x-zip-compressed', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  disabled = false,
  autoUpload = false,
  showPreview = true,
  className = ''
}: FileUploadProps) {
  const [files, setFiles] = useState<UploadingFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const uploadControllersRef = useRef<Map<string, AbortController>>(new Map())

  const generateId = () => Math.random().toString(36).substring(7)

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize) {
      return `File is too large. Max size is ${maxSize / (1024 * 1024)}MB.`
    }
    
    const isTypeAllowed = allowedTypes.some(type => {
      if (type.endsWith('/*')) {
        return file.type.startsWith(type.replace('/*', ''))
      }
      return file.type === type
    })

    if (!isTypeAllowed && allowedTypes.length > 0) {
      return `File type "${file.type}" not supported. Allowed types: ${allowedTypes.join(', ')}`
    }

    return null
  }

  const addFiles = useCallback((newFiles: FileList | File[]) => {
    const filesArray = Array.from(newFiles)
    
    // Check max files limit
    if (files.length + filesArray.length > maxFiles) {
      const remainingSlots = maxFiles - files.length
      if (remainingSlots <= 0) {
        return // Don't add any files if limit reached
      }
      filesArray.splice(remainingSlots) // Keep only what we can add
    }
    
    const mappedFiles: UploadingFile[] = filesArray.map(file => {
      const error = validateFile(file)
      const previewUrl = file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
      
      return {
        id: generateId(),
        file,
        progress: 0,
        status: error ? 'error' as const : 'pending' as const,
        previewUrl,
        error: error || undefined
      }
    })

    setFiles((prev: UploadingFile[]) => [...prev, ...mappedFiles])
    
    // Notify parent component about file selection
    if (onFileSelect) {
      onFileSelect(filesArray.filter(file => !validateFile(file)))
    }

    // Auto-upload if enabled
    if (autoUpload) {
      setTimeout(() => {
        mappedFiles.forEach(f => {
          if (f.status === 'pending') {
            startUpload(f.id)
          }
        })
      }, 500)
    }
  }, [files.length, maxFiles, maxSize, allowedTypes, autoUpload, onFileSelect])

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (!disabled && e.dataTransfer.files) {
      addFiles(e.dataTransfer.files)
    }
  }

  const removeFile = (id: string) => {
    // Cancel any ongoing upload
    const controller = uploadControllersRef.current.get(id)
    if (controller) {
      controller.abort()
      uploadControllersRef.current.delete(id)
    }

    setFiles((prev: UploadingFile[]) => {
      const filtered = prev.filter((f: UploadingFile) => f.id !== id)
      // Cleanup object URL
      const removed = prev.find((f: UploadingFile) => f.id === id)
      if (removed?.previewUrl) URL.revokeObjectURL(removed.previewUrl)
      return filtered
    })
  }

  const startUpload = async (id: string) => {
    if (disabled) return
    
    const controller = new AbortController()
    uploadControllersRef.current.set(id, controller)

    setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => 
      f.id === id ? { ...f, status: 'uploading' } : f
    ))

    const file = files.find(f => f.id === id)
    if (!file) return

    const startTime = Date.now()
    const chunkSize = 1024 * 1024 // 1MB chunks
    const totalChunks = Math.ceil(file.file.size / chunkSize)
    
    try {
      // Simulate upload with progress tracking
      for (let chunk = 0; chunk <= totalChunks; chunk++) {
        if (controller.signal.aborted) {
          throw new Error('Upload cancelled')
        }

        if (isPaused) {
          await new Promise(resolve => {
            const checkPause = setInterval(() => {
              if (!isPaused) {
                clearInterval(checkPause)
                resolve(undefined)
              }
            }, 100)
          })
        }

        const progress = Math.round((chunk / totalChunks) * 100)
        const elapsed = Date.now() - startTime
        const bytesUploaded = chunk * chunkSize
        const uploadSpeed = bytesUploaded / (elapsed / 1000) // bytes per second
        const remainingBytes = file.file.size - bytesUploaded
        const timeRemaining = remainingBytes / uploadSpeed

        setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => 
          f.id === id ? { 
            ...f, 
            progress, 
            uploadSpeed,
            timeRemaining: timeRemaining > 0 ? Math.round(timeRemaining) : 0
          } : f
        ))

        // Notify parent component about progress
        if (onProgress) {
          onProgress(id, progress)
        }

        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200))
      }

      setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => 
        f.id === id ? { ...f, status: 'completed', progress: 100 } : f
      ))

      // Check if all files are completed
      const updatedFiles = files.map(f => 
        f.id === id ? { ...f, status: 'completed' as const, progress: 100 } : f
      )
      if (updatedFiles.every(f => f.status === 'completed' || f.status === 'error')) {
        if (onUploadComplete) {
          onUploadComplete(updatedFiles.map(f => f.file))
        }
      }

    } catch (error) {
      if (error instanceof Error && error.message !== 'Upload cancelled') {
        setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => 
          f.id === id ? { ...f, status: 'error', error: 'Upload failed' } : f
        ))
      }
    } finally {
      uploadControllersRef.current.delete(id)
    }
  }

  const pauseUpload = (id: string) => {
    setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => 
      f.id === id ? { ...f, status: 'paused' } : f
    ))
    setIsPaused(true)
  }

  const resumeUpload = (id: string) => {
    setIsPaused(false)
    startUpload(id)
  }

  const cancelUpload = (id: string) => {
    const controller = uploadControllersRef.current.get(id)
    if (controller) {
      controller.abort()
      uploadControllersRef.current.delete(id)
    }
    
    setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => 
      f.id === id ? { ...f, status: 'pending', progress: 0 } : f
    ))
  }

  const uploadAll = async () => {
    const pendingFiles = files.filter((f: UploadingFile) => f.status === 'pending')
    await Promise.all(pendingFiles.map((f: UploadingFile) => startUpload(f.id)))
  }

  const clearAll = () => {
    // Cancel all ongoing uploads
    uploadControllersRef.current.forEach(controller => controller.abort())
    uploadControllersRef.current.clear()

    // Cleanup all preview URLs
    files.forEach(f => {
      if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
    })

    setFiles([])
  }

  const retryFailedUploads = () => {
    const failedFiles = files.filter((f: UploadingFile) => f.status === 'error')
    failedFiles.forEach(f => {
      setFiles((prev: UploadingFile[]) => prev.map((file: UploadingFile) => 
        file.id === f.id ? { ...file, status: 'pending', progress: 0, error: undefined } : file
      ))
      setTimeout(() => startUpload(f.id), 100)
    })
  }

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <ImageIcon className="h-5 w-5" />
    if (type.startsWith('video/')) return <Film className="h-5 w-5" />
    if (type.startsWith('audio/')) return <Music className="h-5 w-5" />
    if (type.includes('pdf') || type.includes('text')) return <FileText className="h-5 w-5" />
    return <File className="h-5 w-5" />
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatSpeed = (bytesPerSecond: number) => {
    if (bytesPerSecond === 0) return '0 B/s'
    const k = 1024
    const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s']
    const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k))
    return parseFloat((bytesPerSecond / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const formatTime = (seconds: number) => {
    if (seconds === 0) return '0s'
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  const completedFiles = files.filter(f => f.status === 'completed').length
  const failedFiles = files.filter(f => f.status === 'error').length
  const uploadingFiles = files.filter(f => f.status === 'uploading').length

  return (
    <div className={cn("space-y-6 w-full max-w-4xl mx-auto", className)}>
      {/* Upload Zone */}
      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={cn(
          "relative group cursor-pointer border-2 border-dashed rounded-3xl p-12 transition-all duration-300 flex flex-col items-center justify-center gap-4",
          isDragging 
            ? "border-primary bg-primary/5 scale-[0.99]" 
            : "border-border/60 hover:border-primary/40 hover:bg-accent/20",
          files.length > 0 ? "py-8" : "py-16",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <input 
          type="file" 
          multiple 
          className="hidden" 
          ref={fileInputRef}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => e.target.files && addFiles(e.target.files)}
          disabled={disabled}
        />
        
        <div className={cn(
          "w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-inner bg-accent group-hover:scale-110",
          isDragging ? "bg-primary text-primary-foreground animate-bounce" : "text-primary"
        )}>
          <Upload className="h-8 w-8" />
        </div>
        
        <div className="text-center">
          <p className="text-lg font-bold tracking-tight">Drop files here or click to browse</p>
          <p className="text-xs text-muted-foreground mt-2 font-medium">
            Supports {allowedTypes.join(', ')} (Max {formatSize(maxSize)}, {maxFiles} files)
          </p>
        </div>

        {isDragging && (
          <div className="absolute inset-2 bg-primary/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border-2 border-primary border-dashed">
            <p className="text-primary font-bold text-lg animate-pulse">Release to upload files</p>
          </div>
        )}
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4 animate-in slide-in-from-bottom-2 duration-300">
          {/* Header with stats and actions */}
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-4">
              <h4 className="text-sm font-bold text-muted-foreground uppercase tracking-widest">
                Files ({files.length})
              </h4>
              <div className="flex items-center gap-2 text-xs">
                {completedFiles > 0 && (
                  <span className="text-emerald-500 font-medium">
                    ✓ {completedFiles} completed
                  </span>
                )}
                {failedFiles > 0 && (
                  <span className="text-rose-500 font-medium">
                    ✗ {failedFiles} failed
                  </span>
                )}
                {uploadingFiles > 0 && (
                  <span className="text-primary font-medium">
                    ↑ {uploadingFiles} uploading
                  </span>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {files.some(f => f.status === 'pending') && (
                <button 
                  onClick={(e) => { e.stopPropagation(); uploadAll(); }}
                  className="text-xs font-bold text-primary hover:underline"
                  disabled={disabled}
                >
                  Upload All
                </button>
              )}
              {failedFiles > 0 && (
                <button 
                  onClick={(e) => { e.stopPropagation(); retryFailedUploads(); }}
                  className="text-xs font-bold text-amber-500 hover:underline"
                  disabled={disabled}
                >
                  Retry Failed
                </button>
              )}
              <button 
                onClick={(e) => { e.stopPropagation(); clearAll(); }}
                className="text-xs font-bold text-rose-500 hover:underline"
                disabled={disabled}
              >
                Clear All
              </button>
            </div>
          </div>
          
          {/* Files Grid */}
          <div className="grid gap-3 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
            {files.map((f) => (
              <div 
                key={f.id} 
                className={cn(
                  "p-4 rounded-2xl border border-border/50 bg-card/60 backdrop-blur-md transition-all group relative overflow-hidden",
                  f.status === 'error' ? "border-rose-500/30 bg-rose-500/5" : "hover:border-primary/20",
                  f.status === 'uploading' && "border-primary/30 bg-primary/5"
                )}
              >
                {/* Progress Background */}
                {f.status === 'uploading' && (
                  <div 
                    className="absolute bottom-0 left-0 h-1 bg-primary/20 transition-all duration-300" 
                    style={{ width: `${f.progress}%` }}
                  />
                )}

                <div className="flex items-center gap-4 relative z-10">
                  {/* Preview/Icon */}
                  <div className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center shadow-inner overflow-hidden shrink-0">
                    {showPreview && f.previewUrl ? (
                      <img src={f.previewUrl} alt="Preview" className="w-full h-full object-cover" />
                    ) : (
                      getFileIcon(f.file.type)
                    )}
                  </div>
                  
                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-bold truncate pr-8">{f.file.name}</p>
                      <button 
                         onClick={() => removeFile(f.id)}
                         className="p-1.5 hover:bg-accent rounded-lg text-muted-foreground hover:text-rose-500 transition-colors"
                         disabled={disabled}
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <p className="text-[10px] font-bold text-muted-foreground uppercase">{formatSize(f.file.size)}</p>
                      <div className="h-1 w-1 rounded-full bg-border" />
                      
                      {/* Status */}
                      {f.status === 'pending' && (
                        <span className="text-[10px] font-bold text-primary uppercase">Ready to Upload</span>
                      )}
                      {f.status === 'uploading' && (
                        <div className="flex items-center gap-2">
                           <Loader2 className="h-3 w-3 animate-spin text-primary" />
                           <span className="text-[10px] font-bold text-primary uppercase">
                             Uploading... {f.progress}%
                           </span>
                           {f.uploadSpeed && (
                             <>
                               <div className="h-1 w-1 rounded-full bg-border" />
                               <span className="text-[10px] text-muted-foreground">
                                 {formatSpeed(f.uploadSpeed)}
                               </span>
                             </>
                           )}
                           {f.timeRemaining !== undefined && f.timeRemaining > 0 && (
                             <>
                               <div className="h-1 w-1 rounded-full bg-border" />
                               <span className="text-[10px] text-muted-foreground">
                                 {formatTime(f.timeRemaining)} left
                               </span>
                             </>
                           )}
                        </div>
                      )}
                      {f.status === 'paused' && (
                        <div className="flex items-center gap-2">
                           <RefreshCw className="h-3 w-3 text-amber-500" />
                           <span className="text-[10px] font-bold text-amber-500 uppercase">Paused</span>
                        </div>
                      )}
                      {f.status === 'completed' && (
                        <div className="flex items-center gap-1.5 text-emerald-500">
                          <CheckCircle2 className="h-3 w-3" />
                          <span className="text-[10px] font-bold uppercase">Completed</span>
                        </div>
                      )}
                      {f.status === 'error' && (
                        <div className="flex items-center gap-1.5 text-rose-500">
                          <AlertCircle className="h-3 w-3" />
                          <span className="text-[10px] font-bold uppercase">{f.error || 'Upload Failed'}</span>
                        </div>
                      )}
                    </div>

                    {/* Progress Bar */}
                    {(f.status === 'uploading' || f.status === 'paused') && (
                      <div className="mt-2">
                        <div className="w-full bg-border/20 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className="bg-primary h-full transition-all duration-300 ease-out"
                            style={{ width: `${f.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-1">
                    {f.status === 'pending' && (
                      <button 
                        onClick={() => startUpload(f.id)}
                        className="p-1.5 hover:bg-accent rounded-lg text-primary transition-colors"
                        disabled={disabled}
                        title="Start Upload"
                      >
                        <Upload className="h-4 w-4" />
                      </button>
                    )}
                    {f.status === 'uploading' && (
                      <button 
                        onClick={() => pauseUpload(f.id)}
                        className="p-1.5 hover:bg-accent rounded-lg text-amber-500 transition-colors"
                        disabled={disabled}
                        title="Pause Upload"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </button>
                    )}
                    {f.status === 'paused' && (
                      <button 
                        onClick={() => resumeUpload(f.id)}
                        className="p-1.5 hover:bg-accent rounded-lg text-primary transition-colors"
                        disabled={disabled}
                        title="Resume Upload"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </button>
                    )}
                    {f.status === 'uploading' && (
                      <button 
                        onClick={() => cancelUpload(f.id)}
                        className="p-1.5 hover:bg-accent rounded-lg text-rose-500 transition-colors"
                        disabled={disabled}
                        title="Cancel Upload"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                    {f.status === 'completed' && showPreview && f.previewUrl && (
                      <button 
                        onClick={() => window.open(f.previewUrl, '_blank')}
                        className="p-1.5 hover:bg-accent rounded-lg text-primary transition-colors"
                        disabled={disabled}
                        title="Preview"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    )}
                    {f.status === 'error' && (
                      <button 
                        onClick={() => startUpload(f.id)}
                        className="p-1.5 hover:bg-accent rounded-lg text-amber-500 transition-colors"
                        disabled={disabled}
                        title="Retry Upload"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
