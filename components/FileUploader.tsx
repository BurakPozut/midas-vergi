'use client';

import { useState } from 'react';
import { useSession } from "next-auth/react"

type UploadStatus = 'uploading' | 'completed' | 'error' | 'selected';

interface UploadProgress {
  [key: string]: {
    progress: number;
    status: UploadStatus;
  };
}

interface TaxResults {
  profit_loss_by_symbol: { [key: string]: number };
  total_profit: number;
  total_loss: number;
  total_profit_loss: number;
  total_profit_loss_after_commissions: number;
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
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [showUploadButton, setShowUploadButton] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [taxResults, setTaxResults] = useState<TaxResults | null>(null);

  if (status === "loading") {
    return <div>Loading...</div>
  }

  if (!session) {
    return <div>Please sign in to upload files</div>
  }

  const calculateTax = async () => {
    setIsCalculating(true);
    try {
      const response = await fetch('/api/calculate-tax', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to calculate tax');
      }

      const results = await response.json();
      setTaxResults(results);
    } catch (error) {
      console.error('Error calculating tax:', error);
      alert('Vergi hesaplanırken bir hata oluştu.');
    } finally {
      setIsCalculating(false);
    }
  };

  const handleFileSelection = (files: FileList | null) => {
    if (files && files.length > 0) {
      const newFiles = Array.from(files).filter(file => file.type === 'application/pdf');
      setSelectedFiles(prev => [...prev, ...newFiles]);

      newFiles.forEach(file => {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: {
            progress: 0,
            status: 'selected' as UploadStatus
          }
        }));
      });

      setShowUploadButton(true);
    }
  };

  const removeSelectedFile = (fileName: string) => {
    setSelectedFiles(prev => prev.filter(f => f.name !== fileName));
    setUploadProgress(prev => {
      const newState = { ...prev };
      delete newState[fileName];
      return newState;
    });
    if (selectedFiles.length <= 1) {
      setShowUploadButton(false);
    }
  };

  const uploadFiles = async () => {
    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
      // Initialize progress for each file
      setUploadProgress(prev => ({
        ...prev,
        [file.name]: {
          progress: 0,
          status: 'uploading'
        }
      }));
    });

    try {
      const xhr = new XMLHttpRequest();

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const totalProgress = (event.loaded / event.total) * 100;
          // Update progress for all files
          selectedFiles.forEach(file => {
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: {
                progress: totalProgress,
                status: 'uploading'
              }
            }));
          });
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          // Mark all files as completed
          selectedFiles.forEach(file => {
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: {
                progress: 100,
                status: 'completed'
              }
            }));
          });
        } else {
          // Mark all files as error
          selectedFiles.forEach(file => {
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
        // Mark all files as error on network failure
        selectedFiles.forEach(file => {
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
      await new Promise((resolve) => xhr.onloadend = resolve);
    } catch (error) {
      console.error('Error uploading files:', error);
      // Mark all files as error on exception
      selectedFiles.forEach(file => {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: {
            progress: 0,
            status: 'error'
          }
        }));
      });
    }

    setSelectedFiles([]);
    setShowUploadButton(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    handleFileSelection(e.dataTransfer.files);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelection(e.target.files);
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
            accept=".pdf"
          />
        </label>
      </div>

      {showUploadButton && (
        <button
          onClick={uploadFiles}
          className="w-full py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors mb-4"
        >
          Dosyaları Yükle
        </button>
      )}

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
                    status === 'uploading' ? 'text-blue-400' :
                      'text-gray-400'
                  }`}>
                  {status === 'error' ? 'Hata' :
                    status === 'completed' ? 'Tamamlandı' :
                      status === 'uploading' ? `${Math.round(progress)}%` :
                        'Seçildi'}
                </span>
                {(status === 'completed' || status === 'selected') && (
                  <button
                    onClick={() => removeSelectedFile(fileName)}
                    className="text-gray-400 hover:text-red-400 transition-colors"
                    title="Dosyayı Kaldır"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
            {status !== 'selected' && (
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
            )}
          </div>
        ))}
      </div>

      {Object.entries(uploadProgress).length > 0 &&
        Object.entries(uploadProgress).every(([, { status }]) => status === 'completed') && (
          <div className="mt-6">
            <button
              onClick={calculateTax}
              disabled={isCalculating}
              className={`w-full py-2 px-4 bg-green-500 text-white rounded-lg transition-colors ${isCalculating ? 'opacity-50 cursor-not-allowed' : 'hover:bg-green-600'
                }`}
            >
              {isCalculating ? 'Vergi Hesaplanıyor...' : 'Vergi Hesapla'}
            </button>
          </div>
        )}

      {taxResults && (
        <div className="mt-6 bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">Vergi Hesaplama Sonuçları</h3>

          <div className="space-y-2">
            <h4 className="text-md font-medium text-gray-300">Sembol Bazında Kar/Zarar:</h4>
            {Object.entries(taxResults.profit_loss_by_symbol).map(([symbol, profit]) => (
              <div key={symbol} className="flex justify-between text-sm">
                <span className="text-gray-400">{symbol}:</span>
                <span className={`${Number(profit) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {Number(profit).toFixed(2)} TRY
                </span>
              </div>
            ))}
          </div>

          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Toplam Kar:</span>
              <span className="text-green-400">{taxResults.total_profit.toFixed(2)} TRY</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Toplam Zarar:</span>
              <span className="text-red-400">{taxResults.total_loss.toFixed(2)} TRY</span>
            </div>
            <div className="flex justify-between text-sm font-medium">
              <span className="text-gray-300">Toplam Kar/Zarar:</span>
              <span className={`${taxResults.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {taxResults.total_profit_loss.toFixed(2)} TRY
              </span>
            </div>
            <div className="flex justify-between text-sm font-medium pt-2 border-t border-gray-600">
              <span className="text-gray-300">Komisyonlar Sonrası Kar/Zarar:</span>
              <span className={`${taxResults.total_profit_loss_after_commissions >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {taxResults.total_profit_loss_after_commissions.toFixed(2)} TRY
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 