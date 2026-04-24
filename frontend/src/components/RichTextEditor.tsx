import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import Highlight from '@tiptap/extension-highlight'
import Link from '@tiptap/extension-link'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'
import { lowlight } from 'lowlight'
import React, { useEffect, useState, useRef, useCallback } from 'react'
import { Button } from './ui/button'
import { 
  Bold, 
  Italic, 
  List, 
  ListOrdered, 
  Quote, 
  Code, 
  Heading1, 
  Heading2, 
  Heading3,
  Image as ImageIcon,
  Link as LinkIcon,
  Table as TableIcon,
  Highlighter,
  Undo,
  Redo,
  Save,
  Upload,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Strikethrough,
  Code2
} from 'lucide-react'

// Import common languages for code highlighting
// @ts-ignore - highlight.js types are not perfect
import javascript from 'highlight.js/lib/languages/javascript'
// @ts-ignore - highlight.js types are not perfect
import typescript from 'highlight.js/lib/languages/typescript'
// @ts-ignore - highlight.js types are not perfect
import python from 'highlight.js/lib/languages/python'
// @ts-ignore - highlight.js types are not perfect
import css from 'highlight.js/lib/languages/css'
// @ts-ignore - highlight.js types are not perfect
import html from 'highlight.js/lib/languages/xml'
// @ts-ignore - highlight.js types are not perfect
import json from 'highlight.js/lib/languages/json'
// @ts-ignore - highlight.js types are not perfect
import sql from 'highlight.js/lib/languages/sql'
// @ts-ignore - highlight.js types are not perfect
import bash from 'highlight.js/lib/languages/bash'
// @ts-ignore - highlight.js types are not perfect
import markdown from 'highlight.js/lib/languages/markdown'

lowlight.register('javascript', javascript)
lowlight.register('typescript', typescript)
lowlight.register('python', python)
lowlight.register('css', css)
lowlight.register('html', html)
lowlight.register('json', json)
lowlight.register('sql', sql)
lowlight.register('bash', bash)
lowlight.register('markdown', markdown)

interface RichTextEditorProps {
  content?: string
  onChange?: (content: string, plainText?: string) => void
  placeholder?: string
  editable?: boolean
  autoSave?: boolean
  autoSaveDelay?: number
  className?: string
  maxLength?: number
  showCharacterCount?: boolean
  enableMediaUpload?: boolean
  onMediaUpload?: (file: File) => Promise<string>
  onSave?: (content: string) => Promise<void>
  toolbarClassName?: string
  contentClassName?: string
}

