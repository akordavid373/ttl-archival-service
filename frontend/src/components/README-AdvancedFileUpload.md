# Advanced File Upload Component

A comprehensive, feature-rich file upload component built with React and TypeScript that provides drag-and-drop functionality, progress tracking, file validation, and image previews.

## Features

✅ **Drag & Drop Interface** - Intuitive drag-and-drop with visual feedback
✅ **Multiple File Selection** - Upload multiple files simultaneously  
✅ **File Type Validation** - Configurable allowed file types
✅ **File Size Validation** - Customizable maximum file size limits
✅ **Upload Progress Tracking** - Real-time progress with speed and time estimates
✅ **Image Preview** - Thumbnail previews for image files
✅ **Pause/Resume Uploads** - Control upload flow with pause and resume
✅ **Retry Failed Uploads** - Easy retry mechanism for failed uploads
✅ **Batch Operations** - Upload all, clear all, retry failed operations
✅ **Responsive Design** - Mobile-friendly interface with Tailwind CSS
✅ **Accessibility** - Proper ARIA labels and keyboard navigation

## Installation

The component uses the following dependencies which should already be installed in your project:

```bash
npm install lucide-react class-variance-authority clsx tailwind-merge
```

## Usage

### Basic Usage

```tsx
import { AdvancedFileUpload } from './components/AdvancedFileUpload'

function MyComponent() {
  const handleUploadComplete = (files: File[]) => {
    console.log('All files uploaded:', files)
  }

  return (
    <AdvancedFileUpload
      onUploadComplete={handleUploadComplete}
      maxSize={50 * 1024 * 1024} // 50MB
      maxFiles={10}
    />
  )
}
```

### Advanced Configuration

```tsx
import { AdvancedFileUpload } from './components/AdvancedFileUpload'

function MyComponent() {
  const handleUploadComplete = (files: File[]) => {
    // Handle successful uploads
  }

  const handleFileSelect = (files: File[]) => {
    // Handle file selection before upload
  }

  const handleProgress = (fileId: string, progress: number) => {
    // Track individual file progress
  }

  return (
    <AdvancedFileUpload
      onUploadComplete={handleUploadComplete}
      onFileSelect={handleFileSelect}
      onProgress={handleProgress}
      maxSize={100 * 1024 * 1024} // 100MB
      maxFiles={20}
      allowedTypes={[
        'image/*',
        'application/pdf',
        'text/*',
        'application/zip',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ]}
      autoUpload={false}
      showPreview={true}
      disabled={false}
      className="custom-upload-class"
    />
  )
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onUploadComplete` | `(files: File[]) => void` | - | Callback when all files are uploaded |
| `onFileSelect` | `(files: File[]) => void` | - | Callback when files are selected |
| `onProgress` | `(fileId: string, progress: number) => void` | - | Callback for individual file progress |
| `maxSize` | `number` | `50 * 1024 * 1024` (50MB) | Maximum file size in bytes |
| `maxFiles` | `number` | `10` | Maximum number of files |
| `allowedTypes` | `string[]` | See below | Allowed file types |
| `disabled` | `boolean` | `false` | Disable the upload component |
| `autoUpload` | `boolean` | `false` | Automatically start upload on file selection |
| `showPreview` | `boolean` | `true` | Show image previews |
| `className` | `string` | `''` | Additional CSS classes |

### Default Allowed Types

```typescript
const defaultAllowedTypes = [
  'image/*',
  'application/pdf',
  'text/*',
  'application/zip',
  'application/x-zip-compressed',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]
```

## File Status States

Each uploaded file can have one of the following states:

- **`pending`** - File selected, ready to upload
- **`uploading`** - File is currently being uploaded
- **`paused`** - Upload is paused
- **`completed`** - Upload finished successfully
- **`error`** - Upload failed with an error

## Upload Flow

