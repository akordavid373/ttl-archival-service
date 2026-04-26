import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AdvancedFileUpload } from './AdvancedFileUpload'

describe('AdvancedFileUpload', () => {
  const mockOnUploadComplete = jest.fn()
  const mockOnFileSelect = jest.fn()
  const mockOnProgress = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders upload zone', () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
      />
    )

    expect(screen.getByText(/Drop files here or click to browse/)).toBeInTheDocument()
    expect(screen.getByText(/Supports/)).toBeInTheDocument()
  })

  it('handles file selection via click', async () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
      />
    )

    const fileInput = screen.getByRole('button').querySelector('input[type="file"]')
    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    
    fireEvent.change(fileInput!, { target: { files: [file] } })

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith([file])
    })
  })

  it('validates file size', async () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
        maxSize={100} // Very small size for testing
      />
    )

    const fileInput = screen.getByRole('button').querySelector('input[type="file"]')
    const largeFile = new File(['test content'], 'large.txt', { type: 'text/plain' })
    Object.defineProperty(largeFile, 'size', { value: 200 })
    
    fireEvent.change(fileInput!, { target: { files: [largeFile] } })

    await waitFor(() => {
      expect(screen.getByText(/File is too large/)).toBeInTheDocument()
    })
  })

  it('validates file type', async () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
        allowedTypes={['image/*']}
      />
    )

    const fileInput = screen.getByRole('button').querySelector('input[type="file"]')
    const textFile = new File(['test'], 'test.txt', { type: 'text/plain' })
    
    fireEvent.change(fileInput!, { target: { files: [textFile] } })

    await waitFor(() => {
      expect(screen.getByText(/File type.*not supported/)).toBeInTheDocument()
    })
  })

  it('shows drag over state', () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
      />
    )

    const uploadZone = screen.getByText(/Drop files here/).closest('div')
    
    fireEvent.dragOver(uploadZone!)
    
    expect(uploadZone).toHaveClass('border-primary')
  })

  it('handles file drop', async () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
      />
    )

    const uploadZone = screen.getByText(/Drop files here/).closest('div')
    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    
    fireEvent.drop(uploadZone!, {
      dataTransfer: { files: [file] }
    })

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith([file])
    })
  })

  it('limits maximum number of files', async () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
        maxFiles={2}
      />
    )

    const fileInput = screen.getByRole('button').querySelector('input[type="file"]')
    const files = [
      new File(['test1'], 'test1.txt', { type: 'text/plain' }),
      new File(['test2'], 'test2.txt', { type: 'text/plain' }),
      new File(['test3'], 'test3.txt', { type: 'text/plain' })
    ]
    
    fireEvent.change(fileInput!, { target: { files } })

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(files.slice(0, 2))
    })
  })

  it('disables component when disabled prop is true', () => {
    render(
      <AdvancedFileUpload
        onUploadComplete={mockOnUploadComplete}
        onFileSelect={mockOnFileSelect}
        onProgress={mockOnProgress}
        disabled={true}
      />
    )

    const uploadZone = screen.getByText(/Drop files here/).closest('div')
    expect(uploadZone).toHaveClass('opacity-50')
    expect(uploadZone).toHaveClass('cursor-not-allowed')
  })
})
