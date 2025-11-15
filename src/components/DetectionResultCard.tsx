import React from 'react'
import { DetectionResult } from '@/lib/types'
import { formatConfidence, getConfidenceColor, getRiskLevelColor, formatTimestamp } from '@/lib/utils'
import { CheckCircle, XCircle, AlertTriangle, Info, Download } from 'lucide-react'

interface DetectionResultCardProps {
  result: DetectionResult
  onDownload?: () => void
}

export const DetectionResultCard: React.FC<DetectionResultCardProps> = ({ result, onDownload }) => {
  const isIsraeliProduct = result.is_israeli_product
  const confidenceColor = getConfidenceColor(result.confidence)

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className={`p-4 ${isIsraeliProduct ? 'bg-red-50 border-b border-red-100' : 'bg-green-50 border-b border-green-100'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {isIsraeliProduct ? (
              <XCircle className="h-6 w-6 text-red-600" />
            ) : (
              <CheckCircle className="h-6 w-6 text-green-600" />
            )}
            <div>
              <h3 className={`font-semibold ${isIsraeliProduct ? 'text-red-800' : 'text-green-800'}`}>
                {isIsraeliProduct ? 'Produk Terafiliasi Israel' : 'Produk Aman'}
              </h3>
              <p className={`text-sm ${isIsraeliProduct ? 'text-red-600' : 'text-green-600'}`}>
                Confidence: {formatConfidence(result.confidence)}
              </p>
            </div>
          </div>
          {onDownload && (
            <button
              onClick={onDownload}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Download className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Confidence Bar */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Tingkat Keyakinan</span>
            <span className={`text-sm font-semibold ${confidenceColor}`}>
              {formatConfidence(result.confidence)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                result.confidence >= 0.8 ? 'bg-red-500' :
                result.confidence >= 0.6 ? 'bg-orange-500' :
                result.confidence >= 0.4 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${result.confidence * 100}%` }}
            />
          </div>
        </div>

        {/* Detected Features */}
        <div className="mb-4">
          <h4 className="font-medium text-gray-900 mb-3">Fitur yang Terdeteksi</h4>
          <div className="space-y-2">
            {Object.entries(result.detected_features).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between py-1">
                <span className="text-sm text-gray-600 capitalize">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
                <div className="flex items-center space-x-2">
                  {value ? (
                    <>
                      <CheckCircle className="h-4 w-4 text-red-500" />
                      <span className="text-sm font-medium text-red-600">Terdeteksi</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-500">Tidak Ada</span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Brand Info */}
        {result.brand_info && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
              <Info className="h-4 w-4 mr-2" />
              Informasi Brand
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Nama:</span>
                <span className="font-medium">{result.brand_info.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Kategori:</span>
                <span className="font-medium capitalize">{result.brand_info.category.replace(/_/g, ' ')}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Risk Level:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRiskLevelColor(result.brand_info.risk_level)}`}>
                  {result.brand_info.risk_level.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Timestamp */}
        <div className="text-xs text-gray-500 border-t pt-3">
          <div className="flex justify-between items-center">
            <span>Waktu Deteksi: {formatTimestamp(result.timestamp)}</span>
            {result.processing_time_ms && (
              <span>Waktu Proses: {result.processing_time_ms.toFixed(0)}ms</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DetectionResultCard