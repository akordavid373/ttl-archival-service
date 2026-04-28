import { useState } from 'react'
import { AdvancedFileUpload } from '../components/AdvancedFileUpload'
import { FileUpload } from '../components/FileUpload'

export default function FileUploadDemo() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])

  const handleUploadComplete = (files: File[]) => {
    setUploadedFiles(prev => [...prev, ...files])
    console.log('Upload completed:', files)
  }

  const handleFileSelect = (files: File[]) => {
    console.log('Files selected:', files)
  }

  const handleProgress = (fileId: string, progress: number) => {
    console.log(`File ${fileId} progress: ${progress}%`)
  }

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return '🖼️'
    if (type.startsWith('video/')) return '🎬'
    if (type.startsWith('audio/')) return '🎵'
    return '📄'
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-slate-900">Advanced File Upload Components</h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Comprehensive file upload solutions with drag-and-drop, progress tracking, validation, and preview functionality.
          </p>
        </div>

        {/* Features Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <span className="text-blue-600">📤</span>
              </div>
              <h3 className="font-semibold">Drag & Drop</h3>
            </div>
            <p className="text-sm text-slate-600">
              Intuitive drag-and-drop interface with visual feedback and multiple file selection support.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                <span className="text-green-600">✅</span>
              </div>
              <h3 className="font-semibold">Smart Validation</h3>
            </div>
            <p className="text-sm text-slate-600">
              File type and size validation with customizable rules and clear error messages.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <span className="text-purple-600">🖼️</span>
              </div>
              <h3 className="font-semibold">Rich Previews</h3>
            </div>
            <p className="text-sm text-slate-600">
              Image previews, file icons, and detailed information for each uploaded file.
            </p>
          </div>
        </div>

        {/* Upload Components */}
        <div className="space-y-8">
          {/* Advanced Upload Component */}
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Advanced File Upload Component</h2>
              <p className="text-slate-600 mt-1">
                Full-featured upload component with pause/resume, retry, progress tracking, and batch operations.
              </p>
            </div>
            <div className="p-6">
              <AdvancedFileUpload
                onUploadComplete={handleUploadComplete}
                onFileSelect={handleFileSelect}
                onProgress={handleProgress}
                maxSize={100 * 1024 * 1024} // 100MB
                maxFiles={20}
                autoUpload={false}
                showPreview={true}
              />
            </div>
          </div>

          {/* Standard Upload Component */}
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Standard File Upload Component</h2>
              <p className="text-slate-600 mt-1">
                Clean and simple upload component with essential features.
              </p>
            </div>
            <div className="p-6">
              <FileUpload
                onUploadComplete={handleUploadComplete}
                maxSize={50 * 1024 * 1024} // 50MB
              />
            </div>
          </div>
        </div>

        {/* Upload History */}
        {uploadedFiles.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold flex items-center justify-between">
                Upload History
                <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded text-sm">
                  {uploadedFiles.length} files
                </span>
              </h2>
              <p className="text-slate-600 mt-1">
                Recently uploaded files
              </p>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg">
                    <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center shadow-sm">
                      <span>{getFileIcon(file.type)}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{file.name}</p>
                      <p className="text-sm text-slate-500">{formatSize(file.size)}</p>
                    </div>
                    <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm flex items-center gap-1">
                      ✅ Uploaded
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t">
                <button 
                  onClick={() => setUploadedFiles([])}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Clear History
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Configuration Options */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Configuration Options</h2>
            <p className="text-slate-600 mt-1">
              Available props and customization options for the upload components
            </p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3">Advanced Upload Component</h4>
                <ul className="space-y-2 text-sm">
                  <li className="flex justify-between">
                    <span className="text-slate-600">Max File Size:</span>
                    <span className="bg-slate-100 px-2 py-1 rounded text-xs">100MB</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-slate-600">Max Files:</span>
                    <span className="bg-slate-100 px-2 py-1 rounded text-xs">20</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-slate-600">Auto Upload:</span>
                    <span className="bg-slate-100 px-2 py-1 rounded text-xs">Disabled</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-slate-600">Image Preview:</span>
                    <span className="bg-slate-100 px-2 py-1 rounded text-xs">Enabled</span>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Supported File Types</h4>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-slate-100 px-2 py-1 rounded text-xs">Images</span>
                  <span className="bg-slate-100 px-2 py-1 rounded text-xs">PDF</span>
                  <span className="bg-slate-100 px-2 py-1 rounded text-xs">Text</span>
                  <span className="bg-slate-100 px-2 py-1 rounded text-xs">ZIP</span>
                  <span className="bg-slate-100 px-2 py-1 rounded text-xs">Word</span>
                  <span className="bg-slate-100 px-2 py-1 rounded text-xs">And more...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
