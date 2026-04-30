import React, { useState, useCallback, useRef } from "react";
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
  Trash2
} from 'lucide-react'
import { cn } from '../utils/cn'
import { Progress } from './ui/progress'

interface UploadingFile {
  id: string;
  file: File;
  progress: number;
  status: "pending" | "uploading" | "completed" | "error";
  previewUrl?: string;
  error?: string;
}

interface FileUploadProps {
  onUploadComplete?: (files: File[]) => void;
  maxSize?: number; // in bytes
  allowedTypes?: string[];
}

export function FileUpload({
  onUploadComplete,
  maxSize = 50 * 1024 * 1024, // 50MB default
  allowedTypes = [
    "image/*",
    "application/pdf",
    "text/*",
    "application/zip",
    "application/x-zip-compressed",
  ],
}: FileUploadProps) {
  const [files, setFiles] = useState<UploadingFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateId = () => Math.random().toString(36).substring(7);

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize) {
      return `File is too large. Max size is ${maxSize / (1024 * 1024)}MB.`;
    }

    const isTypeAllowed = allowedTypes.some((type) => {
      if (type.endsWith("/*")) {
        return file.type.startsWith(type.replace("/*", ""));
      }
      return file.type === type;
    });

    if (!isTypeAllowed && allowedTypes.length > 0) {
      return "File type not supported.";
    }

    return null;
  };

  const addFiles = useCallback(
    (newFiles: FileList | File[]) => {
      const filesArray = Array.from(newFiles);

      const mappedFiles: UploadingFile[] = filesArray.map((file) => {
        const error = validateFile(file);
        const previewUrl = file.type.startsWith("image/")
          ? URL.createObjectURL(file)
          : undefined;

        return {
          id: generateId(),
          file,
          progress: 0,
          status: error ? ("error" as const) : ("pending" as const),
          previewUrl,
          error: error || undefined,
        };
      });

      setFiles((prev: UploadingFile[]) => [...prev, ...mappedFiles]);
    },
    [maxSize, allowedTypes, generateId, validateFile],
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      addFiles(e.dataTransfer.files);
    }
  };

  const removeFile = (id: string) => {
    setFiles((prev: UploadingFile[]) => {
      const filtered = prev.filter((f: UploadingFile) => f.id !== id);
      // Cleanup object URL
      const removed = prev.find((f: UploadingFile) => f.id === id);
      if (removed?.previewUrl) URL.revokeObjectURL(removed.previewUrl);
      return filtered;
    });
  };

  const startUpload = async (id: string) => {
    setFiles((prev: UploadingFile[]) =>
      prev.map((f: UploadingFile) =>
        f.id === id ? { ...f, status: "uploading" } : f,
      ),
    );

    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise((resolve) =>
        setTimeout(resolve, 200 + Math.random() * 300),
      );
      setFiles((prev: UploadingFile[]) =>
        prev.map((f: UploadingFile) => (f.id === id ? { ...f, progress } : f)),
      );
    }

    setFiles((prev: UploadingFile[]) =>
      prev.map((f: UploadingFile) =>
        f.id === id ? { ...f, status: "completed", progress: 100 } : f,
      ),
    );
  };

  const uploadAll = async () => {
    const pendingFiles = files.filter(
      (f: UploadingFile) => f.status === "pending",
    );
    await Promise.all(
      pendingFiles.map((f: UploadingFile) => startUpload(f.id)),
    );
    if (onUploadComplete) {
      onUploadComplete(files.map((f: UploadingFile) => f.file));
    }
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) return <ImageIcon className="h-5 w-5" />;
    if (type.startsWith("video/")) return <Film className="h-5 w-5" />;
    if (type.startsWith("audio/")) return <Music className="h-5 w-5" />;
    if (type.includes("pdf") || type.includes("text"))
      return <FileText className="h-5 w-5" />;
    return <File className="h-5 w-5" />;
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="space-y-6 w-full max-w-2xl mx-auto">
      {/* Upload Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          "relative group cursor-pointer border-2 border-dashed rounded-3xl p-12 transition-all duration-300 flex flex-col items-center justify-center gap-4",
          isDragging
            ? "border-primary bg-primary/5 scale-[0.99]"
            : "border-border/60 hover:border-primary/40 hover:bg-accent/20",
          files.length > 0 ? "py-8" : "py-16",
        )}
      >
        <input
          type="file"
          multiple
          className="hidden"
          ref={fileInputRef}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            e.target.files && addFiles(e.target.files)
          }
        />

        <div
          className={cn(
            "w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-inner bg-accent group-hover:scale-110",
            isDragging
              ? "bg-primary text-primary-foreground animate-bounce"
              : "text-primary",
          )}
        >
          <Upload className="h-8 w-8" />
        </div>

        <div className="text-center">
          <p className="text-lg font-bold tracking-tight">
            Drop files here or click to browse
          </p>
          <p className="text-xs text-muted-foreground mt-2 font-medium">
            Supports SQL, PDF, ZIP, and Images (Max 50MB)
          </p>
        </div>

        {isDragging && (
          <div className="absolute inset-2 bg-primary/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border-2 border-primary border-dashed">
            <p className="text-primary font-bold text-lg animate-pulse">
              Release to stack archives
            </p>
          </div>
        )}
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4 animate-in slide-in-from-bottom-2 duration-300">
          <div className="flex items-center justify-between px-2">
            <h4 className="text-sm font-bold text-muted-foreground uppercase tracking-widest leading-relaxed">
              Selected Data ({files.length})
            </h4>
            {files.some((f) => f.status === "pending") && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  uploadAll();
                }}
                className="text-xs font-bold text-primary hover:underline"
              >
                Upload All Selected
              </button>
            )}
          </div>

          <div className="grid gap-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
            {files.map((f) => (
              <div
                key={f.id}
                className={cn(
                  "p-4 rounded-2xl border border-border/50 bg-card/60 backdrop-blur-md transition-all group relative overflow-hidden",
                  f.status === "error"
                    ? "border-rose-500/30 bg-rose-500/5"
                    : "hover:border-primary/20",
                )}
              >
                {/* Progress Indicator */}
                {f.status === 'uploading' && (
                  <Progress 
                    value={f.progress} 
                    className="absolute bottom-0 left-0 h-1 rounded-none bg-primary/10" 
                    indicatorClassName="bg-primary transition-all duration-300"
                  />
                )}

                <div className="flex items-center gap-4 relative z-10">
                  <div className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center shadow-inner overflow-hidden shrink-0">
                    {f.previewUrl ? (
                      <img
                        src={f.previewUrl}
                        alt="Preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      getFileIcon(f.file.type)
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-bold truncate pr-8">
                        {f.file.name}
                      </p>
                      <button
                        onClick={() => removeFile(f.id)}
                        className="p-1.5 hover:bg-accent rounded-lg text-muted-foreground hover:text-rose-500 transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="flex items-center gap-3">
                      <p className="text-[10px] font-bold text-muted-foreground uppercase">
                        {formatSize(f.file.size)}
                      </p>
                      <div className="h-1 w-1 rounded-full bg-border" />
                      {f.status === "pending" && (
                        <span className="text-[10px] font-bold text-primary uppercase">
                          Ready to Archive
                        </span>
                      )}
                      {f.status === "uploading" && (
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-3 w-3 animate-spin text-primary" />
                          <span className="text-[10px] font-bold text-primary uppercase">
                            Archiving... {f.progress}%
                          </span>
                        </div>
                      )}
                      {f.status === "completed" && (
                        <div className="flex items-center gap-1.5 text-emerald-500">
                          <CheckCircle2 className="h-3 w-3" />
                          <span className="text-[10px] font-bold uppercase">
                            Success
                          </span>
                        </div>
                      )}
                      {f.status === "error" && (
                        <div className="flex items-center gap-1.5 text-rose-500">
                          <AlertCircle className="h-3 w-3" />
                          <span className="text-[10px] font-bold uppercase">
                            {f.error || "System Limit Error"}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