export function RichTextEditor({
  content = '',
  onChange,
  placeholder = 'Start typing...',
  editable = true,
  autoSave = true,
  autoSaveDelay = 2000,
  className = '',
  maxLength,
  showCharacterCount = false,
  enableMediaUpload = false,
  onMediaUpload,
  onSave,
  toolbarClassName = '',
  contentClassName = ''
}: RichTextEditorProps) {
  const [lastSavedContent, setLastSavedContent] = useState(content)
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'unsaved' | 'error'>('saved')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const autoSaveTimerRef = useRef<ReturnType<typeof setTimeout>>()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6],
        },
      }),
      Placeholder.configure({
        placeholder,
      }),
      CharacterCount.configure({
        limit: maxLength,
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full h-auto rounded-lg shadow-sm',
        },
        allowBase64: enableMediaUpload,
      }),
      CodeBlockLowlight.configure({
        lowlight,
        HTMLAttributes: {
          class: 'rounded-lg bg-gray-900 text-gray-100 p-4 my-4 overflow-x-auto',
        },
        defaultLanguage: 'plaintext',
      }),
      Highlight.configure({
        multicolor: true,
        HTMLAttributes: {
          class: 'bg-yellow-200 px-1 rounded',
        },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 underline hover:text-blue-800 cursor-pointer',
        },
        linkOnPaste: true,
        autolink: true,
      }),
      Table.configure({
        resizable: true,
        HTMLAttributes: {
          class: 'border-collapse table-auto w-full my-4',
        },
        handleWidth: 5,
        cellMinWidth: 100,
      }),
      TableRow.configure({
        HTMLAttributes: {
          class: 'border-b',
        },
      }),
      TableHeader.configure({
        HTMLAttributes: {
          class: 'border border-gray-300 px-4 py-2 bg-gray-50 font-semibold text-left',
        },
      }),
      TableCell.configure({
        HTMLAttributes: {
          class: 'border border-gray-300 px-4 py-2',
        },
      }),
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML()
      const plainText = editor.getText()
      onChange?.(newContent, plainText)
      
      if (autoSave) {
        setSaveStatus('unsaved')
      }
    },
    onSelectionUpdate: () => {
      // Handle selection updates if needed
    },
    onFocus: () => {
      // Handle focus if needed
    },
    onBlur: ({ editor, event }) => {
      // Trigger save on blur if there are unsaved changes
      if (autoSave && saveStatus === 'unsaved') {
        handleManualSave()
      }
    },
    editorProps: {
      attributes: {
        class: 'prose prose-lg max-w-none focus:outline-none min-h-[200px] p-4',
        spellcheck: 'true',
      },
    },
  })

  // Enhanced auto-save functionality
  const handleManualSave = useCallback(async () => {
    if (!editor) return
    
    const currentContent = editor.getHTML()
    if (currentContent !== lastSavedContent) {
      setSaveStatus('saving')
      
      try {
        if (onSave) {
          await onSave(currentContent)
        } else {
          // Simulate save operation - in real app, this would be an API call
          await new Promise(resolve => setTimeout(resolve, 500))
        }
        setLastSavedContent(currentContent)
        setSaveStatus('saved')
      } catch (error) {
        console.error('Save failed:', error)
        setSaveStatus('error')
      }
    }
  }, [editor, lastSavedContent, onSave])

  useEffect(() => {
    if (!editor || !autoSave) return

    // Clear existing timer
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current)
    }

    // Set new timer
    autoSaveTimerRef.current = setTimeout(() => {
      handleManualSave()
    }, autoSaveDelay)

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
    }
  }, [editor?.getHTML(), autoSave, autoSaveDelay, handleManualSave])

  const setLink = () => {
    if (!editor) return
    
    const previousUrl = editor.getAttributes('link').href
    const url = window.prompt('URL', previousUrl)

    if (url === null) {
      return
    }

    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run()
    } else {
      editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
    }
  }

  const addImage = async () => {
    if (!editor) return
    
    if (enableMediaUpload && onMediaUpload) {
      // Open file dialog for image upload
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.onchange = async (e) => {
        const file = (e.target as HTMLInputElement).files?.[0]
        if (file) {
          setIsUploading(true)
          setUploadProgress(0)
          
          try {
            const url = await onMediaUpload(file)
            editor.chain().focus().setImage({ src: url }).run()
          } catch (error) {
            console.error('Image upload failed:', error)
          } finally {
            setIsUploading(false)
            setUploadProgress(0)
          }
        }
      }
      input.click()
    } else {
      // Fallback to URL input
      const url = window.prompt('Image URL')
      if (url) {
        editor.chain().focus().setImage({ src: url }).run()
      }
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file || !onMediaUpload || !editor) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 100)

      const url = await onMediaUpload(file)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      // Insert based on file type
      if (file.type.startsWith('image/')) {
        editor.chain().focus().setImage({ src: url }).run()
      } else if (file.type.startsWith('video/')) {
        // For video files, insert as HTML
        const videoHtml = `<video controls class="max-w-full h-auto rounded-lg"><source src="${url}" type="${file.type}"></video>`
        editor.chain().focus().insertContent(videoHtml).run()
      } else if (file.type.startsWith('audio/')) {
        // For audio files, insert as HTML
        const audioHtml = `<audio controls class="w-full"><source src="${url}" type="${file.type}"></audio>`
        editor.chain().focus().insertContent(audioHtml).run()
      }
    } catch (error) {
      console.error('File upload failed:', error)
    } finally {
      setTimeout(() => {
        setIsUploading(false)
        setUploadProgress(0)
      }, 500)
    }
  }

  const insertTable = () => {
    if (!editor) return
    
    editor.chain().focus()
      .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
      .run()
  }

  const addHighlight = () => {
    if (!editor) return
    
    editor.chain().focus().toggleHighlight({ color: '#fef08a' }).run()
  }

  // Expose addHighlight for potential external use - disabled for now
  // React.useImperativeHandle(ref, () => ({
  //   addHighlight
  // }))

  if (!editor) {
    return <div className="border rounded-lg p-4 min-h-[200px] bg-gray-50"></div>
  }

  return (
    <div className={`border rounded-lg overflow-hidden bg-white ${className}`}>
      {/* Toolbar */}
      <div className={`border-b bg-gray-50 p-2 flex flex-wrap gap-1 ${toolbarClassName}`}>
        {/* Text Formatting */}
        <div className="flex gap-1 border-r pr-2 mr-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleBold().run()}
            disabled={!editor.can().chain().focus().toggleBold().run()}
            className={editor.isActive('bold') ? 'bg-gray-200' : ''}
            title="Bold (Ctrl+B)"
          >
            <Bold className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleItalic().run()}
            disabled={!editor.can().chain().focus().toggleItalic().run()}
            className={editor.isActive('italic') ? 'bg-gray-200' : ''}
            title="Italic (Ctrl+I)"
          >
            <Italic className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleStrike().run()}
            disabled={!editor.can().chain().focus().toggleStrike().run()}
            className={editor.isActive('strike') ? 'bg-gray-200' : ''}
            title="Strikethrough"
          >
            <Strikethrough className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleCode().run()}
            disabled={!editor.can().chain().focus().toggleCode().run()}
            className={editor.isActive('code') ? 'bg-gray-200' : ''}
            title="Inline Code"
          >
            <Code2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleHighlight().run()}
            disabled={!editor.can().chain().focus().toggleHighlight().run()}
            className={editor.isActive('highlight') ? 'bg-gray-200' : ''}
            title="Highlight"
          >
            <Highlighter className="h-4 w-4" />
          </Button>
        </div>

        {/* Headings */}
        <div className="flex gap-1 border-r pr-2 mr-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            className={editor.isActive('heading', { level: 1 }) ? 'bg-gray-200' : ''}
          >
            <Heading1 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            className={editor.isActive('heading', { level: 2 }) ? 'bg-gray-200' : ''}
          >
            <Heading2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            className={editor.isActive('heading', { level: 3 }) ? 'bg-gray-200' : ''}
          >
            <Heading3 className="h-4 w-4" />
          </Button>
        </div>

        {/* Text Alignment - removed for now due to extension issues */}
        {/* <div className="flex gap-1 border-r pr-2 mr-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().setTextAlign('left').run()}
            className={editor.isActive({ textAlign: 'left' }) ? 'bg-gray-200' : ''}
            title="Align Left"
          >
            <AlignLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().setTextAlign('center').run()}
            className={editor.isActive({ textAlign: 'center' }) ? 'bg-gray-200' : ''}
            title="Align Center"
          >
            <AlignCenter className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().setTextAlign('right').run()}
            className={editor.isActive({ textAlign: 'right' }) ? 'bg-gray-200' : ''}
            title="Align Right"
          >
            <AlignRight className="h-4 w-4" />
          </Button>
        </div> */}

        {/* Lists */}
        <div className="flex gap-1 border-r pr-2 mr-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={editor.isActive('bulletList') ? 'bg-gray-200' : ''}
            title="Bullet List"
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={editor.isActive('orderedList') ? 'bg-gray-200' : ''}
            title="Numbered List"
          >
            <ListOrdered className="h-4 w-4" />
          </Button>
        </div>

        {/* Insert Elements */}
        <div className="flex gap-1 border-r pr-2 mr-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={setLink}
            className={editor.isActive('link') ? 'bg-gray-200' : ''}
            title="Insert Link"
          >
            <LinkIcon className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={addImage}
            disabled={isUploading}
            title="Insert Image"
          >
            <ImageIcon className="h-4 w-4" />
          </Button>
          {enableMediaUpload && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,video/*,audio/*"
                onChange={handleFileUpload}
                className="hidden"
              />
              <Button
                variant="ghost"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                title="Upload Media"
              >
                <Upload className="h-4 w-4" />
              </Button>
            </>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={insertTable}
            title="Insert Table"
          >
            <TableIcon className="h-4 w-4" />
          </Button>
        </div>

        {/* Other Elements */}
        <div className="flex gap-1 border-r pr-2 mr-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            className={editor.isActive('blockquote') ? 'bg-gray-200' : ''}
          >
            <Quote className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            className={editor.isActive('codeBlock') ? 'bg-gray-200' : ''}
          >
            <Code className="h-4 w-4" />
          </Button>
        </div>

        {/* History & Actions */}
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().chain().focus().undo().run()}
            title="Undo (Ctrl+Z)"
          >
            <Undo className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().chain().focus().redo().run()}
            title="Redo (Ctrl+Y)"
          >
            <Redo className="h-4 w-4" />
          </Button>
          {autoSave && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleManualSave}
              disabled={saveStatus === 'saving'}
              title="Save Now"
            >
              <Save className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Save Status & Info */}
      <div className="px-4 py-1 text-xs border-b bg-gray-50 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <span className={`flex items-center gap-1 ${
            saveStatus === 'saved' ? 'text-green-600' : 
            saveStatus === 'saving' ? 'text-blue-600' : 
            saveStatus === 'error' ? 'text-red-600' : 
            'text-gray-500'
          }`}>
            {saveStatus === 'saved' && <><Save className="h-3 w-3" /> All changes saved</>}
            {saveStatus === 'saving' && <><Save className="h-3 w-3 animate-spin" /> Saving...</>}
            {saveStatus === 'unsaved' && <>Unsaved changes</>}
            {saveStatus === 'error' && <>Save failed</>}
          </span>
          {showCharacterCount && editor && (
            <span className="text-gray-500">
              {editor.storage.characterCount.characters()}{maxLength && `/${maxLength}`} characters
              {editor.storage.characterCount.words() && ` • ${editor.storage.characterCount.words()} words`}
            </span>
          )}
        </div>
        {isUploading && (
          <div className="flex items-center gap-2 text-blue-600">
            <div className="animate-spin h-3 w-3 border border-current border-t-transparent rounded-full" />
            Uploading... {uploadProgress}%
          </div>
        )}
      </div>

      {/* Editor Content */}
      <div className={`min-h-[300px] relative ${contentClassName}`}>
        <EditorContent 
          editor={editor} 
          className="prose prose-lg max-w-none focus:outline-none min-h-[300px]"
        />
        {!editor?.isFocused && editor?.isEmpty && (
          <div className="absolute top-4 left-4 text-gray-400 pointer-events-none">
            {placeholder}
          </div>
        )}
      </div>
    </div>
  )
}

export default RichTextEditor
