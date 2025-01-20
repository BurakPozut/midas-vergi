'use client';

import { useState } from 'react';
import { useSession } from "next-auth/react"
import { MissingTransactionsAlert } from './MissingTransactionsAlert';

type UploadStatus = 'uploading' | 'processing' | 'completed' | 'error' | 'selected';

interface UploadProgress {
  [key: string]: {
    progress: number;
    status: UploadStatus;
    processingMessage?: string;
  };
}

interface TaxResults {
  profit_loss_by_symbol: { [key: string]: number };
  total_profit: number;
  total_loss: number;
  total_profit_loss: number;
  total_profit_loss_after_commissions: number;
  missingBuyTransactions?: string[];
  dividend_summary: {
    dividends_by_symbol: { [key: string]: number };
    total_gross_amount: number;
    total_tax_withheld: number;
    total_net_amount: number;
  };
}

const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase();

  const iconMap: { [key: string]: JSX.Element } = {
    pdf: (
      <svg className="w-16 h-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  );
};

export default function FileUploader() {
  const { data: session, status } = useSession()
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({});
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);
  const [taxResults, setTaxResults] = useState<TaxResults | null>(null);
  const [showMissingAlert, setShowMissingAlert] = useState(false);
  const [missingSymbols, setMissingSymbols] = useState<string[]>([]);
  const [isResetting, setIsResetting] = useState(false);

  if (status === "loading") {
    return <div>Yükleniyor...</div>
  }

  if (!session) {
    return <div>Dosya yüklemek için lütfen giriş yapın</div>
  }

  const resetUploader = async () => {
    setIsResetting(true);
    try {
      // Call the reset API endpoint
      const response = await fetch('/api/reset-data', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to reset data');
      }

      // Reset all state
      setUploadProgress({});
      setSelectedFiles([]);
      setIsCalculating(false);
      setTaxResults(null);
      setShowMissingAlert(false);
      setMissingSymbols([]);
    } catch (error) {
      console.error('Error resetting data:', error);
      alert('Veriler sıfırlanırken bir hata oluştu.');
    } finally {
      setIsResetting(false);
    }
  };

  const calculateTax = async () => {
    setIsCalculating(true);
    setSelectedFiles([]);
    try {
      const response = await fetch('/api/calculate-tax', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to calculate tax');
      }

      const results = await response.json();

      // Check for missing buy transactions
      if (results.missingBuyTransactions && results.missingBuyTransactions.length > 0) {
        setMissingSymbols(results.missingBuyTransactions);
        setShowMissingAlert(true);
      }

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
    }
  };

  const uploadFiles = async () => {
    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
      setUploadProgress(prev => ({
        ...prev,
        [file.name]: {
          progress: 0,
          status: 'uploading'
        }
      }));
    });

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Failed to get response reader');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const events = text.split('\n\n').filter(Boolean);

        for (const event of events) {
          if (!event.startsWith('data: ')) continue;
          const data = JSON.parse(event.slice(6));

          switch (data.type) {
            case 'status':
              if (data.status === 'processing_start') {
                setUploadProgress(prev => ({
                  ...prev,
                  [data.file]: {
                    ...prev[data.file],
                    status: 'processing',
                    processingMessage: 'İşlem başlatıldı...'
                  }
                }));
              } else if (data.status === 'processing_complete') {
                setUploadProgress(prev => ({
                  ...prev,
                  [data.file]: {
                    ...prev[data.file],
                    progress: 100,
                    status: 'completed',
                    processingMessage: 'İşlem tamamlandı'
                  }
                }));
              }
              break;
            case 'processing_progress':
              setUploadProgress(prev => ({
                ...prev,
                [data.file]: {
                  ...prev[data.file],
                  processingMessage: data.data
                }
              }));
              break;
            case 'error':
              setUploadProgress(prev => ({
                ...prev,
                [data.file]: {
                  ...prev[data.file],
                  status: 'error',
                  processingMessage: data.error
                }
              }));
              break;
            case 'complete':
              // All files processed
              break;
          }
        }
      }
    } catch (error) {
      console.error('Error uploading files:', error);
      selectedFiles.forEach(file => {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: {
            progress: 0,
            status: 'error',
            processingMessage: 'Upload failed'
          }
        }));
      });
    }

    setSelectedFiles([]);
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

  const renderProgress = (fileName: string) => {
    const progress = uploadProgress[fileName];
    if (!progress) return null;

    const getStatusColor = () => {
      switch (progress.status) {
        case 'uploading': return 'bg-blue-500';
        case 'processing': return 'bg-yellow-500';
        case 'completed': return 'bg-green-500';
        case 'error': return 'bg-red-500';
        default: return 'bg-gray-500';
      }
    };

    const getStatusText = () => {
      switch (progress.status) {
        case 'uploading': return 'Yükleniyor';
        case 'processing': return 'İşleniyor';
        case 'completed': return 'Tamamlandı';
        case 'error': return 'Hata';
        default: return 'Hazır';
      }
    };

    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-gray-400">
            {getStatusText()}
          </span>
          <span className="text-xs text-gray-400">
            {progress.progress.toFixed(0)}%
          </span>
        </div>
        <div className="w-full h-2 bg-navy-600 rounded-full overflow-hidden">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${getStatusColor()}`}
            style={{ width: `${progress.progress}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {isResetting && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="animate-pulse flex space-x-4 items-center bg-navy-800 rounded-lg p-4">
            <div className="h-3 w-3 bg-blue-400 rounded-full"></div>
            <div className="text-sm text-gray-400">Veriler sıfırlanıyor...</div>
          </div>
        </div>
      )}
      {!isCalculating && (
        <>
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
              <span className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className="font-medium text-gray-600">
                  Dosyaları sürükleyin veya seçmek için tıklayın
                </span>
              </span>
            </label>
            <input
              type="file"
              id="file-upload"
              name="file-upload"
              className="sr-only"
              onChange={handleInputChange}
              multiple
              accept=".pdf"
            />
          </div>

          {selectedFiles.length > 0 && (
            <div className="flex justify-end mb-6">
              <button
                onClick={uploadFiles}
                className="px-8 py-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
              >
                Dosyaları Yükle
              </button>
            </div>
          )}
        </>
      )}

      {Object.keys(uploadProgress).length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(uploadProgress).map(([fileName, progress]) => (
            <div key={fileName} className="relative flex flex-col bg-navy-700 rounded-lg overflow-hidden shadow-lg">
              <div className="p-6 flex flex-col items-center">
                <div className="mb-4">
                  {getFileIcon(fileName)}
                </div>
                <span className="text-sm font-medium text-gray-200 text-center truncate w-full px-4">
                  {fileName}
                </span>
              </div>

              <div className="p-4 bg-navy-800">
                <div className="space-y-2">
                  {renderProgress(fileName)}
                </div>
                {progress?.processingMessage && (
                  <div className="text-xs text-gray-400 mt-2 max-h-16 overflow-y-auto">
                    {progress.processingMessage}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

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

      {isCalculating && (
        <div className="mt-4">
          <div className="animate-pulse flex space-x-4 items-center">
            <div className="h-3 w-3 bg-blue-400 rounded-full"></div>
            <div className="text-sm text-gray-400">Vergi hesaplanıyor...</div>
          </div>
        </div>
      )}

      {taxResults && (
        <div className="mt-4 space-y-4 bg-navy-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">Vergi Hesaplama Sonuçları</h3>

          {/* Trading Results Section */}
          <div className="space-y-4">
            <h4 className="text-md font-medium text-gray-300">Alım-Satım İşlemleri:</h4>

            <div className="space-y-2">
              <h5 className="text-sm font-medium text-gray-400">Sembol Bazında Kar/Zarar:</h5>
              {Object.entries(taxResults.profit_loss_by_symbol).map(([symbol, profit]) => (
                <div key={symbol} className="flex justify-between text-sm">
                  <span className="text-gray-400">{symbol}:</span>
                  <span className={`${Number(profit) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {Number(profit).toFixed(2)} TL
                  </span>
                </div>
              ))}
            </div>

            <div className="space-y-2 pt-2 border-t border-gray-600">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Toplam Kar:</span>
                <span className="text-green-400">{taxResults.total_profit.toFixed(2)} TL</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Toplam Zarar:</span>
                <span className="text-red-400">{taxResults.total_loss.toFixed(2)} TL</span>
              </div>
              <div className="flex justify-between text-sm font-medium">
                <span className="text-gray-300">Toplam Kar/Zarar:</span>
                <span className={`${taxResults.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {taxResults.total_profit_loss.toFixed(2)} TL
                </span>
              </div>
              <div className="flex justify-between text-sm font-medium pt-2 border-t border-gray-600">
                <span className="text-gray-300">Komisyonlar Sonrası Kar/Zarar:</span>
                <span className={`${taxResults.total_profit_loss_after_commissions >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {taxResults.total_profit_loss_after_commissions.toFixed(2)} TL
                </span>
              </div>
            </div>
          </div>

          {/* Dividend Section */}
          <div className="mt-8 space-y-4 pt-6 border-t border-gray-600">
            <h4 className="text-md font-medium text-gray-300">Temettü Gelirleri:</h4>

            <div className="space-y-2">
              <h5 className="text-sm font-medium text-gray-400">Sembol Bazında Temettüler:</h5>
              {Object.entries(taxResults.dividend_summary.dividends_by_symbol).map(([symbol, amount]) => (
                <div key={symbol} className="flex justify-between text-sm">
                  <span className="text-gray-400">{symbol}:</span>
                  <span className="text-blue-400">{Number(amount).toFixed(2)} TL</span>
                </div>
              ))}
            </div>

            <div className="space-y-2 pt-2 border-t border-gray-600">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Toplam Brüt Temettü:</span>
                <span className="text-blue-400">{taxResults.dividend_summary.total_gross_amount.toFixed(2)} TL</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Stopaj Kesintisi:</span>
                <span className="text-red-400">{taxResults.dividend_summary.total_tax_withheld.toFixed(2)} TL</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Net Temettü:</span>
                <span className="text-blue-400">{taxResults.dividend_summary.total_net_amount.toFixed(2)} TL</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <MissingTransactionsAlert
        symbols={missingSymbols}
        onContinue={() => setShowMissingAlert(false)}
        onUpload={resetUploader}
        open={showMissingAlert}
        onOpenChange={setShowMissingAlert}
      />
    </div>
  );
} 