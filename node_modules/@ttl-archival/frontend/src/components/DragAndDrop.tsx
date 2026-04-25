import { useState, useRef, useCallback } from 'react'
import { cn } from '../utils/cn'
import { GripVertical, Upload, X, FileText, Image, Film, Music } from 'lucide-react'

interface DragItem {
  id: string | number
  content: React.ReactNode
  type?: 'list-item' | 'file'
  file?: File
  [key: string]: any
}

interface DragAndDropProps {
  items: DragItem[]
  onItemsChange: (items: DragItem[]) => void
  onFileUpload?: (files: File[]) => void
  className?: string
  itemClassName?: string
  dragHandle?: boolean
  droppable?: boolean
  multiple?: boolean
  accept?: string
  disabled?: boolean
  orientation?: 'vertical' | 'horizontal'
}

interface DragState {
  draggedItem: DragItem | null
  draggedIndex: number | null
  dropTargetIndex: number | null
  isDraggingOver: boolean
  dragPosition: 'before' | 'after' | null
}

export function DragAndDrop({
  items,
  onItemsChange,
  onFileUpload,
  className = '',
  itemClassName = '',
  dragHandle = true,
  droppable = true,
  multiple = true,
  accept = '*/*',
  disabled = false,
  orientation = 'vertical',
}: DragAndDropProps) {
  const [dragState, setDragState] = useState<DragState>({
    draggedItem: null,
    draggedIndex: null,
    dropTargetIndex: null,
    isDraggingOver: false,
    dragPosition: null,
  })

  const [isDragActive, setIsDragActive] = useState(false)
  const [dragCounter, setDragCounter] = useState(0)
  const dragOverTimeoutRef = useRef<NodeJS.Timeout>()
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Handle drag start
  const handleDragStart = useCallback((e: React.DragEvent, item: DragItem, index: number) => {
    if (disabled) return

    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', JSON.stringify({ item, index }))
    
    setDragState({
      draggedItem: item,
      draggedIndex: index,
      dropTargetIndex: null,
      isDraggingOver: false,
      dragPosition: null,
    })

    // Add visual feedback
    e.currentTarget.classList.add('opacity-50')
  }, [disabled])

  // Handle drag end
  const handleDragEnd = useCallback((e: React.DragEvent) => {
    e.currentTarget.classList.remove('opacity-50')
    
    setDragState({
      draggedItem: null,
      draggedIndex: null,
      dropTargetIndex: null,
      isDraggingOver: false,
      dragPosition: null,
    })

    if (dragOverTimeoutRef.current) {
      clearTimeout(dragOverTimeoutRef.current)
    }
  }, [])

  // Handle drag over
  const handleDragOver = useCallback((e: React.DragEvent, index: number) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'

    if (disabled || dragState.draggedIndex === null) return

    const rect = e.currentTarget.getBoundingClientRect()
    const midpoint = orientation === 'vertical' 
      ? rect.top + rect.height / 2 
      : rect.left + rect.width / 2
    
    const cursorPosition = orientation === 'vertical' ? e.clientY : e.clientX
    const position = cursorPosition < midpoint ? 'before' : 'after'

    setDragState(prev => ({
      ...prev,
      dropTargetIndex: index,
      dragPosition: position,
    }))
  }, [disabled, dragState.draggedIndex, orientation])

  // Handle drop
  const handleDrop = useCallback((e: React.DragEvent, dropIndex: number) => {
    e.preventDefault()
    
    if (disabled || dragState.draggedIndex === null || dragState.draggedItem === null) return

    const newItems = [...items]
    const draggedItem = dragState.draggedItem
    const draggedIndex = dragState.draggedIndex

    // Remove item from original position
    newItems.splice(draggedIndex, 1)
    
    // Calculate new position
    let newPosition = dropIndex
    if (dragState.dragPosition === 'after') {
      newPosition = dropIndex + 1
    }
    
    // Adjust position if we're dropping after the original position
    if (draggedIndex < newPosition) {
      newPosition -= 1
    }

    // Insert item at new position
    newItems.splice(newPosition, 0, draggedItem)
    
    onItemsChange(newItems)

    setDragState({
      draggedItem: null,
      draggedIndex: null,
      dropTargetIndex: null,
      isDraggingOver: false,
      dragPosition: null,
    })
  }, [disabled, dragState, items, onItemsChange])

  // File drag and drop handlers
  const handleFileDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!droppable || disabled) return
    
    setDragCounter(prev => prev + 1)
    setIsDragActive(true)
  }, [droppable, disabled])

  const handleFileDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    setDragCounter(prev => {
      const newCount = prev - 1
      if (newCount === 0) {
        setIsDragActive(false)
      }
      return newCount
    })
  }, [])

  const handleFileDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!droppable || disabled) return
    
    e.dataTransfer.dropEffect = 'copy'
  }, [droppable, disabled])

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!droppable || disabled) return
    
    setIsDragActive(false)
    setDragCounter(0)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileUpload(files)
    }
  }, [droppable, disabled, handleFileUpload])

  const handleFileUpload = useCallback((files: File[]) => {
    if (!multiple && files.length > 1) {
      files = [files[0]]
    }

    // Filter files by accept type
    if (accept !== '*/*') {
      const acceptedTypes = accept.split(',').map(type => type.trim())
      files = files.filter(file => {
        return acceptedTypes.some(type => {
          if (type.startsWith('.')) {
            return file.name.endsWith(type)
          }
          return file.type.match(type.replace('*', '.*'))
        })
      })
    }

    if (files.length === 0) return

    // Create file items
    const fileItems: DragItem[] = files.map(file => ({
      id: `file-${Date.now()}-${Math.random()}`,
      content: (
        <div className="flex items-center gap-3 p-3 bg-white border rounded-lg">
          <FileIcon fileName={file.name} />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{file.name}</p>
            <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation()
              removeFile(`file-${file.name}`)
            }}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ),
      type: 'file',
      file,
    }))

    onItemsChange([...items, ...fileItems])
    onFileUpload?.(files)
  }, [multiple, accept, items, onItemsChange, onFileUpload])

  const removeFile = useCallback((id: string | number) => {
    const newItems = items.filter(item => item.id !== id)
    onItemsChange(newItems)
  }, [items, onItemsChange])

  const openFileDialog = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length > 0) {
      handleFileUpload(files)
    }
    // Reset input
    e.target.value = ''
  }, [handleFileUpload])

  // File icon component
  const FileIcon = ({ fileName }: { fileName: string }) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    
    if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(extension || '')) {
      return <Image className="h-8 w-8 text-blue-500" />
    }
    if (['mp4', 'avi', 'mov', 'wmv', 'webm'].includes(extension || '')) {
      return <Film className="h-8 w-8 text-purple-500" />
    }
    if (['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(extension || '')) {
      return <Music className="h-8 w-8 text-green-500" />
    }
    
    return <FileText className="h-8 w-8 text-gray-500" />
  }

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Get drop indicator styles
  const getDropIndicatorStyles = useCallback((index: number) => {
    if (dragState.dropTargetIndex !== index) return {}

    const baseStyles = {
      position: 'absolute' as const,
      backgroundColor: '#3b82f6',
      zIndex: 10,
    }

    if (orientation === 'vertical') {
      return {
        ...baseStyles,
        left: 0,
        right: 0,
        height: '2px',
        top: dragState.dragPosition === 'before' ? 0 : 'auto',
        bottom: dragState.dragPosition === 'after' ? 0 : 'auto',
      }
    } else {
      return {
        ...baseStyles,
        top: 0,
        bottom: 0,
        width: '2px',
        left: dragState.dragPosition === 'before' ? 0 : 'auto',
        right: dragState.dragPosition === 'after' ? 0 : 'auto',
      }
    }
  }, [dragState.dropTargetIndex, dragState.dragPosition, orientation])

  return (
    <div
      className={cn(
        'relative',
        isDragActive && 'ring-2 ring-blue-500 bg-blue-50',
        className
      )}
      onDragEnter={handleFileDragEnter}
      onDragLeave={handleFileDragLeave}
      onDragOver={handleFileDragOver}
      onDrop={handleFileDrop}
    >
      {/* Upload area */}
      {droppable && (
        <div
          className={cn(
            'border-2 border-dashed border-gray-300 rounded-lg p-6 text-center transition-colors',
            isDragActive ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-400',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
          onClick={!disabled ? openFileDialog : undefined}
        >
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900 mb-2">
            {isDragActive ? 'Drop files here' : 'Drag and drop files here'}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to select files
          </p>
          {accept !== '*/*' && (
            <p className="text-xs text-gray-400">
              Accepted formats: {accept}
            </p>
          )}
          <input
            ref={fileInputRef}
            type="file"
            multiple={multiple}
            accept={accept}
            onChange={handleFileInputChange}
            className="hidden"
            disabled={disabled}
          />
        </div>
      )}

      {/* Draggable items */}
      <div className={cn(
        'mt-4',
        orientation === 'vertical' ? 'space-y-2' : 'flex gap-2 overflow-x-auto'
      )}>
        {items.map((item, index) => (
          <div
            key={item.id}
            className={cn(
              'relative group transition-all duration-200',
              orientation === 'vertical' ? 'w-full' : 'flex-shrink-0',
              dragState.draggedIndex === index && 'opacity-50',
              itemClassName
            )}
            draggable={!disabled}
            onDragStart={(e) => handleDragStart(e, item, index)}
            onDragEnd={handleDragEnd}
            onDragOver={(e) => handleDragOver(e, index)}
            onDrop={(e) => handleDrop(e, index)}
          >
            {/* Drop indicator */}
            {dragState.dropTargetIndex === index && (
              <div style={getDropIndicatorStyles(index)} />
            )}

            {/* Drag handle */}
            {dragHandle && (
              <div
                className={cn(
                  'absolute -left-8 top-1/2 transform -translate-y-1/2 p-1 rounded cursor-move opacity-0 group-hover:opacity-100 transition-opacity',
                  disabled && 'cursor-not-allowed'
                )}
              >
                <GripVertical className="h-4 w-4 text-gray-400" />
              </div>
            )}

            {/* Item content */}
            <div className={cn(
              'bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow',
              disabled && 'opacity-50 cursor-not-allowed'
            )}>
              {item.content}
            </div>
          </div>
        ))}
      </div>

      {/* Empty state */}
      {items.length === 0 && !isDragActive && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg font-medium mb-2">No items yet</p>
          <p className="text-sm">
            {droppable ? 'Drag and drop files or add items to get started' : 'Add items to get started'}
          </p>
        </div>
      )}
    </div>
  )
}

// Hook for drag and drop state management
export function useDragAndDrop<T extends { id: string | number }>(
  initialItems: T[]
) {
  const [items, setItems] = useState<T[]>(initialItems)

  const moveItem = useCallback((fromIndex: number, toIndex: number) => {
    const newItems = [...items]
    const [movedItem] = newItems.splice(fromIndex, 1)
    newItems.splice(toIndex, 0, movedItem)
    setItems(newItems)
    return newItems
  }, [items])

  const addItem = useCallback((item: T) => {
    setItems(prev => [...prev, item])
  }, [])

  const removeItem = useCallback((id: string | number) => {
    setItems(prev => prev.filter(item => item.id !== id))
  }, [])

  const updateItem = useCallback((id: string | number, updates: Partial<T>) => {
    setItems(prev => prev.map(item => 
      item.id === id ? { ...item, ...updates } : item
    ))
  }, [])

  return {
    items,
    setItems,
    moveItem,
    addItem,
    removeItem,
    updateItem,
  }
}
