import React from 'react'
import { DetectionResult } from '@/lib/types'
import { formatTimestamp } from '@/lib/utils'
import { Clock, CheckCircle, XCircle, TrendingUp } from 'lucide-react'

interface DetectionHistoryProps {
  history: DetectionResult[]
  onSelectResult?: (result: DetectionResult) => void
}

export const DetectionHistory: React.FC<DetectionHistoryProps> = ({ 
  history, 
  onSelectResult 
}) => {
  if (history.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <div className="flex items-center space-x-2 mb-4">
          <Clock className="h-5 w-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Riwayat Deteksi</h3>
        </div>
        <div className="text-center py-8">
          <div className="bg-gray-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <Clock className="h-6 w-6 text-gray-400" />
          </div>
          <p className="text-gray-500">Belum ada riwayat deteksi</p>
          <p className="text-sm text-gray-400 mt-1">Mulai deteksi untuk melihat riwayat</p>
        </div>
      </div>
    )
  }

  // Calculate statistics
  const totalDetections = history.length
  const israeliProducts = history.filter(h => h.is_israeli_product).length
  const safeProducts = totalDetections - israeliProducts
  const averageConfidence = history.reduce((sum, h) => sum + h.confidence, 0) / totalDetections

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header with Statistics */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Riwayat Deteksi</h3>
          </div>
          <span className="text-sm text-gray-500">{totalDetections} deteksi</span>
        </div>
        
        {/* Statistics Cards */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white rounded-lg p-3 border">
            <div className="text-xs text-gray-500 mb-1">Total</div>
            <div className="text-lg font-bold text-gray-900">{totalDetections}</div>
          </div>
          <div className="bg-white rounded-lg p-3 border">
            <div className="text-xs text-red-600 mb-1">Israel</div>
            <div className="text-lg font-bold text-red-600">{israeliProducts}</div>
          </div>
          <div className="bg-white rounded-lg p-3 border">
            <div className="text-xs text-green-600 mb-1">Aman</div>
            <div className="text-lg font-bold text-green-600">{safeProducts}</div>
          </div>
        </div>
        
        {/* Average Confidence */}
        <div className="mt-3 p-2 bg-white rounded-lg border">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-500">Rata-rata Confidence</span>
            <span className="text-sm font-medium">{(averageConfidence * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
            <div
              className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${averageConfidence * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* History List */}
      <div className="max-h-96 overflow-y-auto">
        {history.map((result, index) => (
          <div
            key={index}
            className={`p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer ${
              index === history.length - 1 ? 'border-b-0' : ''
            }`}
            onClick={() => onSelectResult?.(result)}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {result.is_israeli_product ? (
                  <XCircle className="h-4 w-4 text-red-500" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                )}
                <span className={`text-sm font-medium ${
                  result.is_israeli_product ? 'text-red-600' : 'text-green-600'
                }`}>
                  {result.is_israeli_product ? 'Produk Israel' : 'Produk Aman'}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                #{totalDetections - index}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-xs text-gray-500">
                  Confidence: {(result.confidence * 100).toFixed(1)}%
                </div>
                {result.brand_info && (
                  <div className="text-xs text-gray-500">
                    Brand: {result.brand_info.name}
                  </div>
                )}
              </div>
              <div className="text-xs text-gray-400">
                {new Date(result.timestamp).toLocaleTimeString('id-ID', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
            
            {/* Feature indicators */}
            <div className="flex items-center space-x-1 mt-2">
              {Object.entries(result.detected_features).map(([key, value]) => (
                value && (
                  <span
                    key={key}
                    className="inline-block w-2 h-2 bg-red-400 rounded-full"
                    title={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  />
                )
              ))}
              {Object.values(result.detected_features).every(v => !v) && (
                <span className="text-xs text-gray-400 italic">No features detected</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DetectionHistory