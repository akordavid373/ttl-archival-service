import { useState } from 'react'
import { RichTextEditor } from '../components/RichTextEditor'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Upload, Save, FileText, Image, Code, Table } from 'lucide-react'

export function RichTextEditorDemo() {
  const [content, setContent] = useState('<h1>Welcome to the Rich Text Editor Demo</h1><p>This is a feature-rich text editor with comprehensive formatting options and media support.</p><h2>Key Features</h2><ul><li><strong>Rich Formatting</strong>: Bold, italic, underline, strikethrough, and more</li><li><strong>Media Support</strong>: Images, videos, and audio embedding</li><li><strong>Code Highlighting</strong>: Syntax highlighting for multiple languages</li><li><strong>Auto-Save</strong>: Automatic saving with visual feedback</li><li><strong>Accessibility</strong>: Full keyboard navigation and screen reader support</li></ul><h3>Try It Out!</h3><p>Start editing this content to see all the features in action. You can:</p><ul><li>Format text using the toolbar buttons</li><li>Add links, images, and tables</li><li>Insert code blocks with syntax highlighting</li><li>Use keyboard shortcuts for common actions</li></ul><blockquote><p>This editor is built with TipTap and provides a modern, extensible editing experience.</p></blockquote>')
  const [savedContent, setSavedContent] = useState(content)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [uploadProgress, setUploadProgress] = useState(0)

  // Mock media upload function
  const handleMediaUpload = async (file: File): Promise<string> => {
    // Simulate upload progress
    for (let i = 0; i <= 100; i += 10) {
      setUploadProgress(i)
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    // Return a mock URL (in real app, this would be the uploaded file URL)
    return URL.createObjectURL(file)
  }

  // Mock save function
  const handleSave = async (editorContent: string) => {
    setSaveStatus('saving')
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSavedContent(editorContent)
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
    } catch (error) {
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 2000)
    }
  }

  const handleContentChange = (newContent: string, _plainText?: string) => {
    setContent(newContent)
  }

  const getCharacterCount = () => {
    const temp = document.createElement('div')
    temp.innerHTML = content
    return temp.textContent?.length || 0
  }

  const getWordCount = () => {
    const temp = document.createElement('div')
    temp.innerHTML = content
    const text = temp.textContent || ''
    return text.trim().split(/\s+/).filter(word => word.length > 0).length
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">Rich Text Editor Demo</h1>
          <p className="text-lg text-gray-600">
            Feature-rich WYSIWYG editor with formatting, media support, and auto-save
          </p>
          <div className="flex justify-center gap-2 flex-wrap">
            <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">WYSIWYG</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">Media Support</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">Code Highlighting</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">Auto-Save</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">Accessible</span>
          </div>
        </div>

        {/* Main Editor */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Rich Text Editor
                </CardTitle>
                <CardDescription>
                  Start typing to see the rich formatting options in action
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  saveStatus === 'saved' ? 'bg-green-100 text-green-800' : 
                  saveStatus === 'saving' ? 'bg-blue-100 text-blue-800' : 
                  saveStatus === 'error' ? 'bg-red-100 text-red-800' : 
                  'bg-gray-100 text-gray-800'
                }`}>
                  {saveStatus === 'idle' && 'Ready'}
                  {saveStatus === 'saving' && 'Saving...'}
                  {saveStatus === 'saved' && 'Saved'}
                  {saveStatus === 'error' && 'Error'}
                </span>
                {uploadProgress > 0 && uploadProgress < 100 && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">Upload: {uploadProgress}%</span>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <RichTextEditor
              content={content}
              onChange={handleContentChange}
              onSave={handleSave}
              enableMediaUpload={true}
              onMediaUpload={handleMediaUpload}
              showCharacterCount={true}
              autoSave={true}
              autoSaveDelay={3000}
              maxLength={10000}
              placeholder="Start typing your content here..."
              className="border-0 shadow-sm"
            />
          </CardContent>
        </Card>

        {/* Feature Cards */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold text-gray-900">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Rich Formatting
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Bold, italic, underline, strikethrough, headings, lists, quotes, and more formatting options.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Image className="h-5 w-5" />
                  Media Support
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Upload and embed images, videos, and audio files with progress tracking.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Table className="h-5 w-5" />
                  Tables & Links
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Create resizable tables and insert links with automatic URL detection.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Save className="h-5 w-5" />
                  Auto-Save
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Automatic saving with visual feedback and manual save options.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  File Upload
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Drag-and-drop file upload with progress indicators and error handling.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Accessibility</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Full keyboard navigation, screen reader support, and ARIA labels.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Document Statistics</CardTitle>
            <CardDescription>
              Real-time statistics about your content
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{getCharacterCount()}</div>
                <div className="text-sm text-gray-600">Characters</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{getWordCount()}</div>
                <div className="text-sm text-gray-600">Words</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{content.split('\n').length}</div>
                <div className="text-sm text-gray-600">Lines</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{(content.match(/<[^>]+>/g) || []).length}</div>
                <div className="text-sm text-gray-600">HTML Tags</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Reference */}
        <Card>
          <CardHeader>
            <CardTitle>API Reference</CardTitle>
            <CardDescription>
              Key props and methods for the Rich Text Editor component
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Main Props</h4>
                <div className="bg-gray-50 p-4 rounded-lg text-sm font-mono">
                  <div>content: string</div>
                  <div>onChange: (content: string, plainText?: string) =&gt; void</div>
                  <div>onSave: (content: string) =&gt; Promise&lt;void&gt;</div>
                  <div>enableMediaUpload: boolean</div>
                  <div>onMediaUpload: (file: File) =&gt; Promise&lt;string&gt;</div>
                  <div>autoSave: boolean</div>
                  <div>showCharacterCount: boolean</div>
                  <div>maxLength: number</div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Usage Example</h4>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto">
{`<RichTextEditor
  content={content}
  onChange={setContent}
  onSave={handleSave}
  enableMediaUpload={true}
  onMediaUpload={uploadFile}
  autoSave={true}
  showCharacterCount={true}
/>`}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default RichTextEditorDemo