1. **File Selection**: Users can drag & drop files or click to browse
2. **Validation**: Files are validated for type and size
3. **Queue**: Valid files are added to the upload queue
4. **Upload**: Files are uploaded individually with progress tracking
5. **Completion**: Callback is fired when all files are processed

## Customization

### Styling

The component uses Tailwind CSS classes and can be customized through the `className` prop:

```tsx
<AdvancedFileUpload
  className="border-2 border-blue-500 rounded-lg"
  // ... other props
/>
```

### File Type Icons

The component automatically displays appropriate icons based on file types:
- Images: 🖼️ (ImageIcon)
- Videos: 🎬 (Film icon)
- Audio: 🎵 (Music icon)
- Documents: 📄 (FileText icon)
- Default: 📁 (File icon)

## Error Handling

The component provides comprehensive error handling:

### File Size Errors
```typescript
// Example error message
"File is too large. Max size is 50MB."
```

### File Type Errors
```typescript
// Example error message
'File type "application/exe" not supported. Allowed types: image/*, application/pdf, text/*'
```

### Upload Errors
```typescript
// Example error message
"Upload failed"
```

## Progress Tracking

The component provides detailed progress information:

```typescript
interface UploadingFile {
  id: string
  file: File
  progress: number // 0-100
  status: 'pending' | 'uploading' | 'completed' | 'error' | 'paused'
  previewUrl?: string
  error?: string
  uploadSpeed?: number // bytes per second
  timeRemaining?: number // seconds remaining
}
```

## Accessibility

The component includes proper ARIA labels and keyboard navigation:

- Screen reader support for file status
- Keyboard navigation for all interactive elements
- Focus management for drag-and-drop zone
- High contrast support

## Browser Support

The component supports all modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Testing

The component includes comprehensive tests covering:

- File selection and validation
- Drag and drop functionality
- Progress tracking
- Error handling
- Accessibility features

Run tests with:
```bash
npm test AdvancedFileUpload
```

## Performance Considerations

- **Memory Management**: Object URLs for image previews are automatically cleaned up
- **Large Files**: Chunked upload simulation prevents memory issues
- **Concurrent Uploads**: Multiple files can upload simultaneously
- **Cancellation**: Uploads can be cancelled to free resources

## Security Notes

- File validation is performed on the client side
- Always validate files on the server side as well
- Object URLs are revoked after use to prevent memory leaks
- No file content is read unless necessary for preview

## Examples

### Image Gallery Upload
```tsx
<AdvancedFileUpload
  allowedTypes={['image/*']}
  maxSize={10 * 1024 * 1024} // 10MB
  maxFiles={50}
  autoUpload={true}
  showPreview={true}
  onUploadComplete={(files) => {
    // Process uploaded images
  }}
/>
```

### Document Upload
```tsx
<AdvancedFileUpload
  allowedTypes={[
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/*'
  ]}
  maxSize={20 * 1024 * 1024} // 20MB
  maxFiles={5}
  showPreview={false}
/>
```

### Multi-File Archive Upload
```tsx
<AdvancedFileUpload
  allowedTypes={[
    'application/zip',
    'application/x-zip-compressed',
    'application/x-rar-compressed',
    'application/x-7z-compressed'
  ]}
  maxSize={500 * 1024 * 1024} // 500MB
  maxFiles={3}
/>
```

## Troubleshooting

### Common Issues

1. **Files not uploading**: Check `autoUpload` prop and ensure `onUploadComplete` is set
2. **Large files failing**: Increase `maxSize` limit or check file size
3. **Type errors**: Verify `allowedTypes` array includes the file types
4. **Preview not showing**: Ensure `showPreview` is true and files are images

### Debug Mode

Enable console logging by checking browser dev tools for:
- File selection events
- Upload progress updates
- Validation errors
- Completion callbacks

## Contributing

When contributing to the component:

1. Follow TypeScript best practices
2. Add appropriate tests for new features
3. Update documentation for API changes
4. Ensure accessibility compliance
5. Test with various file types and sizes

## License

This component is part of the TTL-Aware Automated Archival Service project.
