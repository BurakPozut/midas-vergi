'use client';

import { useState } from 'react';
import { deleteFile } from '@/app/actions/delete-file';
import { useSession } from "next-auth/react"

interface UploadProgress {
  [key: string]: {
    progress: number;
    status: 'uploading' | 'completed' | 'error';
  };
}

const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase();

  const iconMap: { [key: string]: JSX.Element } = {
    pdf: (
      <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
    ),
    jpg: (
      <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    png: (
      <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    doc: (
      <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    )
  };

  return iconMap[extension || ''] || (
    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  );
};

export default function FileUploader() {
  const { data: session, status } = useSession()
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({});
  const [isDragging, setIsDragging] = useState(false);

  if (status === "loading") {
    return <div>Loading...</div>
  }

  if (!session) {
    return <div>Please sign in to upload files</div>
  }

  const handleFileUpload = async (files: FileList | null) => {
    if (files && files.length > 0) {
      const formData = new FormData();

      Array.from(files).forEach((file) => {
        formData.append('files', file);
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: {
            progress: 0,
            status: 'uploading'
          }
        }));
      });

      const xhr = new XMLHttpRequest();
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          Array.from(files).forEach((file) => {
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: {
                progress,
                status: 'uploading'
              }
            }));
          });
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          Array.from(files).forEach((file) => {
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: {
                progress: 100,
                status: 'completed'
              }
            }));
          });
        } else {
          Array.from(files).forEach((file) => {
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: {
                progress: 0,
                status: 'error'
              }
            }));
          });
        }
      };

      xhr.onerror = () => {
        Array.from(files).forEach((file) => {
          setUploadProgress(prev => ({
            ...prev,
            [file.name]: {
              progress: 0,
              status: 'error'
            }
          }));
        });
      };

      xhr.open('POST', '/api/upload');
      xhr.send(formData);
    }
  };

  const removeFile = async (fileName: string) => {
    const result = await deleteFile(fileName);
    if (result.success) {
      setUploadProgress(prev => {
        const newState = { ...prev };
        delete newState[fileName];
        return newState;
      });
    } else {
      console.error('Dosya silinirken hata oluştu');
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileUpload(e.target.files);
  };

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <label
          htmlFor="file-upload"
          className={`flex justify-center w-full h-16 px-4 transition-all duration-300 bg-navy-800 border-2 
            ${isDragging ? 'border-blue-500 scale-105' : 'border-gray-600'} 
            border-dashed rounded-lg appearance-none cursor-pointer hover:border-gray-500 focus:outline-none items-center`}
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(true);
          }}
          onDragEnter={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(true);
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(false);
          }}
          onDrop={handleDrop}
        >
          <span className="flex items-center gap-2">
            <svg className={`w-4 h-4 text-gray-400 transition-transform duration-300 ${isDragging ? 'scale-110' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="font-medium text-gray-400 text-xs">
              Dosyaları sürükleyin veya yüklemek için tıklayın
            </span>
          </span>
          <input
            id="file-upload"
            type="file"
            className="hidden"
            onChange={handleInputChange}
            multiple
          />
        </label>
      </div>

      <div className="space-y-4">
        {Object.entries(uploadProgress).map(([fileName, { progress, status }]) => (
          <div
            key={fileName}
            className="bg-gray-700 p-4 rounded-lg transform transition-all duration-300 hover:scale-[1.02]"
          >
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center space-x-3">
                {getFileIcon(fileName)}
                <span className="text-sm text-gray-300">{fileName}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-sm font-medium ${status === 'error' ? 'text-red-400' :
                  status === 'completed' ? 'text-green-400' :
                    'text-blue-400'
                  }`}>
                  {status === 'error' ? 'Hata' :
                    status === 'completed' ? 'Tamamlandı' :
                      `${Math.round(progress)}%`}
                </span>
                {status === 'completed' && (
                  <button
                    onClick={() => removeFile(fileName)}
                    className="text-gray-400 hover:text-red-400 transition-colors"
                    title="Dosyayı Sil"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
            <div className="w-full bg-gray-600 rounded-full h-2 overflow-hidden">
              <div
                className="h-2 rounded-full transition-all duration-300 ease-out"
                style={{
                  width: `${progress}%`,
                  background: status === 'error' ? 'rgb(239, 68, 68)' :
                    status === 'completed' ? 'rgb(34, 197, 94)' :
                      'linear-gradient(90deg, #3B82F6 0%, #60A5FA 100%)',
                  boxShadow: progress > 0 ? '0 0 10px rgba(59, 130, 246, 0.7)' : 'none'
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 